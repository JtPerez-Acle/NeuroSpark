"""Interaction database operations."""
from typing import Dict, Any, List, Optional
import json
from neo4j import AsyncSession

async def store_interaction(session: AsyncSession, interaction: Dict[str, Any]) -> None:
    """Store an interaction between agents in the database.
    
    Args:
        session: Database session
        interaction: Dictionary containing interaction data
    """
    # Create receiver agent if it doesn't exist
    await session.run(
        """
        MERGE (receiver:Agent {id: $receiver_id})
        ON CREATE SET receiver.type = 'unknown', receiver.role = 'unknown'
        """,
        {"receiver_id": interaction["receiver_id"]}
    )
    
    # Create sender agent if it doesn't exist
    await session.run(
        """
        MERGE (sender:Agent {id: $sender_id})
        ON CREATE SET sender.type = 'unknown', sender.role = 'unknown'
        """,
        {"sender_id": interaction["sender_id"]}
    )
    
    # Convert metadata to JSON if it exists
    metadata = json.dumps(interaction.get("metadata", {})) if interaction.get("metadata") else "{}"
    
    # Create or update interaction
    await session.run(
        """
        MATCH (sender:Agent {id: $sender_id})
        MATCH (receiver:Agent {id: $receiver_id})
        CREATE (sender)-[r:INTERACTS {
            id: $id,
            topic: $topic,
            message: $message,
            interaction_type: $interaction_type,
            timestamp: $timestamp,
            priority: $priority,
            sentiment: $sentiment,
            duration_ms: $duration_ms,
            run_id: $run_id,
            metadata: $metadata
        }]->(receiver)
        """,
        {
            "id": interaction.get("interaction_id", interaction.get("id", "")),
            "sender_id": interaction["sender_id"],
            "receiver_id": interaction["receiver_id"],
            "topic": interaction["topic"],
            "message": interaction["message"],
            "interaction_type": interaction.get("interaction_type", "message"),
            "timestamp": interaction["timestamp"],
            "priority": interaction.get("priority"),
            "sentiment": interaction.get("sentiment"),
            "duration_ms": interaction.get("duration_ms"),
            "run_id": interaction.get("run_id"),
            "metadata": metadata
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
        MATCH (sender:Agent)-[r:INTERACTS]->(receiver:Agent)
        RETURN sender.id as sender_id, receiver.id as receiver_id,
               r.id as id, r.topic as topic, r.message as message,
               r.interaction_type as interaction_type, r.timestamp as timestamp,
               r.priority as priority, r.sentiment as sentiment,
               r.duration_ms as duration_ms, r.run_id as run_id, r.metadata as metadata
        ORDER BY r.timestamp DESC
        LIMIT $limit
        """,
        {"limit": limit}
    )
    
    interactions = []
    async for record in result:
        # Parse metadata if it exists
        metadata = json.loads(record["metadata"]) if record["metadata"] else {}
        
        interactions.append({
            "id": record["id"],
            "sender_id": record["sender_id"],
            "receiver_id": record["receiver_id"],
            "topic": record["topic"],
            "message": record["message"],
            "interaction_type": record["interaction_type"],
            "timestamp": record["timestamp"],
            "priority": record["priority"],
            "sentiment": record["sentiment"],
            "duration_ms": record["duration_ms"],
            "run_id": record["run_id"],
            "metadata": metadata
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
        MATCH (sender:Agent)-[r:INTERACTS]->(receiver:Agent)
        WHERE sender.id = $agent_id OR receiver.id = $agent_id
        RETURN sender.id as sender_id, receiver.id as receiver_id,
               r.id as id, r.topic as topic, r.message as message,
               r.interaction_type as interaction_type, r.timestamp as timestamp,
               r.priority as priority, r.sentiment as sentiment,
               r.duration_ms as duration_ms, r.run_id as run_id, r.metadata as metadata
        ORDER BY r.timestamp DESC
        """,
        {"agent_id": agent_id}
    )
    
    interactions = []
    async for record in result:
        # Parse metadata if it exists
        metadata = json.loads(record["metadata"]) if record["metadata"] else {}
        
        interactions.append({
            "id": record["id"],
            "sender_id": record["sender_id"],
            "receiver_id": record["receiver_id"],
            "topic": record["topic"],
            "message": record["message"],
            "interaction_type": record["interaction_type"],
            "timestamp": record["timestamp"],
            "priority": record["priority"],
            "sentiment": record["sentiment"],
            "duration_ms": record["duration_ms"],
            "run_id": record["run_id"],
            "metadata": metadata
        })
    
    return interactions

async def get_interaction(session: AsyncSession, interaction_id: str) -> Optional[Dict[str, Any]]:
    """Get a specific interaction by ID.
    
    Args:
        session: Database session
        interaction_id: ID of the interaction to retrieve
        
    Returns:
        Interaction data dictionary or None if not found
    """
    result = await session.run(
        """
        MATCH (sender:Agent)-[r:INTERACTS]->(receiver:Agent)
        WHERE r.id = $interaction_id
        RETURN sender.id as sender_id, receiver.id as receiver_id,
               r.id as id, r.topic as topic, r.message as message,
               r.interaction_type as interaction_type, r.timestamp as timestamp,
               r.priority as priority, r.sentiment as sentiment,
               r.duration_ms as duration_ms, r.run_id as run_id, r.metadata as metadata
        """,
        {"interaction_id": interaction_id}
    )
    
    record = await result.single()
    if not record:
        return None
        
    # Parse metadata if it exists
    metadata = json.loads(record["metadata"]) if record["metadata"] else {}
    
    return {
        "id": record["id"],
        "sender_id": record["sender_id"],
        "receiver_id": record["receiver_id"],
        "topic": record["topic"],
        "message": record["message"],
        "interaction_type": record["interaction_type"],
        "timestamp": record["timestamp"],
        "priority": record["priority"],
        "sentiment": record["sentiment"],
        "duration_ms": record["duration_ms"],
        "run_id": record["run_id"],
        "metadata": metadata
    }
