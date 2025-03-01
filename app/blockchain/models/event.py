"""Event models for blockchain contract events."""
from datetime import datetime
from typing import Optional, Dict, Any, List, Union, Literal
from pydantic import BaseModel, Field, field_validator


class Event(BaseModel):
    """Base event model for blockchain contract events."""
    
    chain: str = Field(..., description="Blockchain identifier (ethereum, solana, etc.)")
    contract_address: str = Field(..., description="Contract address that emitted the event")
    tx_hash: str = Field(..., description="Transaction hash")
    block_number: int = Field(..., description="Block containing the event")
    log_index: int = Field(..., description="Index in the transaction logs")
    timestamp: Union[int, datetime] = Field(..., description="Event timestamp")
    name: Optional[str] = Field(None, description="Event name")
    signature: Optional[str] = Field(None, description="Event signature")
    params: Dict[str, Any] = Field(default_factory=dict, description="Event parameters")
    
    @field_validator('timestamp', mode='before')
    @classmethod
    def parse_timestamp(cls, v):
        """Convert timestamp to datetime if it's an integer."""
        if isinstance(v, int):
            return datetime.fromtimestamp(v)
        return v
    
    def to_arangodb_document(self) -> Dict[str, Any]:
        """Convert event to ArangoDB document format.
        
        Returns:
            Dictionary in ArangoDB format
        """
        doc = self.model_dump()
        
        # Create a key from tx_hash and log_index
        key = f"{self.tx_hash.replace('0x', '')}_{self.log_index}"
        key = ''.join(c for c in key if c.isalnum()).lower()
        
        # Add ArangoDB fields
        doc['_key'] = f"{self.chain}_{key}"
        
        # Convert datetime objects to ISO format strings
        if isinstance(doc['timestamp'], datetime):
            doc['timestamp'] = doc['timestamp'].isoformat()
            
        return doc


class EthereumEvent(Event):
    """Ethereum-specific event model."""
    
    chain: Literal["ethereum"] = Field("ethereum", description="Ethereum blockchain identifier")
    topic0: Optional[str] = Field(None, description="First topic (event signature)")
    topics: List[str] = Field(default_factory=list, description="Event topics")
    data: str = Field("0x", description="Raw event data")
    removed: bool = Field(False, description="Whether the event was removed due to chain reorg")
    
    @classmethod
    def from_web3_log(cls, log_data: Dict[str, Any], block_timestamp: Optional[int] = None) -> 'EthereumEvent':
        """Create an EthereumEvent from Web3.py log data.
        
        Args:
            log_data: Log data from Web3.py
            block_timestamp: Optional block timestamp
            
        Returns:
            EthereumEvent instance
        """
        # Extract topics
        topics = log_data.get('topics', [])
        topic0 = topics[0] if topics else None
        
        # Parse signature from topic0 if available
        signature = None
        name = None
        if topic0:
            # In a real implementation, we'd use a signature database or ABI to parse this
            # For now, we'll just use the first 10 chars as an example
            signature = topic0
            name = "Unknown"  # Would be resolved from ABI in real implementation
        
        # Parse parameters (simplified)
        params = {}
        # In a real implementation, this would decode parameters using the ABI
        
        return cls(
            contract_address=log_data.get('address', ''),
            tx_hash=log_data.get('transactionHash', ''),
            block_number=log_data.get('blockNumber', 0),
            log_index=log_data.get('logIndex', 0),
            timestamp=block_timestamp or datetime.now().timestamp(),
            name=name,
            signature=signature,
            params=params,
            topic0=topic0,
            topics=topics,
            data=log_data.get('data', '0x'),
            removed=log_data.get('removed', False)
        )