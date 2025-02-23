"""Interaction model for Neo4j database operations."""
from typing import Dict, Any, Optional, List
from datetime import datetime
from neo4j import AsyncSession
from .base import Neo4jModel

class InteractionModel(Neo4jModel):
    """Model for Interaction operations in Neo4j."""
    
    def __init__(self, **kwargs):
        """Initialize interaction model."""
        super().__init__(**kwargs)
        self.id = kwargs.get("id")
        self.type = kwargs.get("type")
        self.timestamp = kwargs.get("timestamp", self.get_timestamp())
        self.sender_id = kwargs.get("sender_id")
        self.receiver_id = kwargs.get("receiver_id")
        self.run_id = kwargs.get("run_id")
        self.content = kwargs.get("content", {})

    async def store(self, session: AsyncSession) -> None:
        """Store an interaction in Neo4j."""
        query = """
        MATCH (sender:Agent {id: $sender_id})
        MATCH (receiver:Agent {id: $receiver_id})
        MATCH (run:Run {id: $run_id})
        CREATE (i:Interaction {
            id: $id,
            type: $type,
            timestamp: $timestamp,
            content: $content
        })
        CREATE (i)-[:SENT_BY]->(sender)
        CREATE (i)-[:RECEIVED_BY]->(receiver)
        CREATE (i)-[:PART_OF]->(run)
        """
        await session.run(query,
                         id=self.id,
                         type=self.type,
                         timestamp=self.timestamp,
                         content=self.serialize_content(self.content),
                         sender_id=self.sender_id,
                         receiver_id=self.receiver_id,
                         run_id=self.run_id)

    @staticmethod
    async def get_by_run(session: AsyncSession, run_id: str) -> List[Dict[str, Any]]:
        """Get all interactions in a run."""
        query = """
        MATCH (i:Interaction)-[:PART_OF]->(r:Run {id: $run_id})
        MATCH (i)-[:SENT_BY]->(sender:Agent)
        MATCH (i)-[:RECEIVED_BY]->(receiver:Agent)
        WITH i, sender, receiver
        ORDER BY i.timestamp ASC
        RETURN i {
            .id,
            .type,
            .timestamp,
            .content,
            sender: sender { .id, .type, .role },
            receiver: receiver { .id, .type, .role }
        } as interaction
        """
        result = await session.run(query, run_id=run_id)
        interactions = []
        async for record in result:
            interactions.append(record["interaction"])
        return interactions

    @staticmethod
    async def get_between_agents(
        session: AsyncSession,
        agent1_id: str,
        agent2_id: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get interactions between two agents."""
        query = """
        MATCH (a1:Agent {id: $agent1_id}), (a2:Agent {id: $agent2_id})
        MATCH (i:Interaction)
        WHERE (i)-[:SENT_BY]->(a1) AND (i)-[:RECEIVED_BY]->(a2)
           OR (i)-[:SENT_BY]->(a2) AND (i)-[:RECEIVED_BY]->(a1)
        WITH i, a1, a2
        ORDER BY i.timestamp DESC
        """ + (f"LIMIT {limit}" if limit else "") + """
        RETURN i {
            .id,
            .type,
            .timestamp,
            .content,
            sender: CASE 
                WHEN (i)-[:SENT_BY]->(a1) THEN a1 { .id, .type, .role }
                ELSE a2 { .id, .type, .role }
            END,
            receiver: CASE 
                WHEN (i)-[:RECEIVED_BY]->(a1) THEN a1 { .id, .type, .role }
                ELSE a2 { .id, .type, .role }
            END
        } as interaction
        """
        result = await session.run(query, agent1_id=agent1_id, agent2_id=agent2_id)
        interactions = []
        async for record in result:
            interactions.append(record["interaction"])
        return interactions
