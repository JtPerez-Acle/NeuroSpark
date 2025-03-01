"""Core database operations for ArangoDB."""
import logging
from typing import Dict, List, Any, Optional

from arango.database import StandardDatabase
from arango.exceptions import DocumentGetError, DocumentInsertError

logger = logging.getLogger(__name__)

class BaseOperations:
    """Base operations for ArangoDB."""
    
    def __init__(self, db: StandardDatabase):
        """Initialize base operations.
        
        Args:
            db: ArangoDB database instance
        """
        self._db = db
    
    def _document_exists(self, collection, key: str) -> bool:
        """Check if a document exists in a collection.
        
        Args:
            collection: Collection to check
            key: Document key
            
        Returns:
            True if document exists, False otherwise
        """
        try:
            logger.info(f"Checking if document with key '{key}' exists in collection")
            
            # Handle None keys
            if key is None:
                logger.warning("None key provided to _document_exists")
                return False
                
            # Make sure the key doesn't have dashes
            safe_key = key.replace('-', '_')
            result = collection.has({'_key': safe_key})
            logger.info(f"Document exists: {result}")
            return result
        except Exception as e:
            logger.error(f"Error checking if document exists: {e}")
            return False
            
    def create_indexes(self) -> None:
        """Create indexes for collections."""
        raise NotImplementedError("Subclasses must implement create_indexes")