"""Legacy operations for backward compatibility with agent-based model."""
import logging
from typing import Dict, List, Any, Optional

from arango.database import StandardDatabase
from arango.exceptions import DocumentGetError, DocumentInsertError

from .base import BaseOperations

logger = logging.getLogger(__name__)

class LegacyOperations(BaseOperations):
    """Legacy operations for backward compatibility."""
    
    def create_indexes(self) -> None:
        """Create indexes for legacy collections."""
        # Index on agent id
        if 'agents' in self._db.collections():
            self._db.collection('agents').add_hash_index(['id'], unique=True)
        
        # Index on run id
        if 'runs' in self._db.collections():
            self._db.collection('runs').add_hash_index(['id'], unique=True)
        
        # Indexes on interaction fields
        if 'interactions' in self._db.collections():
            edge_collection = self._db.collection('interactions')
            edge_collection.add_hash_index(['sender_id', 'receiver_id'], unique=False)
            edge_collection.add_hash_index(['timestamp'], unique=False)
            edge_collection.add_hash_index(['run_id'], unique=False)
    
    async def store_run(self, run: Dict[str, Any]) -> None:
        """Store a run in the database.
        
        Args:
            run: Dictionary containing run data
        """
        # Prepare run document
        run_doc = run.copy()
        
        # Create runs collection if it doesn't exist
        if not self._db.has_collection('runs'):
            self._db.create_collection('runs')
            self.create_indexes()
        
        # Get runs collection
        runs_collection = self._db.collection('runs')
        
        try:
            # Check if run exists by id
            key = run_doc['id']
            if self._document_exists(runs_collection, key):
                # Update existing run
                runs_collection.update({'_key': key}, run_doc)
            else:
                # Insert new run with id as key
                run_doc['_key'] = key
                runs_collection.insert(run_doc)
        except DocumentInsertError as e:
            logger.error(f"Error storing run: {e}")
            raise
    
    async def get_runs(self, agent_id: str = None) -> List[Dict[str, Any]]:
        """Get runs from the database.
        
        Args:
            agent_id: Optional agent ID to filter runs
            
        Returns:
            List of run dictionaries
        """
        # Ensure the collection exists
        if not self._db.has_collection('runs'):
            return []
        
        if agent_id:
            # Ensure the participation collection exists
            if not self._db.has_collection('participations'):
                return []
                
            # Get runs for specific agent using participations
            query = """
            FOR p IN participations
                FILTER p._from == CONCAT('agents/', @agent_id)
                LET run = DOCUMENT(p._to)
                COLLECT run_doc = run WITH COUNT INTO count
                RETURN UNSET(run_doc, '_id', '_key', '_rev')
            """
            cursor = self._db.aql.execute(query, bind_vars={'agent_id': agent_id})
        else:
            # Get all runs
            query = """
            FOR run IN runs
                RETURN UNSET(run, '_id', '_key', '_rev')
            """
            cursor = self._db.aql.execute(query)
        
        return [doc for doc in cursor]