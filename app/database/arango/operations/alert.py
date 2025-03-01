"""Alert operations for ArangoDB."""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from uuid import uuid4

from arango.database import StandardDatabase
from arango.exceptions import DocumentGetError, DocumentInsertError

from .base import BaseOperations

logger = logging.getLogger(__name__)

class AlertOperations(BaseOperations):
    """Alert operations for ArangoDB."""
    
    def create_indexes(self) -> None:
        """Create indexes for alert collection."""
        if 'alerts' in self._db.collections():
            self._db.collection('alerts').add_hash_index(['entity'], unique=False)
            self._db.collection('alerts').add_hash_index(['type'], unique=False)
            self._db.collection('alerts').add_hash_index(['severity'], unique=False)
            self._db.collection('alerts').add_hash_index(['timestamp'], unique=False)
            self._db.collection('alerts').add_hash_index(['status'], unique=False)
        
        if 'entity_to_alert' in self._db.collections():
            self._db.collection('entity_to_alert').add_hash_index(['timestamp'], unique=False)
            self._db.collection('entity_to_alert').add_hash_index(['alert_type'], unique=False)
            self._db.collection('entity_to_alert').add_hash_index(['severity'], unique=False)
    
    async def store_alert(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Store an alert in the database.
        
        Args:
            alert_data: Dictionary containing alert data
            
        Returns:
            The stored alert document
        """
        # Check if alerts collection exists, create if not
        if not self._db.has_collection('alerts'):
            self._db.create_collection('alerts')
            self.create_indexes()
        
        # Get alerts collection
        alerts_collection = self._db.collection('alerts')
        
        try:
            # Try to get the key from the document
            key = alert_data.get('_key')
            if not key:
                # Create a key using UUID 
                key = str(uuid4()).replace('-', '')
                alert_data['_key'] = key
            
            logger.info(f"Storing alert with key: {key}")
            
            # Check if alert exists, update or insert
            if self._document_exists(alerts_collection, key):
                alerts_collection.update(key, alert_data)
                logger.info(f"Updated existing alert: {key}")
            else:
                alerts_collection.insert(alert_data)
                logger.info(f"Inserted new alert: {key}")
                
            # If we have entity information, link entity to alert
            entity = alert_data.get('entity')
            entity_type = alert_data.get('entity_type')
            
            if entity and entity_type:
                # Determine collection based on entity type
                from_collection = None
                if entity_type == 'wallet':
                    from_collection = 'wallets'
                elif entity_type == 'contract':
                    from_collection = 'contracts'
                elif entity_type == 'transaction':
                    from_collection = 'transactions'
                
                if from_collection:
                    # Create entity_to_alert edge collection if it doesn't exist
                    if not self._db.has_collection('entity_to_alert'):
                        self._db.create_collection('entity_to_alert', edge=True)
                        self._db.collection('entity_to_alert').add_hash_index(['timestamp'], unique=False)
                        self._db.collection('entity_to_alert').add_hash_index(['alert_type'], unique=False)
                        self._db.collection('entity_to_alert').add_hash_index(['severity'], unique=False)
                    
                    # Create entity_to_alert edge
                    entity_to_alert = self._db.collection('entity_to_alert')
                    edge_key = f"{entity.replace('0x', '').lower()}_{key}"
                    
                    # Check if edge already exists
                    try:
                        if not self._document_exists(entity_to_alert, edge_key):
                            entity_to_alert.insert({
                                '_key': edge_key,
                                '_from': f'{from_collection}/{entity}',
                                '_to': f'alerts/{key}',
                                'timestamp': alert_data.get('timestamp'),
                                'alert_type': alert_data.get('type'),
                                'severity': alert_data.get('severity')
                            })
                            logger.info(f"Created entity_to_alert edge for alert: {key}")
                    except Exception as e:
                        logger.warning(f"Error creating entity_to_alert edge: {e}")
                
            return alert_data
        except Exception as e:
            logger.error(f"Error storing alert: {e}")
            logger.error(f"Alert data: {alert_data}")
            raise
    
    async def get_alerts(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get alerts from the database.
        
        Args:
            limit: Maximum number of alerts to return
            offset: Number of alerts to skip
            
        Returns:
            List of alert dictionaries
        """
        # Ensure the collection exists
        if not self._db.has_collection('alerts'):
            return []
        
        query = """
        FOR alert IN alerts
        SORT alert.timestamp DESC
        LIMIT @offset, @limit
        RETURN UNSET(alert, '_id', '_key', '_rev')
        """
        
        cursor = self._db.aql.execute(query, bind_vars={'limit': limit, 'offset': offset})
        return [doc for doc in cursor]
    
    async def get_active_alerts(self, 
                              severity: Optional[str] = None,
                              entity_type: Optional[str] = None,
                              alert_type: Optional[str] = None,
                              limit: int = 50) -> List[Dict[str, Any]]:
        """Get active security alerts from the database.
        
        Args:
            severity: Optional filter by severity level (low, medium, high, critical)
            entity_type: Optional filter by entity type (wallet, contract, transaction)
            alert_type: Optional filter by alert type
            limit: Maximum number of alerts to return
            
        Returns:
            List of active alert dictionaries
        """
        # Check if alerts collection exists
        if not self._db.has_collection('alerts'):
            logger.warning("Alerts collection does not exist")
            return []
        
        try:
            # Build query filters
            filters = ["a.status != 'resolved'"]
            bind_vars = {"limit": limit}
            
            if severity:
                filters.append("a.severity == @severity")
                bind_vars["severity"] = severity
            
            if entity_type:
                filters.append("a.entity_type == @entity_type")
                bind_vars["entity_type"] = entity_type
            
            if alert_type:
                filters.append("a.type == @alert_type")
                bind_vars["alert_type"] = alert_type
            
            # Query alerts
            query = f"""
            FOR a IN alerts
                FILTER {" AND ".join(filters)}
                SORT a.timestamp DESC
                LIMIT @limit
                RETURN UNSET(a, '_id', '_key', '_rev')
            """
            
            cursor = self._db.aql.execute(query, bind_vars=bind_vars)
            alerts = [doc for doc in cursor]
            
            return alerts
        except Exception as e:
            logger.error(f"Error getting active alerts: {e}")
            return []
    
    async def get_entity_alerts(self, entity: str, entity_type: str, 
                               limit: int = 20) -> List[Dict[str, Any]]:
        """Get alerts for a specific entity.
        
        Args:
            entity: Entity identifier (address, tx hash, etc.)
            entity_type: Type of entity (wallet, contract, transaction)
            limit: Maximum number of alerts to return
            
        Returns:
            List of alert dictionaries for the entity
        """
        # Check if alerts collection exists
        if not self._db.has_collection('alerts') or not self._db.has_collection('entity_to_alert'):
            logger.warning("Required collections do not exist")
            return []
        
        try:
            # Determine collection based on entity type
            from_collection = None
            if entity_type == 'wallet':
                from_collection = 'wallets'
            elif entity_type == 'contract':
                from_collection = 'contracts'
            elif entity_type == 'transaction':
                from_collection = 'transactions'
                
            if not from_collection:
                logger.warning(f"Unknown entity type: {entity_type}")
                return []
                
            # Normalize entity identifier
            normalized_entity = entity.replace('0x', '').lower()
            
            # Query using entity_to_alert edges
            query = """
            FOR edge IN entity_to_alert
                FILTER edge._from == @entity_id
                LET alert = DOCUMENT(edge._to)
                SORT edge.timestamp DESC
                LIMIT @limit
                RETURN UNSET(alert, '_id', '_key', '_rev')
            """
            
            bind_vars = {
                "entity_id": f"{from_collection}/{normalized_entity}",
                "limit": limit
            }
            
            cursor = self._db.aql.execute(query, bind_vars=bind_vars)
            alerts = [doc for doc in cursor]
            
            return alerts
        except Exception as e:
            logger.error(f"Error getting alerts for entity {entity}: {e}")
            return []