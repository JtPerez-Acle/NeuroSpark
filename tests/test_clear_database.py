"""Test database clearing functionality."""
import pytest
from app.database.arango.database import ArangoDatabase

class TestClearDatabase:
    """Test database clearing functionality."""

    @pytest.mark.asyncio
    async def test_clear_database(self, test_db_arango):
        """Test that the clear_database method properly removes all data."""
        # Test setup: Add some test data
        agent_data = {
            "id": "test_agent",
            "type": "human",
            "role": "user"
        }
        await test_db_arango.store_agent(agent_data)
        
        # Add another agent
        agent_data2 = {
            "id": "test_agent2",
            "type": "ai",
            "role": "assistant"
        }
        await test_db_arango.store_agent(agent_data2)
        
        # Add an interaction
        interaction_data = {
            "id": "test_interaction",
            "sender_id": "test_agent",
            "receiver_id": "test_agent2",
            "topic": "test_topic",
            "message": "test message",
            "interaction_type": "message",
            "timestamp": "2024-03-20T12:00:00Z"
        }
        await test_db_arango.store_interaction(interaction_data)
        
        # Verify data exists
        agents = await test_db_arango.get_agents()
        interactions = await test_db_arango.get_interactions()
        assert len(agents) == 2, "Expected 2 agents to be stored"
        assert len(interactions) == 1, "Expected 1 interaction to be stored"
        
        # Test the method - clear the database
        result = await test_db_arango.clear_database()
        
        # Verify data was cleared
        agents_after = await test_db_arango.get_agents()
        interactions_after = await test_db_arango.get_interactions()
        
        # Assertions
        assert len(agents_after) == 0, "Expected all agents to be deleted"
        assert len(interactions_after) == 0, "Expected all interactions to be deleted"
        assert "nodes_deleted" in result, "Expected result to contain nodes_deleted count"
        assert "relationships_deleted" in result, "Expected result to contain relationships_deleted count"
        assert result["nodes_deleted"] >= 2, "Expected at least 2 nodes to be deleted"
        assert result["relationships_deleted"] >= 1, "Expected at least 1 relationship to be deleted"