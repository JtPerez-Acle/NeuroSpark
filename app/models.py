"""Data models for the Blockchain Intelligence System."""
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
import re
import uuid
from pydantic import BaseModel, Field, field_validator

class WalletModel(BaseModel):
    """Wallet Model."""
    address: str = Field(..., description="Blockchain address")
    chain: str = Field("ethereum", description="Blockchain identifier")
    type: str = Field(..., description="Wallet type (EOA, contract, etc.)")
    role: str = Field(..., description="Role of the wallet (trader, dex, etc.)")
    balance: float = Field(0.0, description="Current balance")
    first_seen: Optional[str] = Field(None, description="Timestamp of first activity")
    last_active: Optional[str] = Field(None, description="Timestamp of latest activity")
    risk_score: Optional[float] = Field(None, description="Risk assessment score (0-100)")
    tags: List[str] = Field(default_factory=list, description="Wallet tags/labels")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class TransactionModel(BaseModel):
    """Model for blockchain transactions."""
    hash: str = Field(..., description="Transaction hash")
    block_number: int = Field(..., description="Block containing the transaction")
    timestamp: str = Field(..., description="Transaction timestamp")
    from_address: str = Field(..., description="Sender address")
    to_address: Optional[str] = Field(None, description="Recipient address")
    value: float = Field(0.0, description="Transaction amount")
    gas_used: Optional[int] = Field(None, description="Gas consumed")
    gas_price: Optional[int] = Field(None, description="Gas price")
    status: str = Field("success", description="Transaction status")
    chain: str = Field("ethereum", description="Blockchain identifier")
    input_data: Optional[str] = Field(None, description="Transaction input data")
    risk_score: Optional[float] = Field(None, description="Risk assessment score (0-100)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    @field_validator('from_address', 'to_address')
    @classmethod
    def validate_address(cls, value):
        """Validate address if provided."""
        if value and not value.strip():
            raise ValueError("Address cannot be empty string if provided")
        return value
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, value):
        """Validate transaction status."""
        valid_statuses = ["success", "failed", "pending"]
        if value not in valid_statuses:
            raise ValueError(f"Invalid status: {value}. Must be one of: {', '.join(valid_statuses)}")
        return value
    
    @field_validator('risk_score')
    @classmethod
    def validate_risk_score(cls, value):
        """Validate risk score is in range 0-100."""
        if value is not None and (value < 0 or value > 100):
            raise ValueError("Risk score must be between 0 and 100")
        return value

class ContractModel(BaseModel):
    """Smart contract model."""
    address: str = Field(..., description="Contract address")
    chain: str = Field("ethereum", description="Blockchain identifier")
    creator: Optional[str] = Field(None, description="Creator address")
    creation_tx: Optional[str] = Field(None, description="Creation transaction hash")
    creation_timestamp: Optional[str] = Field(None, description="Creation time")
    verified: bool = Field(False, description="Whether source code is verified")
    name: Optional[str] = Field(None, description="Contract name")
    bytecode: Optional[str] = Field(None, description="Contract bytecode")
    abi: Optional[List[Dict[str, Any]]] = Field(None, description="Contract ABI")
    source_code: Optional[str] = Field(None, description="Verified source code")
    risk_score: Optional[float] = Field(None, description="Risk assessment score (0-100)")
    vulnerabilities: List[Dict[str, Any]] = Field(default_factory=list, description="Detected vulnerabilities")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class GraphNode(BaseModel):
    """Model for graph nodes."""
    id: str
    type: str
    properties: Optional[Dict[str, Any]] = Field(default_factory=dict)

class GraphRelationship(BaseModel):
    """Model for graph relationships."""
    source: str
    target: str
    type: str
    properties: Optional[Dict[str, Any]] = Field(default_factory=dict)

class GraphData(BaseModel):
    """Model for graph data."""
    nodes: List[Dict[str, Any]]
    links: List[Dict[str, Any]]  # Changed from relationships to links

class NodeAndEdges(BaseModel):
    """Model for nodes and edges in the graph."""
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]

class GraphQuery(BaseModel):
    """Model for blockchain graph queries."""
    node_type: str  # wallet or contract
    relationship_type: Optional[str] = None  # transaction, call, etc.
    start_time: Optional[str] = None  # Start of time range
    end_time: Optional[str] = None  # End of time range
    addresses: Optional[List[str]] = None  # List of blockchain addresses to query
    limit: Optional[int] = None  # Maximum results to return
    include_properties: Optional[bool] = True  # Include additional properties in results
    
