"""Test database operations."""
import pytest
from app.database.arango.database import ArangoDatabase

class TestDatabaseConnection:
    """Test database connection and operations."""

    @pytest.mark.asyncio
    async def test_database_connection(self, test_db_arango):
        """Test database connection."""
        assert test_db_arango.is_connected()
        await test_db_arango.disconnect()
        assert not test_db_arango.is_connected()
        # Reconnect for other tests
        await test_db_arango.connect()

    @pytest.mark.asyncio
    async def test_database_operations(self, test_db_arango):
        """Test database operations."""
        try:
            # Test storing and retrieving an agent
            agent_data = {
                "id": "test_agent",
                "type": "human",
                "role": "user"
            }
            await test_db_arango.store_agent(agent_data)
            
            agents = await test_db_arango.get_agents()
            assert len(agents) > 0
            agent = await test_db_arango.get_agent("test_agent")
            assert agent["id"] == "test_agent"
            assert agent["type"] == "human"
            assert agent["role"] == "user"

            # Test storing and retrieving an interaction
            interaction_data = {
                "id": "test_interaction",
                "sender_id": "test_agent",
                "receiver_id": "test_agent_2",
                "topic": "test_topic",
                "message": "test message",
                "interaction_type": "message",
                "timestamp": "2024-03-20T12:00:00Z"
            }
            await test_db_arango.store_interaction(interaction_data)

            # Test retrieving interactions
            interactions = await test_db_arango.get_interactions()
            assert len(interactions) > 0
            interaction = await test_db_arango.get_interaction("test_interaction")
            assert interaction is not None
            assert interaction["sender_id"] == "test_agent"
            assert interaction["receiver_id"] == "test_agent_2"

            # Test retrieving network data
            network = await test_db_arango.get_network()
            assert "nodes" in network
            assert "edges" in network
            assert isinstance(network["nodes"], list)
            assert isinstance(network["edges"], list)

            # Test getting agent interactions
            agent_interactions = await test_db_arango.get_agent_interactions("test_agent")
            assert len(agent_interactions) > 0
            assert agent_interactions[0]["sender_id"] == "test_agent"

        finally:
            # Clean up test data
            await test_db_arango.clear_database()
