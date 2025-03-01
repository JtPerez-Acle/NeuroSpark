"""Test main application endpoints."""
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
import pytest_asyncio
from app.main import app
from datetime import datetime

@pytest_asyncio.fixture
async def async_client(test_app):
    """Create an async test client."""
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://localhost:8000") as client:
        yield client

@pytest.mark.asyncio
async def test_root(async_client):
    """Test root endpoint."""
    response = await async_client.get("/")
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["message"] == "NeuroSpark: AI-Powered Blockchain Intelligence API"
    assert "version" in response_data
    assert "capabilities" in response_data
    assert isinstance(response_data["capabilities"], list)

@pytest.mark.asyncio
async def test_agent_message(async_client):
    """Test agent messaging endpoint."""
    # First create an agent
    agent_data = {
        "id": "test_agent",
        "type": "human",
        "role": "user"
    }
    response = await async_client.post("/agents", json=agent_data)
    assert response.status_code == 200

    # Then send a message
    message_data = {
        "sender_id": "test_agent",
        "receiver_id": "test_agent_2",
        "topic": "test_topic",
        "message": "Test message content",
        "interaction_type": "message"
    }
    response = await async_client.post("/agents/message", json=message_data)
    assert response.status_code == 200
    data = response.json()
    assert "interaction_id" in data
    assert data["status"] == "success"

@pytest.mark.asyncio
async def test_agent_runs(async_client):
    """Test agent runs endpoint."""
    # First create an agent
    agent_data = {
        "id": "test_agent",
        "type": "human",
        "role": "user"
    }
    response = await async_client.post("/agents", json=agent_data)
    assert response.status_code == 200
    
    # Then get runs
    response = await async_client.get("/agents/test_agent/runs")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

@pytest.mark.asyncio
async def test_agent_interactions(async_client):
    """Test agent interactions endpoint."""
    # First create an agent
    agent_data = {
        "id": "test_agent",
        "type": "human",
        "role": "user"
    }
    response = await async_client.post("/agents", json=agent_data)
    assert response.status_code == 200
    
    # Then send a message
    message_data = {
        "sender_id": "test_agent",
        "receiver_id": "test_agent_2",
        "topic": "test_topic",
        "message": "Test message content",
        "interaction_type": "message"
    }
    response = await async_client.post("/agents/message", json=message_data)
    assert response.status_code == 200
    
    # Then get interactions
    response = await async_client.get("/agents/test_agent/interactions")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

@pytest.mark.asyncio
async def test_nonexistent_agent(async_client):
    """Test endpoints with nonexistent agent ID."""
    response = await async_client.get("/agents/nonexistent/runs")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
    
    response = await async_client.get("/agents/nonexistent/interactions")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

@pytest.mark.asyncio
async def test_invalid_message(async_client):
    """Test storing an invalid message."""
    # Missing required fields
    message = {"message": "Test message"}
    response = await async_client.post("/agents/message", json=message)
    assert response.status_code == 422  # Validation error
    
    # Invalid interaction type
    message = {
        "sender_id": "test_agent",
        "receiver_id": "test_agent_2",
        "topic": "test_topic",
        "message": "Test message content",
        "interaction_type": "invalid_type"
    }
    response = await async_client.post("/agents/message", json=message)
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_generate_synthetic_kqml(async_client):
    """Test generating synthetic interaction."""
    # First create an agent
    agent_data = {
        "id": "test_agent",
        "type": "human",
        "role": "user"
    }
    response = await async_client.post("/agents", json=agent_data)
    assert response.status_code == 200

    # Then generate interaction
    response = await async_client.post("/synthetic/kqml")
    assert response.status_code == 200
    data = response.json()
    assert "interaction_id" in data
    assert "sender_id" in data
    assert "receiver_id" in data
    assert "topic" in data
    assert "message" in data

@pytest.mark.asyncio
async def test_generate_synthetic_data(async_client):
    """Test generating synthetic data."""
    # Generate synthetic data
    response = await async_client.post("/synthetic/data", json={
        "numAgents": 2,
        "numInteractions": 1
    })
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "success"
    assert "data" in data
    assert "agents" in data["data"]
    assert "interactions" in data["data"]
    assert len(data["data"]["agents"]) == 2
    assert len(data["data"]["interactions"]) == 1

@pytest.mark.asyncio
async def test_get_network(async_client):
    """Test getting network data."""
    response = await async_client.get("/network")
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "edges" in data
    assert isinstance(data["nodes"], list)
    assert isinstance(data["edges"], list)

@pytest.mark.asyncio
async def test_get_network_with_filters(async_client):
    """Test getting network data with filters."""
    response = await async_client.get("/network?node_type=Agent")
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "edges" in data
    assert isinstance(data["nodes"], list)
    assert isinstance(data["edges"], list)

@pytest.mark.asyncio
async def test_query_network(async_client):
    """Test advanced network query endpoint."""
    query = {
        "node_type": "Agent",
        "relationship_type": "INTERACTS",
        "start_time": "2025-02-23T00:00:00Z",
        "end_time": "2025-02-23T23:59:59Z",
        "include_properties": True
    }
    response = await async_client.post("/network/query", json=query)
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "edges" in data
    assert isinstance(data["nodes"], list)
    assert isinstance(data["edges"], list)

@pytest.mark.asyncio
@pytest.mark.parametrize("test_case", [
    ("invalid_message", {"invalid": "data"}, 422),
    ("missing_agent", {"id": "nonexistent"}, 404),
    ("invalid_query", {"invalid_field": "value"}, 422),
])
async def test_error_handling(async_client, test_case):
    """Test error handling for various scenarios."""
    name, data, expected_status = test_case
    
    if name == "invalid_message":
        response = await async_client.post("/agents/message", json=data)
    elif name == "missing_agent":
        response = await async_client.get(f"/agents/{data['id']}/interactions")
    else:
        response = await async_client.post("/network/query", json=data)
    
    assert response.status_code == expected_status
