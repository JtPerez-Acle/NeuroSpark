"""Test main application endpoints."""
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
import pytest_asyncio
from app.main import app
from datetime import datetime, timezone

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

# Legacy agent-based tests have been removed since we migrated to blockchain architecture

@pytest.mark.asyncio
async def test_generate_synthetic_data(async_client, monkeypatch):
    """Test generating synthetic blockchain data."""
    from app.data_generator import DataGenerator
    
    # Create a mock implementation using blockchain terminology
    def mock_generate(self, num_wallets, num_transactions, **kwargs):
        # Return synthetic blockchain data with wallets and transactions
        
        # Define addresses
        address_a = f"0x{''.join('a' for _ in range(40))}"
        address_b = f"0x{''.join('b' for _ in range(40))}"
        tx_hash = f"0x{''.join('c' for _ in range(64))}"
        
        # Create transaction data
        tx_data = {
            "hash": tx_hash,
            "from_address": address_a,
            "to_address": address_b,
            "chain": "ethereum",
            "block_number": 123456,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "value": 1000000000000000000,  # 1 ETH in wei
            "gas_used": 21000,
            "gas_price": 50000000000,
            "status": "success"
        }
        
        return {
            "wallets": [
                {
                    "id": address_a.lower(),
                    "address": address_a,
                    "chain": "ethereum",
                    "type": "EOA",  # External Owned Account
                    "role": "trader",
                    "balance": 100.0,
                    "risk_score": 10.0,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "tags": ["trader"]
                },
                {
                    "id": address_b.lower(),
                    "address": address_b,
                    "chain": "ethereum",
                    "type": "contract",  # Smart contract
                    "role": "token",
                    "balance": 0.0,
                    "risk_score": 30.0,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "tags": ["token", "erc20"]
                }
            ],
            "transactions": [
                {
                    "interaction_id": tx_hash,
                    "sender_id": address_a.lower(),
                    "receiver_id": address_b.lower(),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "topic": "ethereum_transfer",
                    "message": "Transfer from trader to token contract",
                    "interaction_type": "transfer",
                    "metadata": {
                        "transaction": tx_data,
                        "blockchain": "ethereum",
                        "token_symbol": "ETH",
                        "token_amount": 1000000000000000000,
                        "block": 123456
                    }
                }
            ],
            "run_id": "test_run_id",
            "scenario": "token_transfer",
            "blockchain": "ethereum",
            "start_block": 123456,
            "end_block": 123456
        }
    
    # Apply the mock
    monkeypatch.setattr(DataGenerator, "generate_blockchain_data", mock_generate)
    
    # Generate synthetic blockchain data
    response = await async_client.post("/generate/data", json={
        "numWallets": 2,
        "numTransactions": 1
    })
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "success"
    assert "data" in data
    assert "wallets" in data["data"]
    assert "transactions" in data["data"]
    assert len(data["data"]["wallets"]) == 2
    assert len(data["data"]["transactions"]) == 1

@pytest.mark.asyncio
async def test_get_network(async_client):
    """Test getting blockchain network data."""
    response = await async_client.get("/graph/network")
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "links" in data
    assert isinstance(data["nodes"], list)
    assert isinstance(data["links"], list)

@pytest.mark.asyncio
async def test_get_network_with_filters(async_client):
    """Test getting blockchain network data with filters."""
    response = await async_client.get("/graph/network?node_type=wallet")
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "links" in data
    assert isinstance(data["nodes"], list)
    assert isinstance(data["links"], list)

@pytest.mark.asyncio
async def test_query_blockchain_network(async_client):
    """Test advanced blockchain network query endpoint."""
    # Use blockchain-specific parameters
    query = {
        "node_type": "wallet",  # Query for wallet entities
        "relationship_type": "transaction",  # Look for transaction relationships
        "start_time": "2025-02-23T00:00:00Z",  # Start of time window
        "end_time": "2025-02-23T23:59:59Z",  # End of time window
        "addresses": ["0x1234567890123456789012345678901234567890"],  # Specific blockchain address to query
        "include_properties": True  # Include transaction details
    }
    response = await async_client.post("/graph/query", json=query)
    assert response.status_code == 200
    data = response.json()
    # Verify response contains blockchain network data
    assert "nodes" in data  # Contains wallets and contracts
    assert "links" in data  # Contains transactions
    assert isinstance(data["nodes"], list)
    assert isinstance(data["links"], list)

@pytest.mark.asyncio
async def test_wallet_not_found_error(async_client):
    """Test error handling for missing wallet."""
    response = await async_client.get("/blockchain/wallets/0xnonexistent")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

# This test is redundant with test_query_blockchain_network and has been removed
