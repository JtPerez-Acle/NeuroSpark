"""Data models for the KQML Parser Backend."""
from datetime import datetime
from typing import Dict, Any, List, Optional
import re
import uuid
from pydantic import BaseModel, Field, validator

class AgentInteraction(BaseModel):
    """Model for agent interactions."""
    interaction_id: str = Field(default_factory=lambda: str(uuid.uuid4()).replace('-', '_'), description="Unique identifier for the interaction")
    timestamp: datetime = Field(default_factory=datetime.now, description="When the interaction occurred")
    sender_id: str = Field(..., description="ID of the sending agent")
    receiver_id: str = Field(..., description="ID of the receiving agent")
    
    # Content fields
    topic: str = Field(..., description="Main subject/topic of the interaction")
    message: str = Field(..., description="Actual content of the message")
    
    # Contextual fields
    run_id: Optional[str] = Field(None, description="ID of the simulation/experiment run")
    interaction_type: str = Field(default="message", description="Type of interaction (message, query, response, etc)")
    
    # Metrics/Analysis fields
    sentiment: Optional[float] = Field(None, description="Sentiment score of the interaction (-1 to 1)")
    priority: Optional[int] = Field(None, description="Priority level of the message (1-5)")
    duration_ms: Optional[int] = Field(None, description="Processing time in milliseconds")
    
    # Extensibility
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional custom metadata")
    
    @classmethod
    def interaction_types(cls) -> List[str]:
        """Get list of valid interaction types."""
        return [
            "message", "query", "response", "notification", "request", 
            "broadcast", "alert", "command", "report", "update"
        ]
    
    @validator('sender_id', 'receiver_id')
    def validate_agent_id(cls, value):
        """Validate agent ID is not empty."""
        if not value or not value.strip():
            raise ValueError("Agent ID cannot be empty")
        return value.strip()
    
    @validator('topic', 'message')
    def validate_content(cls, value):
        """Validate content is not empty."""
        if not value or not value.strip():
            raise ValueError("Field cannot be empty")
        return value.strip()
    
    @validator('interaction_type')
    def validate_interaction_type(cls, value):
        """Validate interaction type is valid."""
        if value not in cls.interaction_types():
            raise ValueError(f"Invalid interaction type: {value}. Must be one of: {', '.join(cls.interaction_types())}")
        return value
    
    @validator('priority')
    def validate_priority(cls, value):
        """Validate priority is in range 1-5."""
        if value is not None and (value < 1 or value > 5):
            raise ValueError("Priority must be between 1 and 5")
        return value
    
    @validator('sentiment')
    def validate_sentiment(cls, value):
        """Validate sentiment is in range -1 to 1."""
        if value is not None and (value < -1 or value > 1):
            raise ValueError("Sentiment must be between -1 and 1")
        return value

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

class GraphQuery(BaseModel):
    """Model for graph queries."""
    node_type: str
    relationship_type: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    agent_ids: Optional[List[str]] = None
    limit: Optional[int] = None
    include_properties: Optional[bool] = True

class SyntheticDataParams(BaseModel):
    """Model for synthetic data generation parameters."""
    numAgents: int = Field(gt=0, description="Number of agents to generate")
    numInteractions: int = Field(gt=0, description="Number of interactions to generate")

class ScenarioParams(BaseModel):
    """Model for scenario-based data generation parameters."""
    scenario: str = Field(..., description="Scenario type (pd, predator_prey, pursuer_evader, search_rescue)")
    numAgents: int = Field(gt=0, description="Number of agents to generate")
    numInteractions: int = Field(gt=0, description="Number of interactions to generate")
    rounds: Optional[int] = Field(None, description="Number of rounds/time steps (scenario-specific)")
    
    @validator('scenario')
    def validate_scenario(cls, value):
        """Validate scenario type."""
        valid_scenarios = ["pd", "predator_prey", "pursuer_evader", "search_rescue"]
        if value not in valid_scenarios:
            raise ValueError(f"Invalid scenario: {value}. Must be one of: {', '.join(valid_scenarios)}")
        return value

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
