"""Message model for Neo4j database operations."""
from typing import Dict, Any, List, Optional
from datetime import datetime
from neo4j import AsyncSession
from .base import Neo4jModel
from pydantic import BaseModel, Field
from uuid import uuid4
from pydantic import BaseModel, Field
from typing import Optional

class MessageModel(Neo4jModel):
    """Model for Message operations in Neo4j."""
    
    id: str = Field(default_factory=lambda: str(uuid4()))
    performative: str
    content: Dict[str, Any]
    language: str = "json"
    ontology: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    agent_id: str
    run_id: str

    def __init__(self, performative: str, content: Dict[str, Any], agent_id: str, run_id: str, **kwargs):
        """Initialize message model."""
        super().__init__(**kwargs)
        self.id = kwargs.get("id", self.id)
        self.performative = performative
        self.content = content
        self.language = kwargs.get("language", self.language)
        self.ontology = kwargs.get("ontology", self.ontology)
        self.timestamp = kwargs.get("timestamp", self.timestamp)
        self.agent_id = agent_id
        self.run_id = run_id

    async def store(self, session: AsyncSession) -> None:
        """Store a KQML message in Neo4j."""
        query = """
        MATCH (a:Agent {id: $agent_id})
        MATCH (r:Run {id: $run_id})
        CREATE (m:Message {
            id: $id,
            performative: $performative,
            content: $content,
            language: $language,
            ontology: $ontology,
            timestamp: $timestamp
        })
        CREATE (m)-[:SENT_BY]->(a)
        CREATE (m)-[:PART_OF]->(r)
        """
        await session.run(
            query,
            id=self.id,
            performative=self.performative,
            content=self.serialize_content(self.content),
            language=self.language,
            ontology=self.ontology,
            timestamp=self.timestamp,
            agent_id=self.agent_id,
            run_id=self.run_id
        )

    @staticmethod
    async def get_by_agent(session: AsyncSession, agent_id: str) -> List[Dict[str, Any]]:
        """Get all messages sent by an agent."""
        query = """
        MATCH (m:Message)-[:SENT_BY]->(a:Agent {id: $agent_id})
        WITH m, a
        ORDER BY m.timestamp DESC
        RETURN m {
            .id,
            .performative,
            .content,
            .language,
            .ontology,
            .timestamp,
            agent: a { .id, .type, .role }
        } as message
        """
        result = await session.run(query, agent_id=agent_id)
        messages = []
        async for record in result:
            messages.append(record["message"])
        return messages
