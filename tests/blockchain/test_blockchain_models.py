"""Tests for blockchain models."""
import pytest
from datetime import datetime
from app.blockchain.models.wallet import Wallet
from app.blockchain.models.transaction import Transaction
from app.blockchain.models.contract import Contract
from app.blockchain.models.event import Event


class TestWalletModel:
    """Test suite for the Wallet model."""

    def test_wallet_basic(self):
        """Test basic wallet creation and validation."""
        wallet = Wallet(
            address="0x1234567890123456789012345678901234567890",
            chain="ethereum",
            balance=1.5,
            first_seen=datetime.now(),
            last_active=datetime.now(),
            type="EOA",
            tags=["user", "active"],
            risk_score=25.5,
            metadata={"source": "test"}
        )
        
        assert wallet.address == "0x1234567890123456789012345678901234567890"
        assert wallet.chain == "ethereum"
        assert wallet.balance == 1.5
        assert isinstance(wallet.first_seen, datetime)
        assert isinstance(wallet.last_active, datetime)
        assert wallet.type == "EOA"
        assert "user" in wallet.tags
        assert "active" in wallet.tags
        assert wallet.risk_score == 25.5
        assert wallet.metadata["source"] == "test"

    def test_wallet_risk_score_validator(self):
        """Test the risk_score field validator."""
        # Valid risk scores
        wallet = Wallet(
            address="0x1234567890123456789012345678901234567890",
            chain="ethereum",
            risk_score=0
        )
        assert wallet.risk_score == 0
        
        wallet = Wallet(
            address="0x1234567890123456789012345678901234567890",
            chain="ethereum",
            risk_score=50.5
        )
        assert wallet.risk_score == 50.5
        
        wallet = Wallet(
            address="0x1234567890123456789012345678901234567890",
            chain="ethereum",
            risk_score=100
        )
        assert wallet.risk_score == 100
        
        # Invalid risk scores
        with pytest.raises(ValueError):
            Wallet(
                address="0x1234567890123456789012345678901234567890",
                chain="ethereum",
                risk_score=-1
            )
        
        with pytest.raises(ValueError):
            Wallet(
                address="0x1234567890123456789012345678901234567890",
                chain="ethereum",
                risk_score=101
            )

    def test_wallet_to_arangodb_document(self):
        """Test the to_arangodb_document method."""
        now = datetime.now()
        wallet = Wallet(
            address="0x1234567890123456789012345678901234567890",
            chain="ethereum",
            balance=2.5,
            first_seen=now,
            last_active=now,
            tags=["test"],
            risk_score=30.0
        )
        
        doc = wallet.to_arangodb_document()
        
        # Check ArangoDB specific fields
        assert "_key" in doc
        assert doc["_key"] == "ethereum_1234567890123456789012345678901234567890"
        
        # Check datetime conversion
        assert isinstance(doc["first_seen"], str)
        assert isinstance(doc["last_active"], str)
        
        # Check other fields
        assert doc["address"] == "0x1234567890123456789012345678901234567890"
        assert doc["chain"] == "ethereum"
        assert doc["balance"] == 2.5
        assert doc["tags"] == ["test"]
        assert doc["risk_score"] == 30.0


