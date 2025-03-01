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
            # Test storing and retrieving a wallet
            wallet_data = {
                "address": "0x123abc456def789",
                "chain": "ethereum",
                "wallet_type": "EOA",
                "role": "trader",
                "balance": 1.5,
                "first_seen": "2024-01-01T00:00:00Z",
                "last_active": "2024-03-20T12:00:00Z",
                "risk_score": 25.0
            }
            await test_db_arango.store_wallet(wallet_data)
            
            wallets = await test_db_arango.get_wallets()
            assert len(wallets) > 0
            wallet = await test_db_arango.get_wallet("0x123abc456def789")
            assert wallet["address"] == "0x123abc456def789"
            assert wallet["chain"] == "ethereum"
            assert wallet["wallet_type"] == "EOA"
            assert wallet["role"] == "trader"

            # Test storing and retrieving a transaction
            transaction_data = {
                "hash": "0xabcdef1234567890",
                "from_address": "0x123abc456def789",
                "to_address": "0x987fed654cba321",
                "chain": "ethereum",
                "value": 1000000000000000000,  # 1 ETH in wei
                "gas_used": 21000,
                "gas_price": 20000000000,
                "block_number": 12345678,
                "timestamp": "2024-03-20T12:00:00Z",
                "status": "success"
            }
            await test_db_arango.store_transaction(transaction_data)

            # Test retrieving transactions
            transactions = await test_db_arango.get_transactions()
            assert len(transactions) > 0
            transaction = await test_db_arango.get_transaction("0xabcdef1234567890")
            assert transaction is not None
            assert transaction["hash"] == "0xabcdef1234567890"
            assert transaction["from_address"] == "0x123abc456def789"
            assert transaction["to_address"] == "0x987fed654cba321"

            # Test storing and retrieving a contract
            contract_data = {
                "address": "0x987fed654cba321",
                "chain": "ethereum",
                "role": "token",
                "name": "Test Token",
                "symbol": "TST",
                "creator": "0x123abc456def789",
                "creation_tx": "0xabcdef1234567890",
                "creation_timestamp": "2024-03-20T12:00:00Z",
                "verified": True,
                "risk_score": 15.0
            }
            await test_db_arango.store_contract(contract_data)
            
            contracts = await test_db_arango.get_contracts()
            assert len(contracts) > 0
            contract = await test_db_arango.get_contract("0x987fed654cba321")
            assert contract is not None
            assert contract["address"] == "0x987fed654cba321"
            assert contract["name"] == "Test Token"
            assert contract["verified"] is True

            # Test retrieving wallet transactions
            wallet_txs = await test_db_arango.get_wallet_transactions("0x123abc456def789")
            assert len(wallet_txs) > 0
            assert wallet_txs[0]["hash"] == "0xabcdef1234567890"

            # Test retrieving network data
            network = await test_db_arango.get_network()
            assert "nodes" in network
            assert "edges" in network
            assert isinstance(network["nodes"], list)
            assert isinstance(network["edges"], list)

        finally:
            # Clean up test data
            await test_db_arango.clear_database()
