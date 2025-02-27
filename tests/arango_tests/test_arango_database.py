"""Test ArangoDB database operations."""
import os
import pytest
import pytest_asyncio
from uuid import uuid4
from datetime import datetime, timezone

from app.database.arango.database import ArangoDatabase

# Test configuration
TEST_HOST = os.environ.get("TEST_ARANGO_HOST", "localhost")
TEST_PORT = int(os.environ.get("TEST_ARANGO_PORT", "8529"))
TEST_USER = os.environ.get("TEST_ARANGO_USER", "root")
TEST_PASSWORD = os.environ.get("TEST_ARANGO_PASSWORD", "password")
TEST_DB = f"test_db_{uuid4().hex[:8]}"  # Unique test database

@pytest_asyncio.fixture
async def test_db():
    """Test database fixture with improved error handling."""
    import asyncio
    import logging
    from urllib3.exceptions import NewConnectionError, MaxRetryError
    from arango.exceptions import ServerConnectionError, DatabaseCreateError
    
    # Reduce connection warnings during tests
    logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)
    
    db = ArangoDatabase(
        host=TEST_HOST,
        port=TEST_PORT,
        username=TEST_USER,
        password=TEST_PASSWORD,
        db_name=TEST_DB
    )
    
    # Connect with retry logic
    max_retries = 5
    retry_count = 0
    connected = False
    
    while retry_count < max_retries and not connected:
        try:
            await db.connect()
            connected = True
        except (ServerConnectionError, ConnectionError, NewConnectionError, MaxRetryError) as e:
            retry_count += 1
            if retry_count >= max_retries:
                raise
            wait_time = 2 * retry_count  # Exponential backoff
            print(f"Connection attempt {retry_count} failed: {str(e)}. Waiting {wait_time}s...")
            await asyncio.sleep(wait_time)
    
    yield db
    
    try:
        # Clean up
        await db.clear_database()
        await db.disconnect()
        
        # Delete test database
        if db._db:
            try:
                sys_db = db._connection.client.db("_system", username=TEST_USER, password=TEST_PASSWORD)
                if sys_db.has_database(TEST_DB):
                    sys_db.delete_database(TEST_DB)
                    print(f"Test database '{TEST_DB}' deleted")
            except Exception as e:
                print(f"Error deleting test database: {str(e)}")
    except Exception as e:
        print(f"Error during test cleanup: {str(e)}")

