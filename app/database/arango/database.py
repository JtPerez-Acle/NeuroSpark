"""ArangoDB database implementation."""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from arango.database import StandardDatabase
from arango.exceptions import DocumentGetError, DocumentInsertError

from ..base import DatabaseInterface
from .connection import ArangoConnection

logger = logging.getLogger(__name__)

class ArangoDatabase(DatabaseInterface):
    """ArangoDB database implementation."""
    
    def __init__(self, host: str, port: int, username: str, password: str, db_name: str):
        """Initialize the database.
        
        Args:
            host: ArangoDB host
            port: ArangoDB port
            username: Username
            password: Password
            db_name: Database name
        """
        self._connection = ArangoConnection(host, port, username, password, db_name)
        self._db = None
    
    async def connect(self) -> None:
        """Connect to the database."""
        await self._connection.connect()
        self._db = self._connection.get_database()
        
        # Ensure indexes exist for better performance
        self._create_indexes()
    
    def _create_indexes(self) -> None:
        """Create indexes for better query performance."""
        # Index on agent id
        self._db.collection('agents').add_hash_index(['id'], unique=True)
        
        # Index on run id
        self._db.collection('runs').add_hash_index(['id'], unique=True)
        
        # Indexes on interaction fields
        edge_collection = self._db.collection('interactions')
        edge_collection.add_hash_index(['sender_id', 'receiver_id'], unique=False)
        edge_collection.add_hash_index(['timestamp'], unique=False)
        edge_collection.add_hash_index(['run_id'], unique=False)
    
    async def disconnect(self) -> None:
        """Disconnect from the database."""
        await self._connection.disconnect()
        self._db = None
    
    def is_connected(self) -> bool:
        """Check if database is connected.
        
        Returns:
            True if connected, False otherwise
        """
        return self._db is not None
    
    async def store_agent(self, agent: Dict[str, Any]) -> None:
        """Store an agent in the database.
        
        Args:
            agent: Dictionary containing agent data
        """
        if not self.is_connected():
            await self.connect()
        
        # Prepare agent document
        agent_doc = agent.copy()
        
        # Ensure agent has a timestamp
        if 'timestamp' not in agent_doc:
            agent_doc['timestamp'] = datetime.now().isoformat()
        
        # Ensure agent ID is compatible with ArangoDB (no dashes)
        if 'id' in agent_doc:
            agent_doc['id'] = agent_doc['id'].replace('-', '_')
        
        # Get agents collection
        agents_collection = self._db.collection('agents')
        
        try:
            # Check if agent exists by id
            key = agent_doc['id']
            logger.info(f"Storing agent with key: {key}")
            
            if self._document_exists(agents_collection, key):
                logger.info(f"Updating existing agent: {key}")
                # Update existing agent
                agents_collection.update({'_key': key}, agent_doc)
            else:
                logger.info(f"Inserting new agent: {key}")
                # Insert new agent with id as key
                agent_doc['_key'] = key
                agents_collection.insert(agent_doc)
        except DocumentInsertError as e:
            logger.error(f"Error storing agent: {e}")
            logger.error(f"Agent data: {agent_doc}")
            raise
    
    async def get_agents(self) -> List[Dict[str, Any]]:
        """Get all agents from the database.
        
        Returns:
            List of agent dictionaries
        """
        if not self.is_connected():
            await self.connect()
        
        query = """
        FOR agent IN agents
        RETURN UNSET(agent, '_id', '_key', '_rev')
        """
        
        cursor = self._db.aql.execute(query)
        return [doc for doc in cursor]
    
    async def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get a single agent from the database.
        
        Args:
            agent_id: ID of the agent to get
            
        Returns:
            Agent dictionary or None if not found
        """
        if not self.is_connected():
            await self.connect()
        
        try:
            doc = self._db.collection('agents').get({'_key': agent_id})
            if doc:
                # Remove internal fields
                doc.pop('_id', None)
                doc.pop('_key', None)
                doc.pop('_rev', None)
                return doc
            return None
        except DocumentGetError:
            return None
    
    async def store_interaction(self, interaction: Dict[str, Any]) -> None:
        """Store an interaction between agents in the database.
        
        Args:
            interaction: Dictionary containing interaction data
        """
        if not self.is_connected():
            await self.connect()
        
        # Prepare interaction document
        interaction_doc = interaction.copy()
        
        # Ensure interaction has an id - handle both 'id' and 'interaction_id' field names
        id_value = None
        if 'id' in interaction_doc:
            id_value = interaction_doc['id']
        elif 'interaction_id' in interaction_doc:
            id_value = interaction_doc['interaction_id']
        
        if id_value is None:
            # No ID provided, create one
            from uuid import uuid4
            id_value = str(uuid4()).replace('-', '_')
        else:
            # Ensure ID is ArangoDB compatible (no -, :, or / characters)
            id_value = id_value.replace('-', '_').replace(':', '_').replace('/', '_')
        
        # Set both ID fields for compatibility
        interaction_doc['id'] = id_value
        interaction_doc['interaction_id'] = id_value
        
        # Debug logging
        logger.info(f"Setting interaction ID: {id_value}")
        
        # Ensure interaction has a timestamp
        if 'timestamp' not in interaction_doc:
            interaction_doc['timestamp'] = datetime.now().isoformat()
        
        # Get the interactions edge collection
        interactions = self._db.collection('interactions')
        
        # Ensure sender and receiver agents exist
        sender_id = interaction_doc['sender_id'].replace('-', '_')
        receiver_id = interaction_doc['receiver_id'].replace('-', '_')
        
        # Update IDs in the interaction document
        interaction_doc['sender_id'] = sender_id
        interaction_doc['receiver_id'] = receiver_id
        
        agents = self._db.collection('agents')
        
        # Check and create sender agent if needed
        if not self._document_exists(agents, sender_id):
            # Create minimal agent document if sender doesn't exist
            logger.info(f"Creating missing sender agent: {sender_id}")
            agents.insert({
                '_key': sender_id,
                'id': sender_id,
                'type': interaction_doc.get('sender_type', 'unknown'),
                'timestamp': interaction_doc['timestamp']
            })
        
        # Check and create receiver agent if needed
        if not self._document_exists(agents, receiver_id):
            # Create minimal agent document if receiver doesn't exist
            logger.info(f"Creating missing receiver agent: {receiver_id}")
            agents.insert({
                '_key': receiver_id,
                'id': receiver_id,
                'type': interaction_doc.get('receiver_type', 'unknown'),
                'timestamp': interaction_doc['timestamp']
            })
        
        # Store the run if it exists
        if 'run_id' in interaction_doc and interaction_doc['run_id']:
            run_id = interaction_doc['run_id'].replace('-', '_')
            
            # Update the run_id in the interaction document
            interaction_doc['run_id'] = run_id
            
            runs = self._db.collection('runs')
            
            if not self._document_exists(runs, run_id):
                # Create minimal run document
                runs.insert({
                    '_key': run_id,
                    'id': run_id,
                    'timestamp': interaction_doc['timestamp'],
                    'status': 'completed'
                })
        
        # Create the edge document
        edge = {
            '_from': f'agents/{sender_id}',
            '_to': f'agents/{receiver_id}',
            '_key': interaction_doc['id'],
            **interaction_doc
        }
        
        try:
            # Debug
            logger.info(f"Attempting to insert interaction edge with key: {edge['_key']}")
            logger.info(f"From: {edge['_from']}, To: {edge['_to']}")
            
            # Make the interaction document safe for ArangoDB by removing duplicate ID fields
            # We need to keep the _key, _from, and _to fields
            safe_edge = {
                '_key': edge['_key'],
                '_from': edge['_from'],
                '_to': edge['_to'],
                'sender_id': edge['sender_id'],
                'receiver_id': edge['receiver_id'],
                'message': edge['message'],
                'topic': edge['topic'],
                'timestamp': edge['timestamp'],
            }
            
            # Add optional fields if present
            for field in ['interaction_type', 'priority', 'sentiment', 'run_id', 'metadata']:
                if field in edge and edge[field] is not None:
                    safe_edge[field] = edge[field]
            
            # Insert the interaction edge
            interactions.insert(safe_edge)
            logger.info(f"Successfully inserted interaction edge")
            
            # If run_id exists, create participation edges
            if 'run_id' in interaction_doc and interaction_doc['run_id']:
                run_id = interaction_doc['run_id']
                participations = self._db.collection('participations')
                
                # Create participation edges for sender and receiver
                participation_key1 = f"{sender_id}_to_{run_id}"
                participation_key2 = f"{receiver_id}_to_{run_id}"
                
                try:
                    participations.insert({
                        '_key': participation_key1,
                        '_from': f'agents/{sender_id}',
                        '_to': f'runs/{run_id}',
                        'role': 'sender',
                        'interaction_id': interaction_doc['id'],
                        'timestamp': interaction_doc['timestamp']
                    })
                except DocumentInsertError:
                    # Participation edge may already exist, which is fine
                    pass
                
                try:
                    participations.insert({
                        '_key': participation_key2,
                        '_from': f'agents/{receiver_id}',
                        '_to': f'runs/{run_id}',
                        'role': 'receiver',
                        'interaction_id': interaction_doc['id'],
                        'timestamp': interaction_doc['timestamp']
                    })
                except DocumentInsertError:
                    # Participation edge may already exist, which is fine
                    pass
                
        except DocumentInsertError as e:
            logger.error(f"Error storing interaction: {e}")
            logger.error(f"Edge document: {edge}")
            raise
    
    async def get_interactions(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get interactions between agents from the database.
        
        Args:
            limit: Maximum number of interactions to return
            
        Returns:
            List of interaction dictionaries
        """
        if not self.is_connected():
            await self.connect()
        
        query = """
        FOR i IN interactions
            LET sender = DOCUMENT(i._from)
            LET receiver = DOCUMENT(i._to)
            SORT i.timestamp DESC
            LIMIT @limit
            RETURN MERGE(
                UNSET(i, '_id', '_rev', '_from', '_to'),
                { 
                    id: i._key,
                    sender_id: sender.id, 
                    receiver_id: receiver.id 
                }
            )
        """
        
        cursor = self._db.aql.execute(query, bind_vars={'limit': limit})
        return [doc for doc in cursor]
    
    async def get_agent_interactions(self, agent_id: str) -> List[Dict[str, Any]]:
        """Get all interactions associated with an agent.
        
        Args:
            agent_id: Agent ID
            
        Returns:
            List of interactions
        """
        if not self.is_connected():
            await self.connect()
        
        query = """
        FOR i IN interactions
            FILTER i._from == CONCAT('agents/', @agent_id) OR i._to == CONCAT('agents/', @agent_id)
            LET sender = DOCUMENT(i._from)
            LET receiver = DOCUMENT(i._to)
            SORT i.timestamp DESC
            RETURN MERGE(
                UNSET(i, '_id', '_rev', '_from', '_to'),
                { 
                    id: i._key, 
                    sender_id: sender.id, 
                    receiver_id: receiver.id 
                }
            )
        """
        
        cursor = self._db.aql.execute(query, bind_vars={'agent_id': agent_id})
        return [doc for doc in cursor]
    
    async def get_interaction(self, interaction_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific interaction by ID.
        
        Args:
            interaction_id: ID of the interaction to retrieve
            
        Returns:
            Interaction data dictionary or None if not found
        """
        if not self.is_connected():
            await self.connect()
        
        query = """
        FOR i IN interactions
            FILTER i._key == @interaction_id
            LET sender = DOCUMENT(i._from)
            LET receiver = DOCUMENT(i._to)
            RETURN MERGE(
                UNSET(i, '_id', '_rev', '_from', '_to'),
                { 
                    id: i._key, 
                    sender_id: sender.id, 
                    receiver_id: receiver.id 
                }
            )
        """
        
        cursor = self._db.aql.execute(query, bind_vars={'interaction_id': interaction_id})
        results = [doc for doc in cursor]
        return results[0] if results else None
    
    async def store_run(self, run: Dict[str, Any]) -> None:
        """Store a run in the database.
        
        Args:
            run: Dictionary containing run data
        """
        if not self.is_connected():
            await self.connect()
        
        # Prepare run document
        run_doc = run.copy()
        
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
        if not self.is_connected():
            await self.connect()
        
        if agent_id:
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
    
    async def get_network(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get network data from the database with optional filters.
        
        Args:
            filters: Optional filters to apply to the network data
            
        Returns:
            Dictionary containing nodes and edges
        """
        if not self.is_connected():
            await self.connect()
        
        # Default filters
        if filters is None:
            filters = {}
        
        # Build AQL query based on filters
        query_parts = []
        bind_vars = {}
        
        # Start with base query for nodes
        query_parts.append("""
        LET nodes = (
            FOR agent IN agents
        """)
        
        # Add node filters if any
        if 'node_type' in filters:
            query_parts.append("    FILTER agent.type == @node_type")
            bind_vars['node_type'] = filters['node_type']
        
        # Complete nodes query
        query_parts.append("""
            RETURN {
                id: agent.id,
                type: agent.type,
                properties: agent
            }
        )
        """)
        
        # Start edges query
        query_parts.append("""
        LET edges = (
            FOR i IN interactions
        """)
        
        # Add edge filters
        if 'start_time' in filters:
            query_parts.append("    FILTER i.timestamp >= @start_time")
            bind_vars['start_time'] = filters['start_time']
        
        if 'end_time' in filters:
            query_parts.append("    FILTER i.timestamp <= @end_time")
            bind_vars['end_time'] = filters['end_time']
        
        if 'relationship_type' in filters:
            query_parts.append("    FILTER i.interaction_type == @relationship_type")
            bind_vars['relationship_type'] = filters['relationship_type']
        
        if 'agent_ids' in filters and filters['agent_ids']:
            query_parts.append("""
            LET sender = DOCUMENT(i._from)
            LET receiver = DOCUMENT(i._to)
            FILTER sender.id IN @agent_ids OR receiver.id IN @agent_ids
            """)
            bind_vars['agent_ids'] = filters['agent_ids']
        
        # Complete edges query
        query_parts.append("""
            LET sender = DOCUMENT(i._from)
            LET receiver = DOCUMENT(i._to)
            RETURN {
                source: sender.id,
                target: receiver.id,
                type: i.interaction_type,
                properties: i
            }
        )
        """)
        
        # Return results
        query_parts.append("""
        RETURN {
            nodes: nodes,
            edges: edges
        }
        """)
        
        # Execute the query
        query = "\n".join(query_parts)
        cursor = self._db.aql.execute(query, bind_vars=bind_vars)
        result = next(cursor)
        
        return result
    
    async def get_network_data(self, node_type: Optional[str] = None, time_range: Optional[str] = None) -> Dict[str, Any]:
        """Get network data from the database with optional filters.
        
        Args:
            node_type: Optional type of nodes to query
            time_range: Optional time range filter (24h, 7d, 30d, all)
            
        Returns:
            Dictionary containing nodes and edges
        """
        # Convert time range to timestamps
        start_time = None
        if time_range:
            from datetime import datetime, timedelta
            now = datetime.now()
            if time_range == "24h":
                start_time = (now - timedelta(hours=24)).isoformat()
            elif time_range == "7d":
                start_time = (now - timedelta(days=7)).isoformat()
            elif time_range == "30d":
                start_time = (now - timedelta(days=30)).isoformat()
        
        # Build query parameters
        filters = {
            "node_type": node_type,
            "start_time": start_time,
        }
        
        # Filter out None values
        filters = {k: v for k, v in filters.items() if v is not None}
        
        return await self.get_network(filters)
        
    async def query_network(self, node_type: Optional[str] = None, relationship_type: Optional[str] = None,
                          start_time: Optional[str] = None, end_time: Optional[str] = None,
                          agent_ids: Optional[List[str]] = None, limit: Optional[int] = None,
                          include_properties: bool = True) -> Dict[str, Any]:
        """Advanced query for network data with multiple filter options.
        
        Args:
            node_type: Filter nodes by type
            relationship_type: Filter relationships by type
            start_time: Filter for interactions after this time
            end_time: Filter for interactions before this time
            agent_ids: Filter for interactions involving these agents
            limit: Maximum number of results to return
            include_properties: Whether to include node and edge properties
            
        Returns:
            Dictionary containing nodes and edges matching the query
        """
        if not self.is_connected():
            await self.connect()
            
        # Build query filters
        filters = {
            "node_type": node_type,
            "relationship_type": relationship_type,
            "start_time": start_time,
            "end_time": end_time,
            "agent_ids": agent_ids,
            "include_properties": include_properties
        }
        
        # Filter out None values
        filters = {k: v for k, v in filters.items() if v is not None}
        
        # Use the existing get_network method with our filters
        result = await self.get_network(filters)
        
        # Apply limit if specified
        if limit and isinstance(limit, int):
            result["nodes"] = result["nodes"][:limit]
            result["edges"] = result["edges"][:limit]
            
        return result
    
    async def get_all_nodes(self) -> List[Dict[str, Any]]:
        """Get all nodes in the graph.
        
        Returns:
            List of all node dictionaries in the graph
        """
        if not self.is_connected():
            await self.connect()
        
        # Combine agents and runs which are our node collections
        agents = await self.get_agents()
        
        # Get runs
        runs_query = """
        FOR run IN runs
        RETURN UNSET(run, '_id', '_key', '_rev')
        """
        cursor = self._db.aql.execute(runs_query)
        runs = [doc for doc in cursor]
        
        return agents + runs
    
    async def get_all_relationships(self) -> List[Dict[str, Any]]:
        """Get all relationships in the graph.
        
        Returns:
            List of all relationship dictionaries in the graph
        """
        if not self.is_connected():
            await self.connect()
        
        # Combine interactions and participations which are our edge collections
        interactions = await self.get_interactions(limit=10000)  # Set a high limit
        
        # Get participations
        part_query = """
        FOR p IN participations
        LET agent = DOCUMENT(p._from)
        LET run = DOCUMENT(p._to)
        RETURN MERGE(
            UNSET(p, '_id', '_key', '_rev', '_from', '_to'),
            { agent_id: agent.id, run_id: run.id }
        )
        """
        cursor = self._db.aql.execute(part_query)
        participations = [doc for doc in cursor]
        
        return interactions + participations
    
    async def query_nodes(self, query: Any) -> List[Dict[str, Any]]:
        """Query nodes with filters.
        
        Args:
            query: AQL query or filter parameters
            
        Returns:
            List of node dictionaries matching the query
        """
        if not self.is_connected():
            await self.connect()
        
        # If query is a string, treat it as AQL
        if isinstance(query, str):
            cursor = self._db.aql.execute(query)
            return [doc for doc in cursor]
        
        # If query is dict, treat as filter parameters
        elif isinstance(query, dict):
            # Build query based on parameters
            filters = []
            bind_vars = {}
            
            # Start with agents
            if query.get("collection") == "runs":
                aql = "FOR node IN runs"
            else:
                aql = "FOR node IN agents"
            
            # Add filters
            if "id" in query:
                filters.append("node.id == @id")
                bind_vars["id"] = query["id"]
            
            if "type" in query:
                filters.append("node.type == @type")
                bind_vars["type"] = query["type"]
            
            if "role" in query:
                filters.append("node.role == @role")
                bind_vars["role"] = query["role"]
            
            # Add filter clause if there are filters
            if filters:
                aql += " FILTER " + " AND ".join(filters)
            
            # Add return clause
            aql += " RETURN UNSET(node, '_id', '_key', '_rev')"
            
            # Execute query
            cursor = self._db.aql.execute(aql, bind_vars=bind_vars)
            return [doc for doc in cursor]
        
        # Default to returning all nodes
        return await self.get_all_nodes()
    
    async def query_relationships(self, query: Any) -> List[Dict[str, Any]]:
        """Query relationships with filters.
        
        Args:
            query: AQL query or filter parameters
            
        Returns:
            List of relationship dictionaries matching the query
        """
        if not self.is_connected():
            await self.connect()
        
        # If query is a string, treat it as AQL
        if isinstance(query, str):
            cursor = self._db.aql.execute(query)
            return [doc for doc in cursor]
        
        # If query is dict, treat as filter parameters
        elif isinstance(query, dict):
            # Build query based on parameters
            filters = []
            bind_vars = {}
            
            # Start with interactions or participations
            if query.get("collection") == "participations":
                aql = """
                FOR edge IN participations
                LET agent = DOCUMENT(edge._from)
                LET run = DOCUMENT(edge._to)
                """
            else:
                aql = """
                FOR edge IN interactions
                LET sender = DOCUMENT(edge._from)
                LET receiver = DOCUMENT(edge._to)
                """
            
            # Add filters
            if "sender_id" in query:
                filters.append("sender.id == @sender_id")
                bind_vars["sender_id"] = query["sender_id"]
            
            if "receiver_id" in query:
                filters.append("receiver.id == @receiver_id")
                bind_vars["receiver_id"] = query["receiver_id"]
            
            if "agent_id" in query:
                filters.append("(sender.id == @agent_id OR receiver.id == @agent_id)")
                bind_vars["agent_id"] = query["agent_id"]
            
            if "run_id" in query:
                filters.append("edge.run_id == @run_id")
                bind_vars["run_id"] = query["run_id"]
            
            if "type" in query:
                filters.append("edge.interaction_type == @type")
                bind_vars["type"] = query["type"]
            
            # Add filter clause if there are filters
            if filters:
                aql += " FILTER " + " AND ".join(filters)
            
            # Add return clause
            if query.get("collection") == "participations":
                aql += """ 
                RETURN MERGE(
                    UNSET(edge, '_id', '_key', '_rev', '_from', '_to'),
                    { agent_id: agent.id, run_id: run.id }
                )
                """
            else:
                aql += """
                RETURN MERGE(
                    UNSET(edge, '_id', '_key', '_rev', '_from', '_to'),
                    { sender_id: sender.id, receiver_id: receiver.id }
                )
                """
            
            # Execute query
            cursor = self._db.aql.execute(aql, bind_vars=bind_vars)
            return [doc for doc in cursor]
        
        # Default to returning all relationships
        return await self.get_all_relationships()
    
    async def clear_database(self) -> Dict[str, Any]:
        """Clear all data from the database.
        
        Returns:
            Dict containing number of nodes and relationships deleted
        """
        if not self.is_connected():
            await self.connect()
        
        logger.info("Clearing all data from the database")
        
        try:
            # Count documents before deletion
            agents_count = self._db.collection('agents').count()
            interactions_count = self._db.collection('interactions').count()
            runs_count = self._db.collection('runs').count()
            participations_count = self._db.collection('participations').count()
            
            # Clear all collections
            self._db.collection('participations').truncate()
            self._db.collection('interactions').truncate()
            self._db.collection('agents').truncate()
            self._db.collection('runs').truncate()
            
            total_nodes = agents_count + runs_count
            total_edges = interactions_count + participations_count
            
            logger.info(f"Deleted {total_nodes} nodes and {total_edges} relationships")
            
            return {
                "success": True,
                "nodes_deleted": total_nodes,
                "relationships_deleted": total_edges
            }
        except Exception as e:
            logger.error(f"Error clearing database: {e}")
            raise
    
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