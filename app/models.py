"""Data models for the KQML Parser Backend."""
from datetime import datetime
from typing import Dict, Any, List, Optional
import re
from pydantic import BaseModel, Field, validator

class KQMLMessageModel(BaseModel):
    """Model for KQML messages."""
    performative: str = Field(..., description="KQML performative")
    agent_id: str = Field(..., description="ID of the agent sending the message")
    content: Dict[str, Any] = Field(..., description="Content of the message")
    language: Optional[str] = Field(default="KQML", description="Message language")
    ontology: Optional[str] = Field(default=None, description="Message ontology")

    @classmethod
    def from_string(cls, kqml_str: str) -> "KQMLMessageModel":
        """Create a KQMLMessageModel from a KQML string."""
        # Extract performative
        perf_match = re.match(r'\s*\(\s*(\w+)', kqml_str)
        if not perf_match:
            raise ValueError("Invalid KQML message: no performative found")
        performative = perf_match.group(1)

        # Extract content using basic pattern matching
        content_match = re.search(r':content\s+(\{[^}]+\}|\([^)]+\)|\S+)', kqml_str)
        content = {} if not content_match else eval(content_match.group(1))

        # Extract agent ID (sender)
        agent_match = re.search(r':sender\s+(\S+)', kqml_str)
        agent_id = agent_match.group(1) if agent_match else "unknown"

        # Extract optional fields
        language_match = re.search(r':language\s+(\S+)', kqml_str)
        language = language_match.group(1) if language_match else "KQML"

        ontology_match = re.search(r':ontology\s+(\S+)', kqml_str)
        ontology = ontology_match.group(1) if ontology_match else None

        return cls(
            performative=performative,
            agent_id=agent_id,
            content=content,
            language=language,
            ontology=ontology
        )
        
    @classmethod
    def valid_performatives(cls) -> List[str]:
        """Get list of valid KQML performatives."""
        return [
            "achieve", "advertise", "ask-about", "ask-all", "ask-if", "ask-one",
            "break", "broadcast", "broker-all", "broker-one", "deny", "discard",
            "error", "evaluate", "forward", "generator", "insert", "monitor",
            "next", "pipe", "ready", "recommend-all", "recommend-one", "recruit-all",
            "recruit-one", "register", "reply", "rest", "sorry", "stream-about",
            "stream-all", "subscribe", "tell", "transport-address", "unregister",
            "untell", "wait"
        ]
        
    @validator('performative')
    def validate_performative(cls, value):
        """Validate performative is a known KQML performative."""
        if value not in cls.valid_performatives():
            raise ValueError(f"Invalid performative: {value}. Must be one of: {', '.join(cls.valid_performatives())}")
        return value
        
    @validator('agent_id')
    def validate_agent_id(cls, value):
        """Validate agent ID is not empty."""
        if not value or not value.strip():
            raise ValueError("Agent ID cannot be empty")
        return value.strip()
        
    @validator('content')
    def validate_content(cls, value):
        """Validate content is not empty."""
        if not value:
            raise ValueError("Content cannot be empty")
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
