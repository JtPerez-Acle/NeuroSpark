"""Event operations for ArangoDB."""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from arango.database import StandardDatabase
from arango.exceptions import DocumentGetError, DocumentInsertError

from .base import BaseOperations

logger = logging.getLogger(__name__)

class EventOperations(BaseOperations):
    """Event operations for ArangoDB."""
    
    def create_indexes(self) -> None:
        """Create indexes for event collection."""
        if 'events' in self._db.collections():
            self._db.collection('events').add_hash_index(['tx_hash', 'log_index', 'chain'], unique=True)
            self._db.collection('events').add_hash_index(['contract_address'], unique=False)
            self._db.collection('events').add_hash_index(['name'], unique=False)
            self._db.collection('events').add_hash_index(['block_number'], unique=False)
            self._db.collection('events').add_hash_index(['timestamp'], unique=False)
    
    async def store_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Store an event in the database.
        
        Args:
            event_data: Dictionary containing event data
            
        Returns:
            The stored event document
        """
        # Check if events collection exists, create if not
        if not self._db.has_collection('events'):
            self._db.create_collection('events')
            self.create_indexes()
        
        # Get events collection
        events_collection = self._db.collection('events')
        
        try:
            # Try to get the key from the document
            key = event_data.get('_key')
            if not key:
                # Create a key from the tx hash, log index, and chain
                tx_hash = event_data.get('tx_hash', '').replace('0x', '')
                log_index = event_data.get('log_index', 0)
                chain = event_data.get('chain', 'ethereum')
                key = f"{chain}_{tx_hash.lower()}_{log_index}"
                event_data['_key'] = key
            
            logger.info(f"Storing event with key: {key}")
            
            # Check if event exists, update or insert
            if self._document_exists(events_collection, key):
                events_collection.update(key, event_data)
                logger.info(f"Updated existing event: {key}")
            else:
                events_collection.insert(event_data)
                logger.info(f"Inserted new event: {key}")
                
            return event_data
        except Exception as e:
            logger.error(f"Error storing event: {e}")
            logger.error(f"Event data: {event_data}")
            raise
    
    async def get_events(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get events from the database.
        
        Args:
            limit: Maximum number of events to return
            offset: Number of events to skip
            
        Returns:
            List of event dictionaries
        """
        # Ensure the collection exists
        if not self._db.has_collection('events'):
            return []
        
        query = """
        FOR event IN events
        SORT event.timestamp DESC
        LIMIT @offset, @limit
        RETURN UNSET(event, '_id', '_key', '_rev')
        """
        
        cursor = self._db.aql.execute(query, bind_vars={'limit': limit, 'offset': offset})
        return [doc for doc in cursor]
    
    async def get_contract_events(self, contract_address: str, chain: str = "ethereum",
                               event_name: Optional[str] = None, 
                               from_block: Optional[int] = None,
                               to_block: Optional[int] = None,
                               limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get events for a contract.
        
        Args:
            contract_address: Contract address
            chain: Blockchain identifier
            event_name: Optional event name filter
            from_block: Optional starting block number
            to_block: Optional ending block number
            limit: Maximum number of events to return
            offset: Number of events to skip
            
        Returns:
            List of event dictionaries
        """
        # Check if events collection exists
        if not self._db.has_collection('events'):
            logger.warning("Events collection does not exist")
            return []
        
        try:
            # Build query based on filters
            bind_vars = {
                "contract_address": contract_address,
                "chain": chain,
                "offset": offset,
                "limit": limit
            }
            
            filters = ["e.contract_address == @contract_address", "e.chain == @chain"]
            
            if event_name:
                filters.append("e.name == @event_name")
                bind_vars["event_name"] = event_name
            
            if from_block is not None:
                filters.append("e.block_number >= @from_block")
                bind_vars["from_block"] = from_block
            
            if to_block is not None:
                filters.append("e.block_number <= @to_block")
                bind_vars["to_block"] = to_block
            
            query = f"""
            FOR e IN events
                FILTER {" AND ".join(filters)}
                SORT e.block_number DESC, e.log_index ASC
                LIMIT @offset, @limit
                RETURN UNSET(e, '_id', '_key', '_rev')
            """
            
            cursor = self._db.aql.execute(query, bind_vars=bind_vars)
            events = [doc for doc in cursor]
            
            return events
        except Exception as e:
            logger.error(f"Error getting contract events for {contract_address}: {e}")
            return []