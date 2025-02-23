"""Test main application endpoints."""
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
import pytest_asyncio
from app.main import app

@pytest_asyncio.fixture
async def async_client(test_app):
    """Create an async test client."""
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
        yield client

@pytest.mark.asyncio
async def test_root(async_client):
    """Test root endpoint."""
    response = await async_client.get("/")
    assert response.status_code == 200
    assert "version" in response.json()

@pytest.mark.asyncio
async def test_agent_message(async_client):
    """Test agent message endpoint."""
    test_message = {
        "sender": "sensor1",
        "receiver": "analyzer1",
        "performative": "tell",
        "content": "temperature 25.0 celsius"
    }
    response = await async_client.post("/agents/message", json=test_message)
    assert response.status_code == 200
    assert "status" in response.json()
    assert "message_id" in response.json()

@pytest.mark.asyncio
async def test_agent_runs(async_client):
    """Test getting agent runs."""
    # First, create some data for the agent
    params = {"numAgents": 1, "numInteractions": 2}
    response = await async_client.post("/synthetic/data", json=params)
    assert response.status_code == 200
    
    # Now get the agent's runs
    response = await async_client.get("/agents/sensor1/runs")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_agent_interactions(async_client):
    """Test getting agent interactions."""
    # First, create some data for the agent
    params = {"numAgents": 1, "numInteractions": 2}
    response = await async_client.post("/synthetic/data", json=params)
    assert response.status_code == 200
    
    # Now get the agent's interactions
    response = await async_client.get("/agents/sensor1/interactions")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_generate_synthetic_kqml(async_client):
    """Test synthetic KQML message generation endpoint."""
    response = await async_client.post("/synthetic/kqml")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "message_id" in data
    assert "run_id" in data

@pytest.mark.asyncio
async def test_generate_synthetic_data(async_client):
    """Test synthetic dataset generation endpoint."""
    params = {"numAgents": 3, "numInteractions": 5}
    response = await async_client.post("/synthetic/data", json=params)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["num_interactions"] == params["numInteractions"]
    assert len(data["interaction_ids"]) == params["numInteractions"]

@pytest.mark.asyncio
async def test_get_network(async_client):
    """Test network structure endpoint."""
    response = await async_client.get("/network")
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "links" in data

@pytest.mark.asyncio
async def test_get_network_with_filters(async_client):
    """Test network structure endpoint with filters."""
    response = await async_client.get("/network?node_type=Agent&time_range=24h")
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "links" in data

@pytest.mark.asyncio
async def test_query_network(async_client):
    """Test advanced network query endpoint."""
    test_query = {
        "node_type": "Agent",
        "relationship_type": "SENT",
        "start_time": "2025-01-01T00:00:00Z",
        "end_time": "2025-12-31T23:59:59Z",
        "agent_ids": ["sensor1"],
        "limit": 10,
        "include_properties": True
    }
    response = await async_client.post("/network/query", json=test_query)
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "links" in data

@pytest.mark.parametrize("test_case", [
    {
        "endpoint": "/agents/message",
        "method": "post",
        "data": {"invalid": "data"},
        "expected_status": 422
    },
    {
        "endpoint": "/agents/nonexistent/runs",
        "method": "get",
        "expected_status": 404
    },
    {
        "endpoint": "/network/query",
        "method": "post",
        "data": {"invalid": "query"},
        "expected_status": 422
    }
])
@pytest.mark.asyncio
async def test_error_handling(async_client, test_case):
    """Test error handling for various scenarios."""
    method = getattr(async_client, test_case["method"])
    kwargs = {"data": test_case["data"]} if "data" in test_case else {}
    response = await method(test_case["endpoint"], **kwargs)
    assert response.status_code == test_case["expected_status"]
