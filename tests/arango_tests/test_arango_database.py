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
    async def test_store_and_get_wallet(self, test_db):
        """Test storing and retrieving a wallet."""
        # Create test wallet
        wallet_address = f"0x{uuid4().hex[:40]}"
        wallet_data = {
            "address": wallet_address,
            "chain": "ethereum",
            "type": "EOA",
            "balance": 1.5,
            "tags": ["test", "wallet"],
            "risk_score": 25.0,
            "metadata": {"test": True},
            "first_seen": datetime.now(timezone.utc).isoformat(),
            "last_active": datetime.now(timezone.utc).isoformat()
        }
        
        # Ensure blockchain collections exist
        await test_db.setup_blockchain_collections()
        
        # Store wallet
        await test_db.store_wallet(wallet_data)
        
        # Retrieve wallet
        wallet = await test_db.get_wallet(wallet_address, "ethereum")
        assert wallet is not None
        assert wallet["address"] == wallet_address
        assert wallet["chain"] == "ethereum"
        assert wallet["type"] == "EOA"
        assert wallet["balance"] == 1.5
        assert "test" in wallet["tags"]
        assert wallet["risk_score"] == 25.0
        assert wallet["metadata"]["test"] is True
    
    @pytest.mark.asyncio
    async def test_store_and_get_transaction(self, test_db):
        """Test storing and retrieving a blockchain transaction."""
        # Create test wallets
        sender_address = f"0x{uuid4().hex[:40]}"
        sender_data = {
            "address": sender_address,
            "chain": "ethereum",
            "type": "EOA",
            "balance": 10.0
        }
        
        receiver_address = f"0x{uuid4().hex[:40]}"
        receiver_data = {
            "address": receiver_address,
            "chain": "ethereum",
            "type": "contract",
            "balance": 0.0
        }
        
        # Ensure blockchain collections exist
        await test_db.setup_blockchain_collections()
        
        # Store wallets
        await test_db.store_wallet(sender_data)
        await test_db.store_wallet(receiver_data)
        
        # Create transaction
        tx_hash = f"0x{uuid4().hex[:64]}"
        transaction_data = {
            "hash": tx_hash,
            "from_address": sender_address,
            "to_address": receiver_address,
            "chain": "ethereum",
            "block_number": 12345678,
            "value": 1000000000000000000,  # 1 ETH in wei
            "gas_used": 21000,
            "gas_price": 50000000000,
            "input_data": "0x",
            "status": "success",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "risk_score": 15.0
        }
        
        # Store transaction
        await test_db.store_transaction(transaction_data)
        
        # Retrieve transaction
        transaction = await test_db.get_transaction(tx_hash, "ethereum")
        assert transaction is not None
        assert transaction["hash"] == tx_hash
        assert transaction["from_address"] == sender_address
        assert transaction["to_address"] == receiver_address
        assert transaction["chain"] == "ethereum"
        assert transaction["block_number"] == 12345678
        assert transaction["value"] == 1000000000000000000
        assert transaction["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_get_wallet_transactions(self, test_db):
        """Test retrieving transactions for a specific wallet."""
        # Create test wallets
        wallet1_address = f"0x{uuid4().hex[:40]}"
        wallet1_data = {
            "address": wallet1_address,
            "chain": "ethereum", 
            "type": "EOA",
            "balance": 10.0
        }
        
        wallet2_address = f"0x{uuid4().hex[:40]}"
        wallet2_data = {
            "address": wallet2_address,
            "chain": "ethereum",
            "type": "EOA",
            "balance": 5.0
        }
        
        # Ensure blockchain collections exist
        await test_db.setup_blockchain_collections()
        
        # Store wallets
        await test_db.store_wallet(wallet1_data)
        await test_db.store_wallet(wallet2_data)
        
        # Create transactions
        tx1_hash = f"0x{uuid4().hex[:64]}"
        tx1_data = {
            "hash": tx1_hash,
            "from_address": wallet1_address,
            "to_address": wallet2_address,
            "chain": "ethereum",
            "block_number": 12345678,
            "value": 1000000000000000000,  # 1 ETH
            "gas_used": 21000,
            "gas_price": 50000000000,
            "status": "success",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        tx2_hash = f"0x{uuid4().hex[:64]}"
        tx2_data = {
            "hash": tx2_hash,
            "from_address": wallet2_address,
            "to_address": wallet1_address,
            "chain": "ethereum",
            "block_number": 12345679,
            "value": 500000000000000000,  # 0.5 ETH
            "gas_used": 21000,
            "gas_price": 50000000000,
            "status": "success",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Store transactions
        await test_db.store_transaction(tx1_data)
        await test_db.store_transaction(tx2_data)
        
        # Get wallet1's transactions
        wallet1_transactions = await test_db.get_wallet_transactions(wallet1_address)
        assert len(wallet1_transactions) == 2
        
        # Get wallet2's transactions
        wallet2_transactions = await test_db.get_wallet_transactions(wallet2_address)
        assert len(wallet2_transactions) == 2
    
    @pytest.mark.asyncio
    async def test_clear_database(self, test_db):
        """Test clearing the database."""
        # Ensure blockchain collections exist
        await test_db.setup_blockchain_collections()
        
        # Add test data
        wallet_data = {
            "address": f"0x{uuid4().hex[:40]}",
            "chain": "ethereum",
            "type": "EOA",
            "balance": 10.0
        }
        await test_db.store_wallet(wallet_data)
        
        tx_data = {
            "hash": f"0x{uuid4().hex[:64]}",
            "from_address": wallet_data["address"],
            "to_address": f"0x{uuid4().hex[:40]}",
            "chain": "ethereum",
            "block_number": 12345678,
            "value": 1000000000000000000,
            "status": "success",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        await test_db.store_transaction(tx_data)
        
        # Verify data exists
        wallets = await test_db.get_wallets()
        transactions = await test_db.get_transactions()
        assert len(wallets) > 0
        assert len(transactions) > 0
        
        # Clear database
        result = await test_db.clear_database()
        
        # Verify data was cleared
        wallets_after = await test_db.get_wallets()
        transactions_after = await test_db.get_transactions()
        
        # Could be empty lists or None depending on implementation
        if wallets_after is not None:
            assert len(wallets_after) == 0
        if transactions_after is not None:
            assert len(transactions_after) == 0
        
        # Check result
        assert "success" in result or "nodes_deleted" in result  # Either format is acceptable
        if "success" in result:
            assert result["success"] is True
        if "nodes_deleted" in result:
            assert isinstance(result["nodes_deleted"], int)
        if "relationships_deleted" in result:
            assert isinstance(result["relationships_deleted"], int)