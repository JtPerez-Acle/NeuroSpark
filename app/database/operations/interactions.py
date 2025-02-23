"""Interaction database operations."""
from typing import Dict, Any, List
import json
from neo4j import AsyncSession

async def store_interaction(session: AsyncSession, interaction: Dict[str, Any]) -> None:
    """Store an interaction between agents in the database.
    
    Args:
        session: Database session
        interaction: Dictionary containing interaction data
    """
    # Create target agent if it doesn't exist
    await session.run(
        """
        MERGE (target:Agent {id: $target_id})
        ON CREATE SET target.type = 'unknown', target.role = 'unknown'
        """,
        {"target_id": interaction["target_id"]}
    )
    
    # Create source agent if it doesn't exist
    await session.run(
        """
        MERGE (source:Agent {id: $source_id})
        ON CREATE SET source.type = 'unknown', source.role = 'unknown'
        """,
        {"source_id": interaction["source_id"]}
    )
    
    # Create or update interaction
    await session.run(
        """
        MATCH (source:Agent {id: $source_id})
        MATCH (target:Agent {id: $target_id})
        CREATE (source)-[r:INTERACTS {
            performative: $performative,
            content: $content,
            timestamp: $timestamp
        }]->(target)
        """,
        {
            "source_id": interaction["source_id"],
            "target_id": interaction["target_id"],
            "performative": interaction["performative"],
            "content": json.dumps(interaction["content"]),
            "timestamp": interaction["timestamp"]
        }
    )

async def get_interactions(session: AsyncSession, limit: int = 100) -> List[Dict[str, Any]]:
    """Get interactions between agents from the database.
    
    Args:
        session: Database session
        limit: Maximum number of interactions to return
        
    Returns:
        List of interaction dictionaries
    """
    result = await session.run(
        """
        MATCH (source:Agent)-[r:INTERACTS]->(target:Agent)
        RETURN source.id as source_id, target.id as target_id,
               r.performative as performative, r.content as content,
               r.timestamp as timestamp
        ORDER BY r.timestamp DESC
        LIMIT $limit
        """,
        {"limit": limit}
    )
    
    interactions = []
    async for record in result:
        interactions.append({
            "source_id": record["source_id"],
            "target_id": record["target_id"],
            "performative": record["performative"],
            "content": json.loads(record["content"]),
            "timestamp": record["timestamp"]
        })
    
    return interactions

async def get_agent_interactions(session: AsyncSession, agent_id: str) -> List[Dict[str, Any]]:
    """Get all interactions associated with an agent.
    
    Args:
        session: Database session
        agent_id: Agent ID
        
    Returns:
        List of interactions
    """
    result = await session.run(
        """
        MATCH (source:Agent)-[r:INTERACTS]->(target:Agent)
        WHERE source.id = $agent_id OR target.id = $agent_id
        RETURN source.id as source_id, target.id as target_id,
               r.performative as performative, r.content as content,
               r.timestamp as timestamp
        ORDER BY r.timestamp DESC
        """,
        {"agent_id": agent_id}
    )
    
    interactions = []
    async for record in result:
        interactions.append({
            "source_id": record["source_id"],
            "target_id": record["target_id"],
            "performative": record["performative"],
            "content": json.loads(record["content"]),
            "timestamp": record["timestamp"]
        })
    
    return interactions
