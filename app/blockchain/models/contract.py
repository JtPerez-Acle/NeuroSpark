"""Smart contract models for blockchain contracts."""
from datetime import datetime
from typing import Optional, Dict, Any, List, Union, Literal
from pydantic import BaseModel, Field, field_validator


class Contract(BaseModel):
    """Base contract model for blockchain smart contracts."""
    
    address: str = Field(..., description="Contract address")
    chain: str = Field(..., description="Blockchain identifier (ethereum, solana, etc.)")
    creator: Optional[str] = Field(None, description="Creator address")
    creation_tx: Optional[str] = Field(None, description="Creation transaction hash")
    creation_timestamp: Optional[Union[int, datetime]] = Field(None, description="Creation time")
    verified: bool = Field(False, description="Whether source code is verified")
    name: Optional[str] = Field(None, description="Contract name (if known)")
    bytecode: Optional[str] = Field(None, description="Contract bytecode")
    abi: Optional[List[Dict[str, Any]]] = Field(None, description="Contract ABI (if available)")
    source_code: Optional[str] = Field(None, description="Verified source code (if available)")
    risk_score: Optional[float] = Field(None, description="Calculated risk assessment (0-100)")
    vulnerabilities: List[Dict[str, Any]] = Field(default_factory=list, description="Detected vulnerabilities")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional contract metadata")
    
    @field_validator('creation_timestamp', mode='before')
    @classmethod
    def parse_timestamp(cls, v):
        """Convert timestamp to datetime if it's an integer."""
        if isinstance(v, int):
            return datetime.fromtimestamp(v)
        return v
    
    def to_arangodb_document(self) -> Dict[str, Any]:
        """Convert contract to ArangoDB document format.
        
        Returns:
            Dictionary in ArangoDB format
        """
        doc = self.model_dump()
        
        # Create a key from the contract address by removing any non-alphanumeric characters
        key = self.address.replace('0x', '')
        key = ''.join(c for c in key if c.isalnum()).lower()
        
        # Add ArangoDB fields
        doc['_key'] = f"{self.chain}_{key}"
        
        # Convert datetime objects to ISO format strings
        if isinstance(doc['creation_timestamp'], datetime):
            doc['creation_timestamp'] = doc['creation_timestamp'].isoformat()
            
        return doc


class EthereumContract(Contract):
    """Ethereum-specific contract model."""
    
    chain: Literal["ethereum"] = Field("ethereum", description="Ethereum blockchain identifier")
    implementation_address: Optional[str] = Field(None, description="Proxy implementation address (if a proxy)")
    is_proxy: bool = Field(False, description="Whether this contract is a proxy")
    solidity_version: Optional[str] = Field(None, description="Solidity compiler version")
    constructor_arguments: Optional[str] = Field(None, description="Constructor arguments")
    optimization_used: Optional[bool] = Field(None, description="Whether optimization was used")
    
    @classmethod
    def from_etherscan_data(cls, address: str, contract_data: Dict[str, Any]) -> 'EthereumContract':
        """Create an EthereumContract from Etherscan API data.
        
        Args:
            address: Contract address
            contract_data: Contract data from Etherscan API
            
        Returns:
            EthereumContract instance
        """
        # Extract contract ABI if available
        abi = None
        if contract_data.get('ABI') and contract_data['ABI'] != 'Contract source code not verified':
            import json
            try:
                abi = json.loads(contract_data['ABI'])
            except (json.JSONDecodeError, TypeError):
                pass
        
        # Extract contract creation details
        creation_tx = None
        creation_timestamp = None
        if contract_data.get('contractCreation'):
            creation_tx = contract_data['contractCreation'].get('txHash')
            if contract_data['contractCreation'].get('timestamp'):
                creation_timestamp = int(contract_data['contractCreation']['timestamp'])
        
        # Check for proxy implementation
        is_proxy = False
        implementation_address = None
        if contract_data.get('implementation'):
            is_proxy = True
            implementation_address = contract_data['implementation']
        
        return cls(
            address=address,
            creator=contract_data.get('contractCreator', {}).get('address'),
            creation_tx=creation_tx,
            creation_timestamp=creation_timestamp,
            verified=contract_data.get('isVerified', False),
            name=contract_data.get('contractName'),
            bytecode=contract_data.get('bytecode'),
            abi=abi,
            source_code=contract_data.get('sourceCode'),
            solidity_version=contract_data.get('compiler', {}).get('version'),
            constructor_arguments=contract_data.get('constructorArguments'),
            optimization_used=contract_data.get('compiler', {}).get('optimizationUsed', False),
            is_proxy=is_proxy,
            implementation_address=implementation_address
        )