class TestTransactionModel:
    """Test suite for the Transaction model."""

    def test_transaction_basic(self):
        """Test basic transaction creation and validation."""
        transaction = Transaction(
            hash="0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
            chain="ethereum",
            block_number=12345678,
            timestamp=1633046400,  # Unix timestamp
            from_address="0x1234567890123456789012345678901234567890",
            to_address="0x0987654321098765432109876543210987654321",
            value=1000000000000000000,  # 1 ETH in wei
            status="success",
            gas_used=21000,
            gas_price=50000000000,
            input_data="0x",
            risk_score=10.0
        )
        
        assert transaction.hash == "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
        assert transaction.chain == "ethereum"
        assert transaction.block_number == 12345678
        assert isinstance(transaction.timestamp, datetime)  # Should be converted to datetime
        assert transaction.from_address == "0x1234567890123456789012345678901234567890"
        assert transaction.to_address == "0x0987654321098765432109876543210987654321"
        assert transaction.value == 1000000000000000000
        assert transaction.status == "success"
        assert transaction.gas_used == 21000
        assert transaction.gas_price == 50000000000
        assert transaction.input_data == "0x"
        assert transaction.risk_score == 10.0

    def test_transaction_timestamp_conversion(self):
        """Test timestamp conversion in transaction model."""
        # Test with integer timestamp
        transaction = Transaction(
            hash="0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
            chain="ethereum",
            block_number=12345678,
            timestamp=1633046400,  # Unix timestamp
            from_address="0x1234567890123456789012345678901234567890"
        )
        assert isinstance(transaction.timestamp, datetime)
        
        # Test with datetime object
        now = datetime.now()
        transaction = Transaction(
            hash="0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
            chain="ethereum",
            block_number=12345678,
            timestamp=now,
            from_address="0x1234567890123456789012345678901234567890"
        )
        assert transaction.timestamp == now

    def test_transaction_to_arangodb_document(self):
        """Test the to_arangodb_document method."""
        transaction = Transaction(
            hash="0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
            chain="ethereum",
            block_number=12345678,
            timestamp=1633046400,  # Unix timestamp
            from_address="0x1234567890123456789012345678901234567890",
            to_address="0x0987654321098765432109876543210987654321",
            value=1000000000000000000
        )
        
        doc = transaction.to_arangodb_document()
        
        # Check ArangoDB specific fields
        assert "_key" in doc
        assert doc["_key"] == "ethereum_abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
        
        # Check timestamp conversion
        assert isinstance(doc["timestamp"], str)
        
        # Check other fields
        assert doc["hash"] == "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
        assert doc["chain"] == "ethereum"
        assert doc["block_number"] == 12345678
        assert doc["from_address"] == "0x1234567890123456789012345678901234567890"
        assert doc["to_address"] == "0x0987654321098765432109876543210987654321"
        assert doc["value"] == 1000000000000000000


class TestContractModel:
    """Test suite for the Contract model."""

    def test_contract_basic(self):
        """Test basic contract creation and validation."""
        contract = Contract(
            address="0x1234567890123456789012345678901234567890",
            chain="ethereum",
            creator="0x0987654321098765432109876543210987654321",
            creation_tx="0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
            creation_timestamp=1633046400,  # Unix timestamp
            verified=True,
            name="TestToken",
            bytecode="0x60806040...",
            abi=[{"type": "function", "name": "transfer", "inputs": []}],
            source_code="pragma solidity ^0.8.0;",
            risk_score=15.0,
            vulnerabilities=[{"name": "reentrancy", "severity": "high"}]
        )
        
        assert contract.address == "0x1234567890123456789012345678901234567890"
        assert contract.chain == "ethereum"
        assert contract.creator == "0x0987654321098765432109876543210987654321"
        assert contract.creation_tx == "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
        assert isinstance(contract.creation_timestamp, datetime)  # Should be converted to datetime
        assert contract.verified is True
        assert contract.name == "TestToken"
        assert contract.bytecode == "0x60806040..."
        assert len(contract.abi) == 1
        assert contract.abi[0]["name"] == "transfer"
        assert contract.source_code == "pragma solidity ^0.8.0;"
        assert contract.risk_score == 15.0
        assert len(contract.vulnerabilities) == 1
        assert contract.vulnerabilities[0]["name"] == "reentrancy"

    def test_contract_timestamp_conversion(self):
        """Test timestamp conversion in contract model."""
        # Test with integer timestamp
        contract = Contract(
            address="0x1234567890123456789012345678901234567890",
            chain="ethereum",
            creation_timestamp=1633046400  # Unix timestamp
        )
        assert isinstance(contract.creation_timestamp, datetime)
        
        # Test with datetime object
        now = datetime.now()
        contract = Contract(
            address="0x1234567890123456789012345678901234567890",
            chain="ethereum",
            creation_timestamp=now
        )
        assert contract.creation_timestamp == now

    def test_contract_to_arangodb_document(self):
        """Test the to_arangodb_document method."""
        contract = Contract(
            address="0x1234567890123456789012345678901234567890",
            chain="ethereum",
            creation_timestamp=1633046400,  # Unix timestamp
            verified=True,
            name="TestToken"
        )
        
        doc = contract.to_arangodb_document()
        
        # Check ArangoDB specific fields
        assert "_key" in doc
        assert doc["_key"] == "ethereum_1234567890123456789012345678901234567890"
        
        # Check timestamp conversion
        assert isinstance(doc["creation_timestamp"], str)
        
        # Check other fields
        assert doc["address"] == "0x1234567890123456789012345678901234567890"
        assert doc["chain"] == "ethereum"
        assert doc["verified"] is True
        assert doc["name"] == "TestToken"


