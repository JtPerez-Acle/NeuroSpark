"""Agent model for Neo4j database operations."""
from typing import Dict, Any, List
from datetime import datetime
from neo4j import AsyncSession
from .base import Neo4jModel

class AgentModel(Neo4jModel):
    """Model for Agent operations in Neo4j."""
    
    def __init__(self, **kwargs):
        """Initialize agent model."""
        super().__init__(**kwargs)
        self.id = kwargs.get("id")
        self.type = kwargs.get("type")
        self.role = kwargs.get("role")
        self.created_at = kwargs.get("created_at", self.get_timestamp())

    async def store(self, session: AsyncSession) -> None:
        """Store an agent in Neo4j."""
        query = """
        MERGE (a:Agent {id: $id})
        SET a.type = $type,
            a.role = $role,
            a.created_at = $created_at
        """
        await session.run(query, 
                         id=self.id,
                         type=self.type,
                         role=self.role,
                         created_at=self.created_at)

    @staticmethod
    async def get_runs(session: AsyncSession, agent_id: str) -> List[Dict[str, Any]]:
        """Get all runs associated with an agent."""
        query = """
        MATCH (a:Agent {id: $agent_id})<-[:SENT_BY|RECEIVED_BY]-(i:Interaction)-[:PART_OF]->(r:Run)
        WITH DISTINCT r
        ORDER BY r.timestamp DESC
        RETURN r {
            .id,
            .timestamp
        } as run
        """
        result = await session.run(query, agent_id=agent_id)
        runs = []
        async for record in result:
            runs.append(record["run"])
        return runs

    @staticmethod
    async def get_interactions(session: AsyncSession, agent_id: str) -> List[Dict[str, Any]]:
        """Get all interactions associated with an agent."""
        query = """
        MATCH (a:Agent {id: $agent_id})<-[:SENT_BY|RECEIVED_BY]-(i:Interaction)
        WITH i
        ORDER BY i.timestamp DESC
        RETURN i {
            .id,
            .timestamp,
            .type
        } as interaction
        """
        result = await session.run(query, agent_id=agent_id)
        interactions = []
        async for record in result:
            interactions.append(record["interaction"])
        return interactions
