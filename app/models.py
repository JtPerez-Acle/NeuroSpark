"""Models for the KQML Parser Backend."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class KQMLMessageModel(BaseModel):
    """Model for KQML messages."""
    sender: str = Field(..., description="Message sender")
    receiver: str = Field(..., description="Message receiver")
    performative: str = Field(..., description="Message performative")
    content: str = Field(..., description="Message content")

class GraphNode(BaseModel):
    """Model for graph nodes."""
    id: str = Field(..., description="Node ID")
    labels: List[str] = Field(..., description="Node labels")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Node properties")

class GraphRelationship(BaseModel):
    """Model for graph relationships."""
    id: str = Field(..., description="Relationship ID")
    type: str = Field(..., description="Relationship type")
    start_node: str = Field(..., description="Start node ID")
    end_node: str = Field(..., description="End node ID")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Relationship properties")

class GraphData(BaseModel):
    """Model for graph data."""
    nodes: List[GraphNode] = Field(default_factory=list, description="List of nodes")
    relationships: List[GraphRelationship] = Field(default_factory=list, description="List of relationships")

class SyntheticDataParams(BaseModel):
    """Parameters for synthetic data generation."""
    numAgents: int = Field(gt=0, description="Number of agents to generate")
    numInteractions: int = Field(gt=0, description="Number of interactions to generate")

class RunData(BaseModel):
    """Run data model."""
    run_id: str = Field(..., description="Unique identifier for the run")
    timestamp: str = Field(..., description="ISO format timestamp of the run")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata for the run")

class InteractionData(BaseModel):
    """Interaction data model."""
    performative: str = Field(..., description="KQML performative")
    content: str = Field(..., description="Content of the message")
    sender: str = Field(..., description="ID of the sending agent")
    receiver: str = Field(..., description="ID of the receiving agent")
    timestamp: str = Field(..., description="ISO format timestamp of the interaction")
    run_id: Optional[str] = Field(default=None, description="ID of the associated run")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata for the interaction")

class GraphQuery(BaseModel):
    """Model for advanced graph queries."""
    id: Optional[str] = Field(None, description="Filter by node/relationship ID")
    nodeTypes: Optional[List[str]] = Field(None, description="Filter by node types")
    relationshipTypes: Optional[List[str]] = Field(None, description="Filter by relationship types")
    timeRange: Optional[Dict[str, datetime]] = Field(None, description="Filter by time range")
    agents: Optional[List[str]] = Field(None, description="Filter by agent IDs")
    runs: Optional[List[str]] = Field(None, description="Filter by run IDs")
    limit: Optional[int] = Field(default=100, description="Maximum number of results to return")

    def get(self, key: str, default: Any = None) -> Any:
        """Get a field value by key."""
        return getattr(self, key, default)
