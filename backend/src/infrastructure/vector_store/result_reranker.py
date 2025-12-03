"""Result reranking utilities for RAG."""

import re
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Protocol

# Stop words to ignore in keyword matching
STOP_WORDS = {
    "a",
    "an",
    "the",
    "and",
    "or",
    "but",
    "in",
    "on",
    "at",
    "to",
    "for",
    "of",
    "with",
    "by",
    "from",
    "as",
    "is",
    "was",
    "are",
    "were",
    "been",
    "be",
    "have",
    "has",
    "had",
    "do",
    "does",
    "did",
    "will",
    "would",
    "could",
    "should",
    "may",
    "might",
    "must",
    "shall",
    "can",
    "need",
    "it",
    "its",
    "this",
    "that",
    "these",
    "those",
    "i",
    "you",
    "he",
    "she",
    "we",
    "they",
    "what",
    "which",
    "who",
    "whom",
    "how",
    "when",
    "where",
    "why",
    "all",
    "each",
    "every",
    "both",
    "few",
    "more",
    "most",
    "other",
    "some",
    "such",
    "no",
    "nor",
    "not",
    "only",
    "own",
    "same",
    "so",
    "than",
    "too",
    "very",
    "just",
    "about",
    "into",
    "through",
    "during",
    "before",
    "after",
    "above",
    "below",
    "between",
    "under",
}


class Scoreable(Protocol):
    """Protocol for items that can be scored."""

    score: float
    content: str


@dataclass
class RerankedResult:
    """A reranked search result."""

    original_item: Any
    original_score: float
    final_score: float
    boost_factors: dict[str, float]


def extract_keywords(text: str) -> set[str]:
    """Extract meaningful keywords from text.

    Args:
        text: Input text

    Returns:
        Set of lowercase keywords
    """
    # Tokenize and lowercase
    words = re.findall(r"\b\w+\b", text.lower())

    # Filter stop words and short words
    keywords = {w for w in words if w not in STOP_WORDS and len(w) > 2}

    return keywords


def keyword_match_score(query_keywords: set[str], content: str) -> float:
    """Calculate keyword match score.

    Args:
        query_keywords: Keywords from query
        content: Content to match against

    Returns:
        Match score (0-1)
    """
    if not query_keywords:
        return 0.0

    content_lower = content.lower()
    matches = sum(1 for kw in query_keywords if kw in content_lower)

    return matches / len(query_keywords)


def recency_score(timestamp: datetime, max_age_days: int = 365) -> float:
    """Calculate recency score based on timestamp.

    Args:
        timestamp: Item timestamp
        max_age_days: Maximum age to consider

    Returns:
        Recency score (0-1, 1 being most recent)
    """
    now = datetime.now(UTC)
    age = (now - timestamp).days

    if age <= 0:
        return 1.0
    if age >= max_age_days:
        return 0.0

    # Linear decay
    return 1.0 - (age / max_age_days)


def mmr_rerank(
    results: list[tuple[Any, float, str]],
    query_embedding: list[float] | None = None,
    lambda_param: float = 0.7,
    top_k: int = 5,
) -> list[tuple[Any, float]]:
    """Maximal Marginal Relevance reranking.

    Balances relevance with diversity to avoid redundant results.

    Args:
        results: List of (item, score, content) tuples
        query_embedding: Query embedding (not used in simple version)
        lambda_param: Trade-off between relevance (1.0) and diversity (0.0)
        top_k: Number of results to return

    Returns:
        Reranked list of (item, score) tuples
    """
    if not results:
        return []

    if len(results) <= top_k:
        return [(item, score) for item, score, _ in results]

    selected = []
    remaining = list(results)

    while len(selected) < top_k and remaining:
        best_idx = 0
        best_mmr_score = float("-inf")

        for i, (item, score, content) in enumerate(remaining):
            # Relevance component
            relevance = score

            # Diversity component (simplified: penalize similarity to selected)
            if selected:
                max_sim = 0.0
                for sel_item, sel_score, sel_content in selected:
                    # Simple text overlap as proxy for similarity
                    sel_words = set(sel_content.lower().split())
                    cur_words = set(content.lower().split())
                    if sel_words and cur_words:
                        overlap = len(sel_words & cur_words) / max(len(sel_words), len(cur_words))
                        max_sim = max(max_sim, overlap)
                diversity = 1.0 - max_sim
            else:
                diversity = 1.0

            # MMR score
            mmr_score = lambda_param * relevance + (1 - lambda_param) * diversity

            if mmr_score > best_mmr_score:
                best_mmr_score = mmr_score
                best_idx = i

        # Add best item to selected
        item, score, content = remaining.pop(best_idx)
        selected.append((item, score, content))

    return [(item, score) for item, score, _ in selected]


