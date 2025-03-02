"""Test database clearing functionality."""
import pytest
from app.database.arango.database import ArangoDatabase
from app.blockchain.models.wallet import Wallet
from app.blockchain.models.transaction import EthereumTransaction
from datetime import datetime

class TestClearDatabase:
    """Test database clearing functionality."""

    @pytest.mark.asyncio
    async def test_clear_database(self, test_db_arango):
        """Test that the clear_database method properly removes all data."""
        # Set up blockchain collections
        await test_db_arango.setup_blockchain_collections()
        
        # Test setup: Add some test blockchain data
        wallet1_data = {
            "address": "0x1234567890123456789012345678901234567890",
            "chain": "ethereum",
            "balance": 1.0,
            "type": "EOA"
        }
        await test_db_arango.store_wallet(wallet1_data)
        
        # Add another wallet
        wallet2_data = {
            "address": "0x0987654321098765432109876543210987654321",
            "chain": "ethereum", 
            "balance": 2.0,
            "type": "contract"
        }
        await test_db_arango.store_wallet(wallet2_data)
        
        # Add a transaction
        transaction_data = {
            "hash": "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
            "chain": "ethereum",
            "block_number": 12345678,
            "timestamp": datetime.now().isoformat(),
            "from_address": wallet1_data["address"],
            "to_address": wallet2_data["address"],
            "value": 1000000000000000000,  # 1 ETH
            "gas_limit": 21000,
            "gas_price": 20000000000,
            "status": "success"
        }
        await test_db_arango.store_transaction(transaction_data)
        
        # Verify data exists
        wallets = await test_db_arango.get_wallets(100, 0)
        transactions = await test_db_arango.get_transactions(100, 0)
        # During transaction insertion, the wallet references may be created again, so there could be 4 wallet entries
        assert len(wallets) >= 2, "Expected at least 2 wallets to be stored"
        assert len(transactions) == 1, "Expected 1 transaction to be stored"
        
        # Test the method - clear the database
        result = await test_db_arango.clear_database()
        
        # Verify data was cleared
        wallets_after = await test_db_arango.get_wallets(100, 0)
        transactions_after = await test_db_arango.get_transactions(100, 0)
        
        # Assertions
        assert len(wallets_after) == 0, "Expected all wallets to be deleted"
        assert len(transactions_after) == 0, "Expected all transactions to be deleted"
        assert "nodes_deleted" in result, "Expected result to contain nodes_deleted count"
        assert "relationships_deleted" in result, "Expected result to contain relationships_deleted count"
        assert result["nodes_deleted"] >= 2, "Expected at least 2 nodes to be deleted"
        assert result["relationships_deleted"] >= 1, "Expected at least 1 relationship to be deleted"