"""Test Ethereum blockchain connector."""
import os
import pytest
import pytest_asyncio
from unittest.mock import patch, MagicMock

from app.blockchain.connectors.ethereum import EthereumConnector
from app.blockchain.models.transaction import EthereumTransaction
from app.blockchain.models.wallet import Wallet

# Mock web3 to avoid actual blockchain calls
@pytest.fixture
def mock_web3():
    """Create a mock Web3 object for testing."""
    with patch('web3.Web3', autospec=True) as mock_web3_class:
        mock_web3 = MagicMock()
        mock_web3_class.return_value = mock_web3
        
        # Mock eth property
        mock_eth = MagicMock()
        mock_web3.eth = mock_eth
        
        # Mock common methods
        mock_eth.get_block.return_value = {
            'number': 12345678,
            'timestamp': 1612345678,
            'hash': '0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef'
        }
        
        mock_eth.get_transaction.return_value = {
            'hash': '0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890',
            'from': '0x1234567890123456789012345678901234567890',
            'to': '0x0987654321098765432109876543210987654321',
            'value': 1000000000000000000,  # 1 ETH in wei
            'gas': 21000,
            'gasPrice': 50000000000,  # 50 Gwei
            'input': '0x',
            'nonce': 42,
            'blockNumber': 12345678,
            'blockHash': '0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef',
            'transactionIndex': 0
        }
        
        mock_eth.get_transaction_receipt.return_value = {
            'transactionHash': '0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890',
            'blockNumber': 12345678,
            'blockHash': '0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef',
            'gasUsed': 21000,
            'status': 1,  # Success
            'logs': []
        }
        
        mock_eth.get_balance.return_value = 5000000000000000000  # 5 ETH in wei
        
        # Mock contract method
        mock_contract = MagicMock()
        mock_eth.contract.return_value = mock_contract
        
        # Mock web3.toChecksumAddress method
        mock_web3.toChecksumAddress = lambda addr: addr
        
        # Mock web3.isAddress method
        mock_web3.isAddress = lambda addr: addr.startswith('0x')
        
        yield mock_web3

@pytest_asyncio.fixture
async def ethereum_connector(mock_web3):
    """Create an EthereumConnector with mocked Web3."""
    connector = EthereumConnector(
        provider_url="http://localhost:8545",
        api_key="test_key",
        max_retries=1,
        retry_delay=0.1
    )
    
    # Replace the Web3 instance with our mock
    connector._web3 = mock_web3
    connector._connected = True
    
    yield connector

class TestEthereumConnector:
    """Tests for the EthereumConnector class."""
    
    @pytest.mark.asyncio
    async def test_connect(self, mock_web3):
        """Test connector initialization and connection."""
        # Arrange
        connector = EthereumConnector(
            provider_url="http://localhost:8545",
            api_key="test_key"
        )
        
        # Act
        await connector.connect()
        
        # Assert
        assert connector.is_connected()
    
    @pytest.mark.asyncio
    async def test_get_transaction(self, ethereum_connector, mock_web3):
        """Test retrieving a transaction."""
        # Arrange
        tx_hash = "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
        
        # Act
        transaction = await ethereum_connector.get_transaction(tx_hash)
        
        # Assert
        assert transaction is not None
        assert transaction.hash == tx_hash
        assert transaction.from_address == "0x1234567890123456789012345678901234567890"
        assert transaction.to_address == "0x0987654321098765432109876543210987654321"
        assert transaction.value == 1000000000000000000
        assert transaction.gas == 21000
        assert transaction.status == "success"
    
    @pytest.mark.asyncio
    async def test_get_wallet(self, ethereum_connector, mock_web3):
        """Test retrieving wallet information."""
        # Arrange
        address = "0x1234567890123456789012345678901234567890"
        
        # Act
        wallet = await ethereum_connector.get_wallet(address)
        
        # Assert
        assert wallet is not None
        assert wallet.address == address
        assert wallet.chain == "ethereum"
        assert wallet.balance == 5000000000000000000
    
    @pytest.mark.asyncio
    async def test_get_transactions_for_address(self, ethereum_connector, mock_web3):
        """Test retrieving transactions for an address."""
        # Arrange
        address = "0x1234567890123456789012345678901234567890"
        
        # Mock the API call to get transactions
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": "1",
            "message": "OK",
            "result": [
                {
                    "hash": "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
                    "from": "0x1234567890123456789012345678901234567890",
                    "to": "0x0987654321098765432109876543210987654321",
                    "value": "1000000000000000000",
                    "gas": "21000",
                    "gasPrice": "50000000000",
                    "blockNumber": "12345678",
                    "timeStamp": "1612345678",
                    "input": "0x"
                }
            ]
        }
        
        with patch('aiohttp.ClientSession.get', return_value=MagicMock(__aenter__=MagicMock(return_value=mock_response))):
            # Act
            transactions = await ethereum_connector.get_transactions_for_address(address)
            
            # Assert
            assert len(transactions) == 1
            assert transactions[0].hash == "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
            assert transactions[0].from_address == address