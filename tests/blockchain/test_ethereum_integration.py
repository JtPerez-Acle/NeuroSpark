"""Integration tests for Ethereum blockchain functionality."""
import pytest
import pytest_asyncio
from unittest.mock import patch, MagicMock
import asyncio
import datetime

from app.blockchain.connectors.ethereum import EthereumConnector
from app.blockchain.models import Wallet, EthereumTransaction, EthereumContract, EthereumEvent

# Import the database fixture from conftest.py
from tests.conftest import test_db_arango

@pytest_asyncio.fixture
async def ethereum_connector_mock():
    """Create a mock Ethereum connector for testing."""
    connector = MagicMock(spec=EthereumConnector)
    
    # Mock wallet data
    mock_wallet = Wallet(
        address="0x1234567890123456789012345678901234567890",
        chain="ethereum",
        balance=5000000000000000000,  # 5 ETH
        type="EOA",
        first_seen=datetime.datetime.utcnow(),
        last_active=datetime.datetime.utcnow()
    )
    connector.get_wallet.return_value = mock_wallet
    
    # Mock transaction data
    mock_transaction = EthereumTransaction(
        hash="0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
        block_number=12345678,
        timestamp=datetime.datetime.utcnow(),
        from_address="0x1234567890123456789012345678901234567890",
        to_address="0x0987654321098765432109876543210987654321",
        value=1000000000000000000,  # 1 ETH
        gas_used=21000,
        gas_price=50000000000,  # 50 Gwei
        status="success"
    )
    connector.get_transaction.return_value = mock_transaction
    
    # Mock transaction list
    connector.get_transactions_for_address.return_value = [mock_transaction]
    
    # Mock contract data
    mock_contract = EthereumContract(
        address="0x0987654321098765432109876543210987654321",
        creator="0x1234567890123456789012345678901234567890",
        creation_timestamp=datetime.datetime.utcnow(),
        verified=True,
        name="TestContract"
    )
    connector.get_contract.return_value = mock_contract
    
    yield connector

@pytest.mark.asyncio
async def test_wallet_database_integration(test_db_arango, ethereum_connector_mock):
    """Test wallet storage and retrieval in database."""
    # First ensure the blockchain collections exist
    await test_db_arango.setup_blockchain_collections()
    
    # Get mock wallet data
    mock_wallet = await ethereum_connector_mock.get_wallet("0x1234567890123456789012345678901234567890")
    
    # Convert to ArangoDB document format
    wallet_doc = mock_wallet.to_arangodb_document()
    
    # Store in database
    await test_db_arango.store_wallet(wallet_doc)
    
    # Retrieve wallet from database
    retrieved_wallet = await test_db_arango.get_wallet("0x1234567890123456789012345678901234567890")
    
    # Validate
    assert retrieved_wallet is not None
    assert retrieved_wallet['address'] == "0x1234567890123456789012345678901234567890"
    assert retrieved_wallet['chain'] == "ethereum"
    assert retrieved_wallet['type'] == "EOA"

@pytest.mark.asyncio
async def test_transaction_database_integration(test_db_arango, ethereum_connector_mock):
    """Test transaction storage and retrieval in database."""
    # First ensure the blockchain collections exist
    await test_db_arango.setup_blockchain_collections()
    
    # Get mock transaction data
    mock_tx = await ethereum_connector_mock.get_transaction("0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890")
    
    # Convert to ArangoDB document format
    tx_doc = mock_tx.to_arangodb_document()
    
    # Store in database
    await test_db_arango.store_transaction(tx_doc)
    
    # Retrieve transaction from database
    retrieved_tx = await test_db_arango.get_transaction("0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890")
    
    # Validate
    assert retrieved_tx is not None
    assert retrieved_tx['hash'] == "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
    assert retrieved_tx['chain'] == "ethereum"
    assert retrieved_tx['from_address'] == "0x1234567890123456789012345678901234567890"
    assert retrieved_tx['status'] == "success"
    
    # Test wallet_to_wallet relationship was created
    # Get wallets created by transaction
    wallets = await test_db_arango.get_wallets_by_query({'chain': 'ethereum'})
    assert len(wallets) == 2
    
    # Test wallet transaction query
    wallet_txs = await test_db_arango.get_wallet_transactions("0x1234567890123456789012345678901234567890")
    assert len(wallet_txs) > 0

@pytest.mark.asyncio
async def test_contract_database_integration(test_db_arango, ethereum_connector_mock):
    """Test contract storage and retrieval in database."""
    # First ensure the blockchain collections exist
    await test_db_arango.setup_blockchain_collections()
    
    # Get mock contract data
    mock_contract = await ethereum_connector_mock.get_contract("0x0987654321098765432109876543210987654321")
    
    # Convert to ArangoDB document format
    contract_doc = mock_contract.to_arangodb_document()
    
    # Store in database
    await test_db_arango.store_contract(contract_doc)
    
    # Retrieve contract from database
    retrieved_contract = await test_db_arango.get_contract("0x0987654321098765432109876543210987654321")
    
    # Validate
    assert retrieved_contract is not None
    assert retrieved_contract['address'] == "0x0987654321098765432109876543210987654321"
    assert retrieved_contract['chain'] == "ethereum"
    assert retrieved_contract['creator'] == "0x1234567890123456789012345678901234567890"
    assert retrieved_contract['verified'] is True

@pytest.mark.asyncio
async def test_db_arango_get_wallets_by_query(test_db_arango, ethereum_connector_mock):
    """Test wallet querying by criteria."""
    # First ensure the blockchain collections exist
    await test_db_arango.setup_blockchain_collections()
    
    # Create and store Ethereum wallet directly
    eth_wallet = {
        "address": "0x1234567890123456789012345678901234567890",
        "chain": "ethereum",
        "type": "EOA",
        "balance": 5000000000000000000,
        "first_seen": datetime.datetime.utcnow().isoformat(),
        "last_active": datetime.datetime.utcnow().isoformat(),
        "tags": ["trader"],
        "risk_score": 15.5
    }
    await test_db_arango.store_wallet(eth_wallet)
    
    # Create and store Solana wallet directly
    solana_wallet = {
        "address": "0x9876543210987654321098765432109876543210",
        "chain": "solana",
        "type": "EOA",
        "balance": 5000000000000000000,
        "first_seen": datetime.datetime.utcnow().isoformat(),
        "last_active": datetime.datetime.utcnow().isoformat(),
        "tags": ["nft_collector"],
        "risk_score": 25.2
    }
    await test_db_arango.store_wallet(solana_wallet)
    
    # Test query by chain
    ethereum_wallets = await test_db_arango.get_wallets_by_query({"chain": "ethereum"})
    assert len(ethereum_wallets) == 1
    assert ethereum_wallets[0]["address"] == "0x1234567890123456789012345678901234567890"
    
    solana_wallets = await test_db_arango.get_wallets_by_query({"chain": "solana"})
    assert len(solana_wallets) == 1
    assert solana_wallets[0]["address"] == "0x9876543210987654321098765432109876543210"
    
    # Test query by wallet type
    eoa_wallets = await test_db_arango.get_wallets_by_query({"type": "EOA"})
    assert len(eoa_wallets) == 2