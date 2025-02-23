"""Core database functionality."""
from typing import Dict, Any, List, Optional
from neo4j import AsyncSession

from ..core.connection import Neo4jConnection
from ..operations import agents, interactions, runs, network, messages

class Neo4jDatabase:
    """Neo4j database implementation."""
    
    def __init__(self, uri: str, username: str, password: str):
        """Initialize the database.
        
        Args:
            uri: Neo4j URI
            username: Username
            password: Password
        """
        self._connection = Neo4jConnection(uri, username, password)
        self._driver = None
    
    async def connect(self) -> None:
        """Connect to the database."""
        await self._connection.connect()
        self._driver = self._connection.driver
    
    async def disconnect(self) -> None:
        """Disconnect from the database."""
        await self._connection.disconnect()
        self._driver = None

    def is_connected(self) -> bool:
        """Check if database is connected.
        
        Returns:
            True if connected, False otherwise
        """
        return self._driver is not None
    
    async def get_session(self) -> AsyncSession:
        """Get a database session.
        
        Returns:
            Database session
        """
        if not self._driver:
            await self.connect()
        return self._driver.session()
    
    @property
    def driver(self):
        """Get the database driver.
        
        Returns:
            Database driver
        """
        return self._driver
    
    async def store_agent(self, agent: Dict[str, Any]) -> None:
        """Store an agent in the database.
        
        Args:
            agent: Dictionary containing agent data
        """
        async with await self.get_session() as session:
            await agents.store_agent(session, agent)
    
    async def get_agents(self) -> List[Dict[str, Any]]:
        """Get all agents from the database.
        
        Returns:
            List of agent dictionaries
        """
        async with await self.get_session() as session:
            return await agents.get_agents(session)
    
    async def get_agent(self, agent_id: str) -> Dict[str, Any]:
        """Get a single agent from the database.
        
        Args:
            agent_id: ID of the agent to get
            
        Returns:
            Agent dictionary
            
        Raises:
            ValueError: If agent not found
        """
        async with await self.get_session() as session:
            agent = await agents.get_agent(session, agent_id)
            if not agent:
                raise ValueError(f"Agent {agent_id} not found")
            return agent
    
    async def store_interaction(self, interaction: Dict[str, Any]) -> None:
        """Store an interaction between agents in the database.
        
        Args:
            interaction: Dictionary containing interaction data
        """
        async with await self.get_session() as session:
            await interactions.store_interaction(session, interaction)
    
    async def get_interactions(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get interactions between agents from the database.
        
        Args:
            limit: Maximum number of interactions to return
            
        Returns:
            List of interaction dictionaries
        """
        async with await self.get_session() as session:
            return await interactions.get_interactions(session, limit)
    
    async def get_agent_interactions(self, agent_id: str) -> List[Dict[str, Any]]:
        """Get all interactions associated with an agent.
        
        Args:
            agent_id: Agent ID
            
        Returns:
            List of interactions
        """
        async with await self.get_session() as session:
            return await interactions.get_agent_interactions(session, agent_id)

    async def store_run(self, run: Dict[str, Any]) -> None:
        """Store a run in the database.
        
        Args:
            run: Dictionary containing run data
            
        Raises:
            ValueError: If agent not found
        """
        try:
            async with await self.get_session() as session:
                await runs.store_run(session, run)
        except Exception as e:
            # Re-raise ValueError, but wrap other exceptions
            if isinstance(e, ValueError):
                raise
            raise Exception(f"Error storing run: {str(e)}")
    
    async def get_runs(self, agent_id: str = None) -> List[Dict[str, Any]]:
        """Get runs from the database.
        
        Args:
            agent_id: Optional agent ID to filter runs
            
        Returns:
            List of run dictionaries
            
        Raises:
            ValueError: If agent not found when filtering by agent_id
        """
        try:
            async with await self.get_session() as session:
                return await runs.get_runs(session, agent_id)
        except Exception as e:
            # Re-raise ValueError, but wrap other exceptions
            if isinstance(e, ValueError):
                raise
            raise Exception(f"Error getting runs: {str(e)}")

    async def get_network(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get network data from the database with optional filters.
        
        Args:
            filters: Optional filters to apply to the network data
            
        Returns:
            Dictionary containing nodes and edges
        """
        async with await self.get_session() as session:
            return await network.get_network(session, filters)

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
        params = {
            "node_type": node_type or "Agent",
            "relationship_type": "INTERACTS",
            "start_time": start_time,
            "include_properties": True
        }
        
        return await self.query_network(**params)

    async def query_network(
        self,
        node_type: str,
        relationship_type: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        agent_ids: Optional[List[str]] = None,
        limit: Optional[int] = None,
        include_properties: Optional[bool] = True
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Query network data with filters.
        
        Args:
            node_type: Type of nodes to query
            relationship_type: Optional type of relationships to query
            start_time: Optional start time filter
            end_time: Optional end time filter
            agent_ids: Optional list of agent IDs to filter
            limit: Optional limit on number of results
            include_properties: Whether to include node and relationship properties
            
        Returns:
            Dictionary containing nodes and edges
        """
        async with await self.get_session() as session:
            # Build query
            query = f"""
            MATCH (n:{node_type})
            """
            
            # Add relationship filter if provided
            if relationship_type:
                query += f"-[r:{relationship_type}]->(m:{node_type})"
            else:
                query += f"-[r]->(m:{node_type})"
            
            # Add WHERE clause filters
            conditions = []
            params = {}
            
            if start_time:
                conditions.append("r.timestamp >= $start_time")
                params["start_time"] = start_time
            
            if end_time:
                conditions.append("r.timestamp <= $end_time")
                params["end_time"] = end_time
            
            if agent_ids:
                conditions.append("(n.id IN $agent_ids OR m.id IN $agent_ids)")
                params["agent_ids"] = agent_ids
            
            if conditions:
                query += "\nWHERE " + " AND ".join(conditions)
            
            # Add return clause
            if include_properties:
                query += """
                RETURN COLLECT(DISTINCT {
                    id: n.id,
                    type: n.type,
                    properties: properties(n)
                }) as nodes,
                COLLECT(DISTINCT {
                    source: n.id,
                    target: m.id,
                    type: type(r),
                    properties: properties(r)
                }) as edges
                """
            else:
                query += """
                RETURN COLLECT(DISTINCT {
                    id: n.id,
                    type: n.type
                }) as nodes,
                COLLECT(DISTINCT {
                    source: n.id,
                    target: m.id,
                    type: type(r)
                }) as edges
                """
            
            # Add limit if provided
            if limit:
                query += f"\nLIMIT {limit}"
            
            # Execute query
            result = await session.run(query, params)
            record = await result.single()
            
            return {
                "nodes": record["nodes"],
                "edges": record["edges"]
            }

    async def store_message(self, message: Dict[str, Any]) -> None:
        """Store a message in the database.
        
        Args:
            message: Dictionary containing message data
        """
        try:
            async with await self.get_session() as session:
                await messages.store_message(session, message)
        except Exception as e:
            raise Exception(f"Error storing message: {str(e)}")
    
    async def get_messages(self, agent_id: str = None) -> List[Dict[str, Any]]:
        """Get messages from the database.
        
        Args:
            agent_id: Optional agent ID to filter messages
            
        Returns:
            List of message dictionaries
        """
        try:
            async with await self.get_session() as session:
                return await messages.get_messages(session, agent_id)
        except Exception as e:
            raise Exception(f"Error getting messages: {str(e)}")
