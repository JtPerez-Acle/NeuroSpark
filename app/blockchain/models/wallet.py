"""Wallet model for blockchain accounts."""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, field_validator


class Wallet(BaseModel):
    """Base wallet model for blockchain addresses."""
    
    address: str = Field(..., description="Wallet address")
    chain: str = Field(..., description="Blockchain identifier (ethereum, solana, etc.)")
    balance: float = Field(0.0, description="Current wallet balance")
    first_seen: Optional[datetime] = Field(None, description="Timestamp of first activity")
    last_active: Optional[datetime] = Field(None, description="Timestamp of latest activity")
    type: str = Field("EOA", description="Wallet type (EOA, contract, etc.)")
    tags: List[str] = Field(default_factory=list, description="Labels or categories")
    risk_score: float = Field(0.0, description="Calculated risk assessment (0-100)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional chain-specific data")
    
    @field_validator('risk_score')
    @classmethod
    def validate_risk_score(cls, v):
        """Ensure risk score is between 0 and 100."""
        if v < 0 or v > 100:
            raise ValueError("Risk score must be between 0 and 100")
        return v
    
    def to_arangodb_document(self) -> Dict[str, Any]:
        """Convert wallet to ArangoDB document format.
        
        Returns:
            Dictionary in ArangoDB format
        """
        doc = self.model_dump()
        
        # Create a key by removing '0x' from Ethereum addresses and any non-alphanumeric characters
        key = self.address.replace('0x', '')
        key = ''.join(c for c in key if c.isalnum()).lower()
        
        # Add ArangoDB fields
        doc['_key'] = f"{self.chain}_{key}"
        
        # Convert datetime objects to ISO format strings
        if self.first_seen:
            doc['first_seen'] = self.first_seen.isoformat()
        if self.last_active:
            doc['last_active'] = self.last_active.isoformat()
            
        return doc