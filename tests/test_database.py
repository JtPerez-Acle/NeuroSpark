"""Test database operations."""
import pytest
from app.database.core.database import Neo4jDatabase

class TestDatabaseConnection:
    """Test database connection and operations."""

    @pytest.mark.asyncio
    async def test_database_connection(self, test_db_neo4j):
        """Test database connection."""
        assert test_db_neo4j.is_connected()
        await test_db_neo4j.disconnect()
        assert not test_db_neo4j.is_connected()

    @pytest.mark.asyncio
    async def test_database_operations(self, test_db_neo4j):
        """Test database operations."""
        try:
            # Test storing and retrieving an agent
            agent_data = {
                "id": "test_agent",
                "type": "human",
                "role": "user"
            }
            await test_db_neo4j.store_agent(agent_data)
            
            agents = await test_db_neo4j.get_agents()
            assert len(agents) > 0
            agent = agents[0]
            assert agent["id"] == "test_agent"
            assert agent["type"] == "human"
            assert agent["role"] == "user"

            # Test storing and retrieving an interaction
            interaction_data = {
                "source_id": "test_agent",
                "target_id": "test_agent_2",
                "performative": "tell",
                "content": {"message": "test"},
                "timestamp": "2024-03-20T12:00:00Z"
            }
            await test_db_neo4j.store_interaction(interaction_data)

            # Test retrieving interactions
            interactions = await test_db_neo4j.get_interactions()
            assert len(interactions) > 0
            assert interactions[0]["source_id"] == "test_agent"
            assert interactions[0]["target_id"] == "test_agent_2"

            # Test retrieving network data
            network = await test_db_neo4j.get_network()
            assert "nodes" in network
            assert "edges" in network
            assert isinstance(network["nodes"], list)
            assert isinstance(network["edges"], list)

        finally:
            # Clean up test data
            async with await test_db_neo4j.get_session() as session:
                await session.run("MATCH (n) DETACH DELETE n")