class TestArangoDatabase:
    """Test ArangoDB database operations."""
    
    @pytest.mark.asyncio
    async def test_connection(self, test_db):
        """Test database connection."""
        assert test_db.is_connected()
        await test_db.disconnect()
        assert not test_db.is_connected()
        await test_db.connect()
        assert test_db.is_connected()
    
    @pytest.mark.asyncio
    async def test_store_and_get_agent(self, test_db):
        """Test storing and retrieving an agent."""
        # Create test agent
        agent_id = f"test_agent_{uuid4().hex[:8]}"
        agent_data = {
            "id": agent_id,
            "type": "human",
            "role": "user",
            "metadata": {"test": True},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Store agent
        await test_db.store_agent(agent_data)
        
        # Retrieve all agents
        agents = await test_db.get_agents()
        assert len(agents) == 1
        assert agents[0]["id"] == agent_id
        
        # Retrieve specific agent
        agent = await test_db.get_agent(agent_id)
        assert agent is not None
        assert agent["id"] == agent_id
        assert agent["type"] == "human"
        assert agent["role"] == "user"
        assert agent["metadata"]["test"] is True
    
    @pytest.mark.asyncio
    async def test_store_and_get_interaction(self, test_db):
        """Test storing and retrieving an interaction."""
        # Create test agents
        sender_id = f"sender_{uuid4().hex[:8]}"
        sender_data = {
            "id": sender_id,
            "type": "human",
            "role": "user"
        }
        
        receiver_id = f"receiver_{uuid4().hex[:8]}"
        receiver_data = {
            "id": receiver_id,
            "type": "ai",
            "role": "assistant"
        }
        
        # Store agents
        await test_db.store_agent(sender_data)
        await test_db.store_agent(receiver_data)
        
        # Create interaction
        interaction_id = f"interaction_{uuid4().hex[:8]}"
        interaction_data = {
            "id": interaction_id,
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "topic": "test_topic",
            "message": "Hello, this is a test",
            "interaction_type": "message",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "priority": 3,
            "sentiment": 0.7
        }
        
        # Store interaction
        await test_db.store_interaction(interaction_data)
        
        # Retrieve all interactions
        interactions = await test_db.get_interactions()
        assert len(interactions) == 1
        assert interactions[0]["id"] == interaction_id
        
        # Retrieve specific interaction
        interaction = await test_db.get_interaction(interaction_id)
        assert interaction is not None
        assert interaction["id"] == interaction_id
        assert interaction["sender_id"] == sender_id
        assert interaction["receiver_id"] == receiver_id
        assert interaction["topic"] == "test_topic"
        assert interaction["message"] == "Hello, this is a test"
        assert interaction["interaction_type"] == "message"
        assert interaction["priority"] == 3
        assert interaction["sentiment"] == 0.7
    
    @pytest.mark.asyncio
    async def test_get_agent_interactions(self, test_db):
        """Test retrieving interactions for a specific agent."""
        # Create test agents
        agent1_id = f"agent1_{uuid4().hex[:8]}"
        agent1_data = {"id": agent1_id, "type": "human", "role": "user"}
        
        agent2_id = f"agent2_{uuid4().hex[:8]}"
        agent2_data = {"id": agent2_id, "type": "ai", "role": "assistant"}
        
        # Store agents
        await test_db.store_agent(agent1_data)
        await test_db.store_agent(agent2_data)
        
        # Create interactions
        interaction1_data = {
            "id": f"interaction1_{uuid4().hex[:8]}",
            "sender_id": agent1_id,
            "receiver_id": agent2_id,
            "topic": "topic1",
            "message": "Message 1",
            "interaction_type": "message",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        interaction2_data = {
            "id": f"interaction2_{uuid4().hex[:8]}",
            "sender_id": agent2_id,
            "receiver_id": agent1_id,
            "topic": "topic2",
            "message": "Message 2",
            "interaction_type": "response",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Store interactions
        await test_db.store_interaction(interaction1_data)
        await test_db.store_interaction(interaction2_data)
        
        # Get agent1's interactions
        agent1_interactions = await test_db.get_agent_interactions(agent1_id)
        assert len(agent1_interactions) == 2
        
        # Get agent2's interactions
        agent2_interactions = await test_db.get_agent_interactions(agent2_id)
        assert len(agent2_interactions) == 2
    
    @pytest.mark.asyncio
    async def test_clear_database(self, test_db):
        """Test clearing the database."""
        # Add test data
        agent_data = {"id": "test_agent", "type": "human", "role": "user"}
        await test_db.store_agent(agent_data)
        
        interaction_data = {
            "id": "test_interaction",
            "sender_id": "test_agent",
            "receiver_id": "test_agent",  # self-interaction for simplicity
            "topic": "test",
            "message": "Test message",
            "interaction_type": "message",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        await test_db.store_interaction(interaction_data)
        
        # Verify data exists
        agents = await test_db.get_agents()
        interactions = await test_db.get_interactions()
        assert len(agents) > 0
        assert len(interactions) > 0
        
        # Clear database
        result = await test_db.clear_database()
        
        # Verify data was cleared
        agents_after = await test_db.get_agents()
        interactions_after = await test_db.get_interactions()
        assert len(agents_after) == 0
        assert len(interactions_after) == 0
        
        # Check result
        assert "success" in result
        assert result["success"] is True
        assert "nodes_deleted" in result
        assert "relationships_deleted" in result