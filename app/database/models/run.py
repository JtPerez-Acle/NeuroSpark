"""Run model for Neo4j database."""
from typing import Dict, Any, List
from datetime import datetime, timezone
from neo4j import AsyncSession

from .base import Neo4jModel

class RunModel(Neo4jModel):
    """Model for run operations."""
    
    def __init__(self, **kwargs):
        """Initialize run model."""
        super().__init__(**kwargs)
        self.id = kwargs.get("id")
        self.timestamp = kwargs.get("timestamp", datetime.now(timezone.utc).isoformat())
        
    async def store(self, session: AsyncSession) -> None:
        """Store run in Neo4j."""
        query = """
        CREATE (r:Run {
            id: $id,
            timestamp: $timestamp
        })
        """
        await session.run(query, id=self.id, timestamp=self.timestamp)
        
    @staticmethod
    async def get_agent_runs(session: AsyncSession, agent_id: str) -> List[Dict[str, Any]]:
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
            run = record["run"]
            runs.append(run)
        return runs
