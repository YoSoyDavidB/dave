"""Vault indexing use case - indexes Obsidian vault for RAG."""

import hashlib
from datetime import datetime
from typing import Any

import structlog

from src.infrastructure.github_vault import get_github_vault_client
from src.infrastructure.vector_store.document_repository import get_document_repository

logger = structlog.get_logger()

# Folders to exclude from indexing
EXCLUDED_FOLDERS = {
    ".obsidian",
    ".git",
    ".trash",
    "Extras/Templates",  # Don't index templates
    "Archive",  # Optional: exclude archived content
}

# File extensions to index
INDEXABLE_EXTENSIONS = {".md"}


def should_index_path(path: str) -> bool:
    """Check if a path should be indexed.

    Args:
        path: File path in vault

    Returns:
        True if should be indexed
    """
    # Check extension
    if not any(path.endswith(ext) for ext in INDEXABLE_EXTENSIONS):
        return False

    # Check excluded folders
    for excluded in EXCLUDED_FOLDERS:
        if path.startswith(excluded) or f"/{excluded}/" in path:
            return False

    return True


def compute_content_hash(content: str) -> str:
    """Compute hash of content for change detection.

    Args:
        content: Document content

    Returns:
        SHA256 hash (first 16 chars)
    """
    return hashlib.sha256(content.encode()).hexdigest()[:16]


class VaultIndexingUseCase:
    """Indexes the Obsidian vault for semantic search."""

    def __init__(self):
        self._vault = get_github_vault_client()
        self._doc_repo = get_document_repository()
        self._indexed_hashes: dict[str, str] = {}  # path -> content_hash

    async def full_sync(self) -> dict[str, Any]:
        """Perform a full vault sync.

        Returns:
            Stats about indexed documents
        """
        stats = {
            "total_files": 0,
            "indexed": 0,
            "skipped": 0,
            "errors": 0,
            "chunks_created": 0,
        }

        logger.info("vault_sync_started")

        try:
            # Get all files recursively
            files = await self._get_all_files("")

            stats["total_files"] = len(files)

            for file_info in files:
                path = file_info["path"]

                if not should_index_path(path):
                    stats["skipped"] += 1
                    continue

                try:
                    # Get file content
                    file_data = await self._vault.get_file(path)

                    if file_data is None:
                        stats["errors"] += 1
                        continue

                    content = file_data.get("content", "")

                    if not content.strip():
                        stats["skipped"] += 1
                        continue

                    # Index the document
                    chunks = await self._doc_repo.index_document(
                        path=path,
                        content=content,
                        last_modified=datetime.utcnow(),
                    )

                    stats["indexed"] += 1
                    stats["chunks_created"] += chunks

                    # Store hash for incremental sync
                    self._indexed_hashes[path] = compute_content_hash(content)

                except Exception as e:
                    logger.error("file_indexing_error", path=path, error=str(e))
                    stats["errors"] += 1

            logger.info(
                "vault_sync_completed",
                indexed=stats["indexed"],
                chunks=stats["chunks_created"],
                errors=stats["errors"],
            )

        except Exception as e:
            logger.error("vault_sync_failed", error=str(e))
            raise

        return stats

    async def incremental_sync(self) -> dict[str, Any]:
        """Sync only changed files.

        Returns:
            Stats about indexed documents
        """
        stats = {
            "checked": 0,
            "updated": 0,
            "added": 0,
            "deleted": 0,
            "unchanged": 0,
            "errors": 0,
        }

        logger.info("incremental_sync_started")

        try:
            # Get current files
            current_files = await self._get_all_files("")
            current_paths = {f["path"] for f in current_files if should_index_path(f["path"])}

            # Get indexed paths
            indexed_paths = set(await self._doc_repo.get_indexed_paths())

            # Find deleted files
            deleted = indexed_paths - current_paths
            for path in deleted:
                await self._doc_repo.delete_by_path(path)
                self._indexed_hashes.pop(path, None)
                stats["deleted"] += 1

            # Check each current file
            for file_info in current_files:
                path = file_info["path"]
                stats["checked"] += 1

                if not should_index_path(path):
                    continue

                try:
                    # Get file content
                    file_data = await self._vault.get_file(path)

                    if file_data is None:
                        continue

                    content = file_data.get("content", "")

                    if not content.strip():
                        continue

                    # Check if content changed
                    content_hash = compute_content_hash(content)
                    old_hash = self._indexed_hashes.get(path)

                    if old_hash == content_hash:
                        stats["unchanged"] += 1
                        continue

                    # Index the document
                    await self._doc_repo.index_document(
                        path=path,
                        content=content,
                        last_modified=datetime.utcnow(),
                    )

                    self._indexed_hashes[path] = content_hash

                    if path in indexed_paths:
                        stats["updated"] += 1
                    else:
                        stats["added"] += 1

                except Exception as e:
                    logger.error("incremental_sync_error", path=path, error=str(e))
                    stats["errors"] += 1

            logger.info(
                "incremental_sync_completed",
                added=stats["added"],
                updated=stats["updated"],
                deleted=stats["deleted"],
            )

        except Exception as e:
            logger.error("incremental_sync_failed", error=str(e))
            raise

        return stats

    async def index_single_document(self, path: str) -> int:
        """Index a single document.

        Args:
            path: Document path

        Returns:
            Number of chunks created
        """
        if not should_index_path(path):
            return 0

        file_data = await self._vault.get_file(path)

        if file_data is None:
            return 0

        content = file_data.get("content", "")

        if not content.strip():
            return 0

        chunks = await self._doc_repo.index_document(
            path=path,
            content=content,
            last_modified=datetime.utcnow(),
        )

        self._indexed_hashes[path] = compute_content_hash(content)

        logger.info("single_document_indexed", path=path, chunks=chunks)

        return chunks

    async def _get_all_files(self, path: str) -> list[dict[str, Any]]:
        """Recursively get all files from vault.

        Args:
            path: Starting path

        Returns:
            List of file info dicts
        """
        files = []

        items = await self._vault.list_directory(path)

        for item in items:
            if item["type"] == "file":
                files.append(item)
            elif item["type"] == "dir":
                # Skip excluded folders
                item_path = item.get("path", item.get("name", ""))
                if not any(excl in item_path for excl in EXCLUDED_FOLDERS):
                    sub_files = await self._get_all_files(item_path)
                    files.extend(sub_files)

        return files

    async def get_stats(self) -> dict[str, Any]:
        """Get indexing statistics.

        Returns:
            Index stats
        """
        counts = await self._doc_repo.count_documents()
        return {
            "documents_indexed": counts["documents"],
            "total_chunks": counts["chunks"],
            "cached_hashes": len(self._indexed_hashes),
        }


# Singleton instance
_vault_indexing: VaultIndexingUseCase | None = None


def get_vault_indexing_use_case() -> VaultIndexingUseCase:
    """Get the singleton vault indexing use case."""
    global _vault_indexing
    if _vault_indexing is None:
        _vault_indexing = VaultIndexingUseCase()
    return _vault_indexing
