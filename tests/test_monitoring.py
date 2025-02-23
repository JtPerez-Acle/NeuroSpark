"""Test monitoring functionality."""
import pytest
import httpx
from httpx import AsyncClient
from app.main import app

@pytest.fixture
async def test_client():
    """Create test client."""
    async with AsyncClient(base_url="http://localhost:8001") as client:
        yield client

@pytest.fixture
def test_app():
    """Create test app."""
    yield app

@pytest.fixture
async def async_client(test_app):
    """Create async client."""
    async with AsyncClient(
        base_url="http://localhost:8001",
        transport=httpx.ASGITransport(app=test_app)
    ) as client:
        yield client

@pytest.mark.asyncio
async def test_metrics_endpoint(test_app, async_client):
    """Test metrics endpoint."""
    response = await async_client.get("/metrics")
    assert response.status_code == 200
    assert "http_requests_total" in response.text

@pytest.mark.asyncio
async def test_http_request_metrics(test_app, async_client):
    """Test HTTP request metrics."""
    # Make a request
    await async_client.get("/")
    
    # Check metrics
    response = await async_client.get("/metrics")
    assert response.status_code == 200
    assert "http_requests_total" in response.text
    assert "method=\"GET\"" in response.text
    assert "endpoint=\"/\"" in response.text

@pytest.mark.asyncio
async def test_websocket_metrics(test_app, async_client):
    """Test WebSocket metrics."""
    # Check metrics
    response = await async_client.get("/metrics")
    assert response.status_code == 200
    assert "websocket_connections" in response.text

@pytest.mark.asyncio
async def test_database_metrics(test_app, async_client):
    """Test database metrics."""
    # Check metrics
    response = await async_client.get("/metrics")
    assert response.status_code == 200
    assert "database_operations_total" in response.text
