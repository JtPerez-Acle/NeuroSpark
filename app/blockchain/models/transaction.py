"""Transaction models for blockchain transactions."""
from datetime import datetime
from typing import Optional, Dict, Any, List, Union, Literal
from pydantic import BaseModel, Field, field_validator


class Transaction(BaseModel):
    """Base transaction model for blockchain transactions."""
    
    hash: str = Field(..., description="Transaction hash/identifier")
    chain: str = Field(..., description="Blockchain identifier (ethereum, solana, etc.)")
    block_number: int = Field(..., description="Block containing the transaction")
    timestamp: Union[int, datetime] = Field(..., description="Transaction timestamp")
    from_address: str = Field(..., description="Sender address")
    to_address: Optional[str] = Field(None, description="Recipient address")
    value: int = Field(0, description="Transaction amount in smallest units (wei, lamports, etc.)")
    status: str = Field("pending", description="Transaction status")
    gas_used: Optional[int] = Field(None, description="Gas consumed by the transaction")
    gas_price: Optional[int] = Field(None, description="Gas price")
    input_data: Optional[str] = Field(None, description="Transaction input data")
    risk_score: Optional[float] = Field(None, description="Calculated risk assessment (0-100)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional chain-specific data")
    
    @field_validator('timestamp', mode='before')
    @classmethod
    def parse_timestamp(cls, v):
        """Convert timestamp to datetime if it's an integer."""
        if isinstance(v, int):
            return datetime.fromtimestamp(v)
        return v
    
    def to_arangodb_document(self) -> Dict[str, Any]:
        """Convert transaction to ArangoDB document format.
        
        Returns:
            Dictionary in ArangoDB format
        """
        doc = self.model_dump()
        
        # Clean the hash to remove 0x prefix if present
        clean_hash = self.hash.replace('0x', '')
        
        # Create a key from the transaction hash by removing any non-alphanumeric characters
        key = ''.join(c for c in clean_hash if c.isalnum()).lower()
        
        # Add ArangoDB fields
        doc['_key'] = f"{self.chain}_{key}"
        
        # Convert datetime objects to ISO format strings
        if isinstance(doc['timestamp'], datetime):
            doc['timestamp'] = doc['timestamp'].isoformat()
            
        return doc


class EthereumTransaction(Transaction):
    """Ethereum-specific transaction model."""
    
    chain: Literal["ethereum"] = Field("ethereum", description="Ethereum blockchain identifier")
    nonce: Optional[int] = Field(None, description="Transaction nonce")
    gas_limit: Optional[int] = Field(None, description="Gas limit for the transaction")
    transaction_index: Optional[int] = Field(None, description="Index in the block")
    is_contract_creation: bool = Field(False, description="Whether this transaction created a contract")
    logs: List[Dict[str, Any]] = Field(default_factory=list, description="Event logs emitted by the transaction")
    
    @classmethod
    def from_web3_transaction(cls, tx_data: Dict[str, Any], receipt_data: Optional[Dict[str, Any]] = None) -> 'EthereumTransaction':
        """Create an EthereumTransaction from Web3.py transaction data.
        
        Args:
            tx_data: Transaction data from Web3.py
            receipt_data: Optional transaction receipt data
            
        Returns:
            EthereumTransaction instance
        """
        # Default status if receipt not available
        status = "pending"
        gas_used = None
        logs = []
        
        # Update fields from receipt if available
        if receipt_data:
            status = "success" if receipt_data.get('status') == 1 else "failed"
            gas_used = receipt_data.get('gasUsed')
            logs = receipt_data.get('logs', [])
        
        # Determine if contract creation
        is_contract_creation = tx_data.get('to') is None
        
        return cls(
            hash=tx_data.get('hash', ''),
            block_number=tx_data.get('blockNumber', 0),
            timestamp=tx_data.get('timestamp', datetime.now()),
            from_address=tx_data.get('from', ''),
            to_address=tx_data.get('to'),
            value=tx_data.get('value', 0),
            status=status,
            gas_used=gas_used,
            gas_price=tx_data.get('gasPrice'),
            gas_limit=tx_data.get('gas'),
            input_data=tx_data.get('input'),
            nonce=tx_data.get('nonce'),
            transaction_index=tx_data.get('transactionIndex'),
            is_contract_creation=is_contract_creation,
            logs=logs
        )