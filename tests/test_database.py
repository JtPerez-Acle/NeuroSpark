"""Database tests module."""
import pytest
import os
from datetime import datetime, timezone

from app.database import Neo4jDatabase, InMemoryDatabase

@pytest.mark.asyncio
class TestDatabaseConnection:
    """Test database connection and operations."""

    async def test_database_connection(self):
        """Test database connection."""
        # Try to connect to Neo4j
        try:
            db = Neo4jDatabase(
                uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
                username=os.getenv("NEO4J_USER", "neo4j"),
                password=os.getenv("NEO4J_PASSWORD", "neo4j")
            )
            await db.connect()
            
            # Clean up test data
            async with await db._get_session() as session:
                await session.run("MATCH (n) DETACH DELETE n")
            
            await db.disconnect()
        except Exception as e:
            pytest.skip(f"Neo4j database not available: {str(e)}")

    async def test_database_operations(self):
        """Test database operations."""
        # Use in-memory database for testing
        db = InMemoryDatabase()
        await db.connect()

        try:
            # Test storing interaction
            interaction = {
                "message_id": "test_id",
                "id": "test_id",
                "sender": "agent1",
                "receiver": "agent2",
                "content": "test content",
                "performative": "tell",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "run_id": "test_run"
            }
            await db.store_interaction(interaction)

            # Test retrieving agent runs
            runs = await db.get_agent_runs("agent1")
            assert len(runs) > 0
            assert runs[0]["id"] == "test_run"

            # Test retrieving agent interactions
            interactions = await db.get_agent_interactions("agent1")
            assert len(interactions) > 0
            assert interactions[0]["id"] == "test_id"
            assert interactions[0]["sender"] == "agent1"
            assert interactions[0]["receiver"] == "agent2"

        finally:
            await db.disconnect()
