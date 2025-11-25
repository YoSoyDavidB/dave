"""Neo4j graph database client for knowledge graph operations."""

from typing import Any

import structlog
from neo4j import AsyncDriver, AsyncGraphDatabase
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config import get_settings

logger = structlog.get_logger()


class Neo4jClient:
    """Client for interacting with Neo4j graph database.

    This client manages connections to Neo4j and provides methods for
    creating and querying the knowledge graph of user memories, preferences,
    and conversation topics.
    """

    def __init__(self) -> None:
        """Initialize Neo4j client."""
        self.settings = get_settings()
        self.driver: AsyncDriver | None = None
        self._initialized = False

    async def connect(self) -> None:
        """Establish connection to Neo4j database."""
        if self._initialized:
            return

        try:
            self.driver = AsyncGraphDatabase.driver(
                self.settings.neo4j_url,
                auth=(self.settings.neo4j_user, self.settings.neo4j_password),
            )

            # Test connection
            await self.driver.verify_connectivity()

            self._initialized = True
            logger.info(
                "neo4j_connected",
                url=self.settings.neo4j_url,
                user=self.settings.neo4j_user,
            )
        except Exception as e:
            logger.error("neo4j_connection_failed", error=str(e))
            # Don't fail startup - Neo4j features will be unavailable
            self._initialized = False

    async def close(self) -> None:
        """Close Neo4j connection."""
        if self.driver:
            await self.driver.close()
            self._initialized = False
            logger.info("neo4j_disconnected")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
    )
    async def execute_query(
        self,
        query: str,
        parameters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Execute a Cypher query and return results.

        Args:
            query: Cypher query string
            parameters: Query parameters

        Returns:
            List of result records as dictionaries
        """
        if not self._initialized or not self.driver:
            logger.warning("neo4j_not_initialized")
            return []

        try:
            async with self.driver.session() as session:
                result = await session.run(query, parameters or {})
                records = await result.data()
                return records
        except Exception as e:
            logger.error("neo4j_query_failed", query=query, error=str(e))
            raise

    async def execute_write(
        self,
        query: str,
        parameters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Execute a write query (CREATE, MERGE, UPDATE, DELETE).

        Args:
            query: Cypher query string
            parameters: Query parameters

        Returns:
            List of result records as dictionaries
        """
        if not self._initialized or not self.driver:
            logger.warning("neo4j_not_initialized")
            return []

        try:
            async with self.driver.session() as session:

                async def _execute_write(tx):
                    result = await tx.run(query, parameters or {})
                    records = await result.data()
                    return records

                records = await session.execute_write(_execute_write)
                return records
        except Exception as e:
            logger.error("neo4j_write_failed", query=query, error=str(e))
            raise

    async def initialize_schema(self) -> None:
        """Initialize Neo4j schema with constraints and indexes.

        Creates:
        - Unique constraints on node IDs
        - Indexes for common queries
        """
        if not self._initialized:
            logger.warning("neo4j_not_initialized_skipping_schema")
            return

        constraints = [
            # Unique constraint on Memory.memory_id
            """
            CREATE CONSTRAINT memory_id_unique IF NOT EXISTS
            FOR (m:Memory) REQUIRE m.memory_id IS UNIQUE
            """,
            # Unique constraint on Topic.name per user
            """
            CREATE CONSTRAINT topic_name_unique IF NOT EXISTS
            FOR (t:Topic) REQUIRE (t.user_id, t.name) IS UNIQUE
            """,
            # Unique constraint on Concept.name
            """
            CREATE CONSTRAINT concept_name_unique IF NOT EXISTS
            FOR (c:Concept) REQUIRE c.name IS UNIQUE
            """,
        ]

        indexes = [
            # Index on Memory.user_id for user-specific queries
            """
            CREATE INDEX memory_user_id IF NOT EXISTS
            FOR (m:Memory) ON (m.user_id)
            """,
            # Index on Memory.memory_type for type filtering
            """
            CREATE INDEX memory_type IF NOT EXISTS
            FOR (m:Memory) ON (m.memory_type)
            """,
            # Index on Topic.user_id
            """
            CREATE INDEX topic_user_id IF NOT EXISTS
            FOR (t:Topic) ON (t.user_id)
            """,
            # Index on Memory.timestamp for temporal queries
            """
            CREATE INDEX memory_timestamp IF NOT EXISTS
            FOR (m:Memory) ON (m.timestamp)
            """,
        ]

        try:
            for constraint in constraints:
                await self.execute_write(constraint)

            for index in indexes:
                await self.execute_write(index)

            logger.info("neo4j_schema_initialized")
        except Exception as e:
            logger.error("neo4j_schema_init_failed", error=str(e))
            # Don't fail - the database might already have these


# Global instance
_neo4j_client: Neo4jClient | None = None


def get_neo4j_client() -> Neo4jClient:
    """Get the global Neo4j client instance.

    Returns:
        Neo4j client instance
    """
    global _neo4j_client
    if _neo4j_client is None:
        _neo4j_client = Neo4jClient()
    return _neo4j_client
