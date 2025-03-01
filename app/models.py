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
    """Model for graph queries."""
    node_type: str
    relationship_type: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    agent_ids: Optional[List[str]] = None
    limit: Optional[int] = None
    include_properties: Optional[bool] = True
    
class NaturalLanguageQuery(BaseModel):
    """Model for natural language queries."""
    query: str = Field(..., description="Natural language query to process")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context for the query")
    
class NetworkAgents(BaseModel):
    """Model for network agent data."""
    nodes: List[Dict[str, Any]]
    links: List[Dict[str, Any]]
    
class NetworkFilter(BaseModel):
    """Model for network filtering."""
    agent_types: Optional[List[str]] = Field(None, description="Types of agents to include")
    agent_roles: Optional[List[str]] = Field(None, description="Roles of agents to include")
    interaction_types: Optional[List[str]] = Field(None, description="Types of interactions to include")
    time_range: Optional[List[str]] = Field(None, description="Time range [start, end] in ISO format")
    min_interactions: Optional[int] = Field(0, description="Minimum number of interactions")
    max_agents: Optional[int] = Field(100, description="Maximum number of agents to return")
    
class NetworkStats(BaseModel):
    """Model for network statistics."""
    num_agents: int
    num_interactions: int
    agent_types: Dict[str, int]
    interaction_types: Dict[str, int]
    average_interactions_per_agent: float
    top_agents: List[Dict[str, Any]]
    recent_activity: List[Dict[str, Any]]
    
class DatabaseOperation(BaseModel):
    """Model for database operations."""
    operation: str
    status: str
    timestamp: str
    details: Optional[Any] = None

class SyntheticDataParams(BaseModel):
    """Model for synthetic data generation parameters."""
    numAgents: int = Field(gt=0, description="Number of agents to generate")
    numInteractions: int = Field(gt=0, description="Number of interactions to generate")

class ScenarioParams(BaseModel):
    """Model for blockchain scenario-based data generation parameters."""
    scenario: str = Field(..., description="Blockchain scenario type (dex, lending, nft, token_transfer)")
    numAgents: int = Field(gt=0, description="Number of wallets and contracts to generate")
    numInteractions: int = Field(gt=0, description="Number of transactions to generate")
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

class InteractionData(BaseModel):
    """Interaction data model."""
    interaction_id: Optional[str] = Field(None, description="Unique identifier for the interaction")
    sender_id: str = Field(..., description="ID of the sending agent/wallet")
    receiver_id: str = Field(..., description="ID of the receiving agent/wallet")
    topic: Optional[str] = Field(None, description="Topic of the interaction")
    message: Optional[str] = Field(None, description="Message content")
    timestamp: Optional[str] = Field(None, description="ISO format timestamp of the interaction")
    interaction_type: Optional[str] = Field(None, description="Type of interaction (transfer, swap, etc.)")
    run_id: Optional[str] = Field(None, description="ID of the associated run")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
