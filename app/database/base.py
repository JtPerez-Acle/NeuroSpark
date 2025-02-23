"""Database interface module."""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional

class DatabaseInterface(ABC):
    """Abstract base class for database operations."""
    
    @abstractmethod
    async def connect(self) -> None:
        """Establish database connection."""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Close database connection."""
        pass
    
    @abstractmethod
    async def store_interaction(self, interaction_data: Dict[str, Any]) -> None:
        """Store an interaction in the database."""
        pass
    
    @abstractmethod
    async def get_all_nodes(self) -> List[Dict[str, Any]]:
        """Get all nodes in the graph."""
        pass
    
    @abstractmethod
    async def get_all_relationships(self) -> List[Dict[str, Any]]:
        """Get all relationships in the graph."""
        pass
    
    @abstractmethod
    async def query_nodes(self, query: Any) -> List[Dict[str, Any]]:
        """Query nodes with filters."""
        pass
    
    @abstractmethod
    async def query_relationships(self, query: Any) -> List[Dict[str, Any]]:
        """Query relationships with filters."""
        pass
    
    @abstractmethod
    async def clear_database(self) -> Dict[str, Any]:
        """Clear all data from the database."""
        pass
