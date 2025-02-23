"""Neo4j database implementation module."""
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime, timezone
import uuid
import random

from neo4j import AsyncGraphDatabase, AsyncSession
from neo4j.exceptions import Neo4jError

from .base import DatabaseInterface

logger = logging.getLogger(__name__)

class Neo4jDatabase(DatabaseInterface):
    """Neo4j database implementation."""
    
    def __init__(self, uri: str, username: str, password: str):
        """Initialize Neo4j database connection."""
        self.uri = uri
        self.username = username
        self.password = password
        self.driver = None
        self.agents = {}  # For synthetic data generation
        self.runs = {}   # For synthetic data generation
        self.interactions = []  # For synthetic data generation
    
    async def connect(self) -> None:
        """Establish connection to Neo4j database."""
        try:
            self.driver = AsyncGraphDatabase.driver(
                self.uri, auth=(self.username, self.password)
            )
            # Test the connection
            async with self.driver.session() as session:
                result = await session.run("RETURN 1")
                await result.consume()
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {str(e)}")
            raise
    
    async def disconnect(self) -> None:
        """Close Neo4j database connection."""
        if self.driver:
            await self.driver.close()

    async def _get_session(self) -> AsyncSession:
        """Get a new session."""
        if not self.driver:
            await self.connect()
        return self.driver.session()

    async def store_interaction(self, interaction_data: Dict[str, Any]) -> None:
        """Store an interaction in Neo4j."""
        try:
            # Create interaction node
            query = """
            MERGE (i:Interaction {id: $id})
            SET i += $props
            WITH i
            MERGE (s:Agent {id: $sender})
            MERGE (r:Agent {id: $receiver})
            MERGE (s)-[:SENT]->(i)
            MERGE (i)-[:RECEIVED_BY]->(r)
            """
            
            props = {
                "id": interaction_data["message_id"],
                "content": interaction_data["content"],
                "performative": interaction_data["performative"],
                "timestamp": interaction_data["timestamp"]
            }
            
            async with await self._get_session() as session:
                await session.run(
                    query,
                    id=interaction_data["message_id"],
                    props=props,
                    sender=interaction_data["sender"],
                    receiver=interaction_data["receiver"]
                )
                
            # Update run if present
            if "run_id" in interaction_data:
                run_query = """
                MERGE (r:Run {id: $run_id})
                SET r.timestamp = $timestamp
                WITH r
                MATCH (i:Interaction {id: $interaction_id})
                MERGE (i)-[:PART_OF]->(r)
                """
                
                async with await self._get_session() as session:
                    await session.run(
                        run_query,
                        run_id=interaction_data["run_id"],
                        timestamp=interaction_data["timestamp"],
                        interaction_id=interaction_data["message_id"]
                    )
                
        except Exception as e:
            logger.error(f"Error storing interaction in Neo4j: {str(e)}")
            raise
    
    async def get_all_nodes(self) -> List[Dict[str, Any]]:
        """Get all nodes from Neo4j."""
        try:
            query = """
            MATCH (n)
            RETURN n
            """
            nodes = []
            async with await self._get_session() as session:
                result = await session.run(query)
                async for record in result:
                    node = record["n"]
                    nodes.append({
                        "id": node.id,
                        "labels": list(node.labels),
                        "properties": dict(node)
                    })
            return nodes
        except Exception as e:
            logger.error(f"Error getting nodes from Neo4j: {str(e)}")
            raise

    async def get_all_relationships(self) -> List[Dict[str, Any]]:
        """Get all relationships from Neo4j."""
        try:
            query = """
            MATCH ()-[r]->()
            RETURN r
            """
            relationships = []
            async with await self._get_session() as session:
                result = await session.run(query)
                async for record in result:
                    rel = record["r"]
                    relationships.append({
                        "id": rel.id,
                        "type": rel.type,
                        "start_node": rel.start_node.id,
                        "end_node": rel.end_node.id,
                        "properties": dict(rel)
                    })
            return relationships
        except Exception as e:
            logger.error(f"Error getting relationships from Neo4j: {str(e)}")
            raise

    async def query_nodes(self, query: Any) -> List[Dict[str, Any]]:
        """Query nodes with filters."""
        try:
            cypher_query = """
            MATCH (n)
            WHERE n.id = $id
            RETURN n
            """
            nodes = []
            async with await self._get_session() as session:
                result = await session.run(cypher_query, id=query.get("id"))
                async for record in result:
                    node = record["n"]
                    nodes.append({
                        "id": node.id,
                        "labels": list(node.labels),
                        "properties": dict(node)
                    })
            return nodes
        except Exception as e:
            logger.error(f"Error querying nodes from Neo4j: {str(e)}")
            raise

    async def query_relationships(self, query: Any) -> List[Dict[str, Any]]:
        """Query relationships with filters."""
        try:
            cypher_query = """
            MATCH ()-[r]->()
            WHERE r.id = $id
            RETURN r
            """
            relationships = []
            async with await self._get_session() as session:
                result = await session.run(cypher_query, id=query.get("id"))
                async for record in result:
                    rel = record["r"]
                    relationships.append({
                        "id": rel.id,
                        "type": rel.type,
                        "start_node": rel.start_node.id,
                        "end_node": rel.end_node.id,
                        "properties": dict(rel)
                    })
            return relationships
        except Exception as e:
            logger.error(f"Error querying relationships from Neo4j: {str(e)}")
            raise

    async def clear_database(self) -> Dict[str, Any]:
        """Clear all data from Neo4j database."""
        try:
            query = """
            MATCH (n)
            DETACH DELETE n
            """
            async with await self._get_session() as session:
                await session.run(query)
            return {"status": "success", "message": "Database cleared successfully"}
        except Exception as e:
            logger.error(f"Error clearing Neo4j database: {str(e)}")
            raise

    async def generate_synthetic_data(self, num_agents: int, num_interactions: int) -> None:
        """Generate synthetic KQML messages and store them in Neo4j."""
        # Clear existing data
        await self.clear_database()

        # Generate agent IDs
        agent_ids = [f"agent_{i}" for i in range(num_agents)]
        
        # KQML performatives for synthetic data
        performatives = [
            "tell", "perform", "reply", "ask-one", "ask-all",
            "stream-all", "eos", "error", "sorry", "ready"
        ]

        # Generate interactions
        run_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()

        for i in range(num_interactions):
            # Select random sender and receiver
            sender = random.choice(agent_ids)
            receiver = random.choice([a for a in agent_ids if a != sender])
            
            # Create interaction data
            interaction = {
                "message_id": str(uuid.uuid4()),
                "sender": sender,
                "receiver": receiver,
                "performative": random.choice(performatives),
                "content": f"Synthetic message {i} from {sender} to {receiver}",
                "timestamp": timestamp,
                "run_id": run_id
            }
            
            # Store the interaction
            await self.store_interaction(interaction)
            
        logger.info(f"Generated {num_interactions} synthetic interactions between {num_agents} agents")

    async def get_agent_runs(self, agent_id: str) -> List[Dict[str, Any]]:
        """Get all runs associated with an agent."""
        query = """
        MATCH (a:Agent {id: $agent_id})<-[:SENT|:RECEIVED_BY]-(i:Interaction)-[:PART_OF]->(r:Run)
        RETURN DISTINCT r.id as id, r.timestamp as timestamp
        ORDER BY r.timestamp DESC
        """
        
        async with await self._get_session() as session:
            result = await session.run(query, agent_id=agent_id)
            records = await result.data()
            return [{"id": r["id"], "timestamp": r["timestamp"]} for r in records]

    async def get_agent_interactions(self, agent_id: str) -> List[Dict[str, Any]]:
        """Get all interactions associated with an agent."""
        query = """
        MATCH (a:Agent {id: $agent_id})<-[rel:SENT|:RECEIVED_BY]-(i:Interaction)
        RETURN i.id as id,
               i.content as content,
               i.performative as performative,
               i.timestamp as timestamp,
               CASE WHEN type(rel) = 'SENT' THEN $agent_id ELSE null END as sender,
               CASE WHEN type(rel) = 'RECEIVED_BY' THEN $agent_id ELSE null END as receiver
        ORDER BY i.timestamp DESC
        """
        
        async with await self._get_session() as session:
            result = await session.run(query, agent_id=agent_id)
            records = await result.data()
            return [
                {
                    "id": r["id"],
                    "content": r["content"],
                    "performative": r["performative"],
                    "timestamp": r["timestamp"],
                    "sender": r["sender"] or agent_id,
                    "receiver": r["receiver"] or agent_id
                }
                for r in records
            ]