class NaturalLanguageQuery(BaseModel):
    """Model for natural language queries."""
    query: str = Field(..., description="Natural language query to process")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context for the query")
    
class BlockchainNetwork(BaseModel):
    """Model for blockchain network data."""
    nodes: List[Dict[str, Any]]  # Wallets and contracts
    links: List[Dict[str, Any]]  # Transactions and events
    
class NetworkFilter(BaseModel):
    """Model for blockchain network filtering."""
    entity_types: Optional[List[str]] = Field(None, description="Types of blockchain entities to include (wallet, contract)")
    entity_roles: Optional[List[str]] = Field(None, description="Roles of entities to include (trader, dex, etc.)")
    transaction_types: Optional[List[str]] = Field(None, description="Types of transactions to include (transfer, swap, etc.)")
    time_range: Optional[List[str]] = Field(None, description="Time range [start, end] in ISO format")
    min_transactions: Optional[int] = Field(0, description="Minimum number of transactions")
    max_entities: Optional[int] = Field(100, description="Maximum number of blockchain entities to return")
    
class NetworkStats(BaseModel):
    """Model for blockchain network statistics."""
    num_entities: int  # Number of wallets and contracts
    num_transactions: int  # Number of blockchain transactions
    entity_types: Dict[str, int]  # Count by type (wallet, contract, etc.)
    transaction_types: Dict[str, int]  # Count by type (transfer, swap, etc.)
    average_transactions_per_entity: float
    top_entities: List[Dict[str, Any]]  # Most active wallets/contracts
    recent_activity: List[Dict[str, Any]]  # Recent blockchain transactions
    
class DatabaseOperation(BaseModel):
    """Model for database operations."""
    operation: str
    status: str
    timestamp: str
    details: Optional[Any] = None

class SyntheticDataParams(BaseModel):
    """Model for synthetic blockchain data generation parameters."""
    numWallets: int = Field(gt=0, description="Number of blockchain entities (wallets/contracts) to generate")
    numTransactions: int = Field(gt=0, description="Number of blockchain transactions to generate")

class ScenarioParams(BaseModel):
    """Model for blockchain scenario-based data generation parameters."""
    scenario: str = Field(..., description="Blockchain scenario type (dex, lending, nft, token_transfer)")
    numWallets: int = Field(gt=0, description="Number of wallets and contracts to generate")
    numTransactions: int = Field(gt=0, description="Number of blockchain transactions to generate")
    blocks: Optional[int] = Field(None, description="Number of blocks to simulate")
    
    @field_validator('scenario')
    @classmethod
    def validate_scenario(cls, value):
        """Validate scenario type."""
        valid_scenarios = ["dex", "lending", "nft", "token_transfer"]
        if value not in valid_scenarios:
            raise ValueError(f"Invalid scenario: {value}. Must be one of: {', '.join(valid_scenarios)}")
        return value

class RunData(BaseModel):
    """Run data model."""
    run_id: str = Field(..., description="Unique identifier for the run")
    timestamp: str = Field(..., description="ISO format timestamp of the run")
    scenario: Optional[str] = Field(None, description="Scenario type for this run")
    blockchain: Optional[str] = Field("ethereum", description="Blockchain for this run")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata for the run")

class TransactionData(BaseModel):
    """Blockchain transaction data model."""
    transaction_hash: Optional[str] = Field(None, description="Unique hash for the blockchain transaction")
    from_address: str = Field(..., description="Sender blockchain address")
    to_address: str = Field(..., description="Recipient blockchain address")
    chain: Optional[str] = Field("ethereum", description="Blockchain identifier")
    data: Optional[str] = Field(None, description="Transaction input data/calldata")
    timestamp: Optional[str] = Field(None, description="ISO format timestamp of the transaction")
    transaction_type: Optional[str] = Field(None, description="Type of transaction (transfer, swap, etc.)")
    block_number: Optional[int] = Field(None, description="Block containing the transaction")
    value: Optional[str] = Field(None, description="Transaction value in wei")
    gas_price: Optional[int] = Field(None, description="Gas price in wei")
    gas_used: Optional[int] = Field(None, description="Gas used by the transaction")
    status: Optional[str] = Field("success", description="Transaction status (success, failed, pending)")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