class ResultReranker:
    """Reranks search results using various strategies."""

    def __init__(self):
        self._strategies = {
            "keyword": self._keyword_boost,
            "recency": self._recency_boost,
            "hybrid": self._hybrid_boost,
            "mmr": self._mmr_rerank,
        }

    def rerank(
        self,
        results: list[Any],
        query: str,
        strategy: str = "hybrid",
        top_k: int = 5,
        **kwargs,
    ) -> list[RerankedResult]:
        """Rerank results using specified strategy.

        Args:
            results: Search results (must have 'score' and 'content' attributes)
            query: Original search query
            strategy: Reranking strategy ("keyword", "recency", "hybrid", "mmr")
            top_k: Number of results to return
            **kwargs: Strategy-specific parameters

        Returns:
            Reranked results with scores
        """
        if not results:
            return []

        if strategy not in self._strategies:
            raise ValueError(f"Unknown strategy: {strategy}")

        reranked = self._strategies[strategy](results, query, **kwargs)

        # Sort by final score and limit
        reranked.sort(key=lambda r: r.final_score, reverse=True)

        return reranked[:top_k]

    def _keyword_boost(
        self,
        results: list[Any],
        query: str,
        keyword_weight: float = 0.3,
        **kwargs,
    ) -> list[RerankedResult]:
        """Boost results with keyword matches."""
        query_keywords = extract_keywords(query)
        reranked = []

        for result in results:
            content = getattr(result, "content", str(result))
            original_score = getattr(result, "score", 0.5)

            kw_score = keyword_match_score(query_keywords, content)
            boost = kw_score * keyword_weight

            reranked.append(
                RerankedResult(
                    original_item=result,
                    original_score=original_score,
                    final_score=original_score + boost,
                    boost_factors={"keyword": boost},
                )
            )

        return reranked

    def _recency_boost(
        self,
        results: list[Any],
        query: str,
        recency_weight: float = 0.2,
        max_age_days: int = 365,
        **kwargs,
    ) -> list[RerankedResult]:
        """Boost recent results."""
        reranked = []

        for result in results:
            original_score = getattr(result, "score", 0.5)

            # Try to get timestamp
            timestamp = getattr(result, "last_modified", None)
            if timestamp is None:
                timestamp = getattr(result, "timestamp", datetime.now(UTC))

            rec_score = recency_score(timestamp, max_age_days)
            boost = rec_score * recency_weight

            reranked.append(
                RerankedResult(
                    original_item=result,
                    original_score=original_score,
                    final_score=original_score + boost,
                    boost_factors={"recency": boost},
                )
            )

        return reranked

    def _hybrid_boost(
        self,
        results: list[Any],
        query: str,
        keyword_weight: float = 0.3,
        recency_weight: float = 0.1,
        max_age_days: int = 365,
        **kwargs,
    ) -> list[RerankedResult]:
        """Combine keyword and recency boosts."""
        query_keywords = extract_keywords(query)
        reranked = []

        for result in results:
            content = getattr(result, "content", str(result))
            original_score = getattr(result, "score", 0.5)

            # Keyword boost
            kw_score = keyword_match_score(query_keywords, content)
            kw_boost = kw_score * keyword_weight

            # Recency boost
            timestamp = getattr(result, "last_modified", None)
            if timestamp is None:
                timestamp = getattr(result, "timestamp", datetime.now(UTC))

            rec_score = recency_score(timestamp, max_age_days)
            rec_boost = rec_score * recency_weight

            reranked.append(
                RerankedResult(
                    original_item=result,
                    original_score=original_score,
                    final_score=original_score + kw_boost + rec_boost,
                    boost_factors={"keyword": kw_boost, "recency": rec_boost},
                )
            )

        return reranked

    def _mmr_rerank(
        self,
        results: list[Any],
        query: str,
        lambda_param: float = 0.7,
        **kwargs,
    ) -> list[RerankedResult]:
        """MMR reranking for diversity."""
        # Prepare data for MMR
        mmr_input = [
            (result, getattr(result, "score", 0.5), getattr(result, "content", str(result)))
            for result in results
        ]

        # Run MMR
        mmr_results = mmr_rerank(mmr_input, lambda_param=lambda_param, top_k=len(results))

        # Convert back to RerankedResult
        reranked = []
        for i, (item, score) in enumerate(mmr_results):
            # MMR doesn't boost, it reorders
            reranked.append(
                RerankedResult(
                    original_item=item,
                    original_score=score,
                    final_score=score * (1.0 - i * 0.01),  # Small penalty for rank
                    boost_factors={"mmr_rank": i},
                )
            )

        return reranked


# Singleton instance
_reranker: ResultReranker | None = None


def get_result_reranker() -> ResultReranker:
    """Get the singleton result reranker."""
    global _reranker
    if _reranker is None:
        _reranker = ResultReranker()
    return _reranker
