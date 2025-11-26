import asyncio
import sys

from src.application.use_cases.graph_context_retrieval import (
    get_graph_context_retrieval,
)
from src.infrastructure.graph.neo4j_client import get_neo4j_client

sys.path.insert(0, "backend")

"""Test script to verify graph context retrieval is working."""


async def test_graph_context():
    """Test that graph context retrieval works."""
    # Connect to Neo4j
    neo4j_client = get_neo4j_client()
    await neo4j_client.connect()

    # Get graph context retrieval use case
    graph_retrieval = get_graph_context_retrieval()

    # Test query
    user_id = "2302f1b9-400a-422b-9a73-da3321126f37"
    query = "de que hemos hablado antes"

    print(f"\nTesting graph context retrieval for user: {user_id}")
    print(f"Query: {query}\n")

    # Get context
    context = await graph_retrieval.get_context_for_query(
        user_id=user_id,
        query=query,
        max_topics=5,
        max_concepts=5,
    )

    print(f"Topics found: {len(context.topics)}")
    for topic in context.topics:
        print(f"  - {topic['name']} (mentioned {topic['mention_count']}x)")

    print(f"\nConcepts found: {len(context.concepts)}")
    for concept in context.concepts:
        print(f"  - {concept['name']} ({concept['category']})")

    print(f"\nRelated topics: {len(context.related_topics)}")
    for topic in context.related_topics:
        print(
            f"  - {topic['name']} (mentioned {topic['mention_count']}x, "
            f"{topic['shared_concepts']} shared concepts)"
        )

    print("\n--- Formatted Context ---")
    print(context.formatted_context)
    print("--- End Context ---\n")

    # Close connection
    await neo4j_client.close()


if __name__ == "__main__":
    asyncio.run(test_graph_context())
