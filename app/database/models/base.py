"""Base models for Neo4j database operations."""
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import json

class Neo4jModel:
    """Base class for Neo4j models."""
    
    def __init__(self, **kwargs):
        """Initialize Neo4j model."""
        pass
        
    @staticmethod
    def serialize_content(content: Any) -> str:
        """Serialize complex content to JSON string."""
        if isinstance(content, (dict, list)):
            return json.dumps(content)
        return str(content)

    @staticmethod
    def get_timestamp() -> str:
        """Get current timestamp in ISO format."""
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def prepare_props(data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare properties for Neo4j storage."""
        props = {}
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                props[key] = Neo4jModel.serialize_content(value)
            else:
                props[key] = value
        return props
