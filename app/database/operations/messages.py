"""Message operations for Neo4j database."""
from typing import Dict, Any, List
import json
from neo4j import AsyncSession

async def store_message(session: AsyncSession, message: Dict[str, Any]) -> None:
    """Store a message in the database.
    
    Args:
        session: Database session
        message: Dictionary containing message data
    """
    # Convert content to string for Neo4j storage
    message_data = message.copy()
    message_data["content"] = json.dumps(message["content"])
    
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
    CREATE (a)-[:SENT]->(m)
    CREATE (m)-[:PART_OF]->(r)
    """
    await session.run(query, message_data)

async def get_messages(session: AsyncSession, agent_id: str = None) -> List[Dict[str, Any]]:
    """Get messages from the database.
    
    Args:
        session: Database session
        agent_id: Optional agent ID to filter messages
        
    Returns:
        List of message dictionaries
    """
    if agent_id:
        query = """
        MATCH (a:Agent {id: $agent_id})-[:SENT]->(m:Message)
        RETURN m
        ORDER BY m.timestamp DESC
        """
        result = await session.run(query, {"agent_id": agent_id})
    else:
        query = """
        MATCH (m:Message)
        RETURN m
        ORDER BY m.timestamp DESC
        """
        result = await session.run(query)
    
    messages = []
    async for record in result:
        message = dict(record["m"])
        # Convert content back to dictionary
        message["content"] = json.loads(message["content"])
        messages.append(message)
    return messages
