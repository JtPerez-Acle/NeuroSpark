"""Test blockchain API routes."""
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
async def test_api_root(async_client):
    """Test root endpoint."""
    response = await async_client.get("/")
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["message"] == "NeuroSpark: AI-Powered Blockchain Intelligence API"
    assert "version" in response_data
    assert "capabilities" in response_data
    assert isinstance(response_data["capabilities"], list)
    assert "Blockchain Analytics" in response_data["capabilities"]

@pytest.mark.asyncio
async def test_blockchain_wallet_operations(async_client):
    """Test wallet blockchain operations."""
    # Create wallet via data generation endpoint
    wallet_data = {
        "address": "0xabcdef1234567890",
        "chain": "ethereum",
        "wallet_type": "EOA",
        "role": "trader",
        "balance": 1.5,
        "first_seen": "2024-01-01T00:00:00Z",
        "last_active": "2024-03-20T12:00:00Z",
        "risk_score": 25.0
    }
    
    # Store wallet through API
    response = await async_client.post("/generate/transaction", json={})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "sender" in data
    assert "receiver" in data
    assert "transaction" in data
    
    # Get wallet info
    sender_address = data["sender"]["address"]
    response = await async_client.get(f"/blockchain/wallets/{sender_address}")
    assert response.status_code == 200
    wallet = response.json()
    assert wallet["address"] == sender_address
    assert "wallet_type" in wallet
    assert "chain" in wallet

@pytest.mark.asyncio
async def test_blockchain_transaction_operations(async_client):
    """Test transaction blockchain operations."""
    # Generate a transaction
    response = await async_client.post("/generate/transaction", json={})
    assert response.status_code == 200
    data = response.json()
    
    # Get transaction info by hash
    tx_hash = data["transaction"]["metadata"]["transaction"]["hash"]
    response = await async_client.get(f"/blockchain/transactions/{tx_hash}")
    assert response.status_code == 200
    transaction = response.json()
    assert transaction["hash"] == tx_hash
    assert "from_address" in transaction
    assert "to_address" in transaction
    assert "status" in transaction
    
    # Get wallet transactions
    sender_address = data["sender"]["address"]
    response = await async_client.get(f"/blockchain/wallets/{sender_address}/transactions")
    assert response.status_code == 200
    wallet_txs = response.json()
    assert "items" in wallet_txs
    assert "count" in wallet_txs
    assert wallet_txs["count"] > 0

@pytest.mark.asyncio
async def test_blockchain_data_generation(async_client):
    """Test blockchain data generation endpoints."""
    # Generate blockchain data
    params = {
        "numAgents": 5,
        "numInteractions": 10
    }
    response = await async_client.post("/generate/data", json=params)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "data" in data
    assert "agents" in data["data"]
    assert "interactions" in data["data"]
    assert len(data["data"]["agents"]) == 5
    assert len(data["data"]["interactions"]) == 10
    
    # Generate scenario data
    scenario_params = {
        "scenario": "dex",
        "numAgents": 5,
        "numInteractions": 10,
        "blocks": 5
    }
    response = await async_client.post("/generate/scenario", json=scenario_params)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["scenario"] == "dex"
    assert "data" in data
    assert "agents" in data["data"]
    assert "interactions" in data["data"]

@pytest.mark.asyncio
async def test_blockchain_network_endpoints(async_client):
    """Test blockchain network endpoints."""
    # Generate some data first
    params = {
        "numAgents": 5,
        "numInteractions": 10
    }
    await async_client.post("/generate/data", json=params)
    
    # Test graph endpoints
    response = await async_client.get("/graph/data")
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "edges" in data
    assert isinstance(data["nodes"], list)
    assert isinstance(data["edges"], list)
    
    # Test analysis endpoints
    response = await async_client.get("/analysis/degree_centrality")
    assert response.status_code == 200
    data = response.json()
    assert "node_degrees" in data
    assert isinstance(data["node_degrees"], dict)

@pytest.mark.asyncio
async def test_admin_operations(async_client):
    """Test admin database operations."""
    # Clear database
    response = await async_client.post("/admin/database/clear")
    assert response.status_code == 200
    data = response.json()
    assert data["operation"] == "clear_database"
    assert data["status"] == "success"
    assert "details" in data