class TestEventModel:
    """Test suite for the Event model."""

    def test_event_basic(self):
        """Test basic event creation and validation."""
        event = Event(
            chain="ethereum",
            contract_address="0x1234567890123456789012345678901234567890",
            tx_hash="0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
            block_number=12345678,
            log_index=0,
            timestamp=1633046400,  # Unix timestamp
            name="Transfer",
            signature="Transfer(address,address,uint256)",
            params={
                "from": "0x0000000000000000000000000000000000000000",
                "to": "0x0987654321098765432109876543210987654321",
                "value": "1000000000000000000"
            }
        )
        
        assert event.chain == "ethereum"
        assert event.contract_address == "0x1234567890123456789012345678901234567890"
        assert event.tx_hash == "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
        assert event.block_number == 12345678
        assert event.log_index == 0
        assert isinstance(event.timestamp, datetime)  # Should be converted to datetime
        assert event.name == "Transfer"
        assert event.signature == "Transfer(address,address,uint256)"
        assert event.params["from"] == "0x0000000000000000000000000000000000000000"
        assert event.params["to"] == "0x0987654321098765432109876543210987654321"
        assert event.params["value"] == "1000000000000000000"

    def test_event_timestamp_conversion(self):
        """Test timestamp conversion in event model."""
        # Test with integer timestamp
        event = Event(
            chain="ethereum",
            contract_address="0x1234567890123456789012345678901234567890",
            tx_hash="0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
            block_number=12345678,
            log_index=0,
            timestamp=1633046400  # Unix timestamp
        )
        assert isinstance(event.timestamp, datetime)
        
        # Test with datetime object
        now = datetime.now()
        event = Event(
            chain="ethereum",
            contract_address="0x1234567890123456789012345678901234567890",
            tx_hash="0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
            block_number=12345678,
            log_index=0,
            timestamp=now
        )
        assert event.timestamp == now

    def test_event_to_arangodb_document(self):
        """Test the to_arangodb_document method."""
        event = Event(
            chain="ethereum",
            contract_address="0x1234567890123456789012345678901234567890",
            tx_hash="0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
            block_number=12345678,
            log_index=3,
            timestamp=1633046400,  # Unix timestamp
            name="Transfer"
        )
        
        doc = event.to_arangodb_document()
        
        # Check ArangoDB specific fields
        assert "_key" in doc
        assert doc["_key"] == "ethereum_abcdef1234567890abcdef1234567890abcdef1234567890abcdef12345678903"
        
        # Check timestamp conversion
        assert isinstance(doc["timestamp"], str)
        
        # Check other fields
        assert doc["chain"] == "ethereum"
        assert doc["contract_address"] == "0x1234567890123456789012345678901234567890"
        assert doc["tx_hash"] == "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
        assert doc["block_number"] == 12345678
        assert doc["log_index"] == 3
        assert doc["name"] == "Transfer"