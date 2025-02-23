"""Agent database operations."""
from typing import Dict, Any, List, Optional
from neo4j import AsyncSession

async def store_agent(session: AsyncSession, agent: Dict[str, Any]) -> None:
    """Store an agent in the database.
    
    Args:
        session: Database session
        agent: Dictionary containing agent data
    """
    await session.run(
        """
        MERGE (a:Agent {id: $id})
        SET a += $properties
        """,
        {
            "id": agent["id"],
            "properties": {
                "type": agent.get("type"),
                "role": agent.get("role")
            }
        }
    )

async def get_agents(session: AsyncSession) -> List[Dict[str, Any]]:
    """Get all agents from the database.
    
    Args:
        session: Database session
        
    Returns:
        List of agent dictionaries
    """
    result = await session.run(
        """
        MATCH (a:Agent)
        RETURN a.id as id, a.type as type, a.role as role
        """
    )
    
    agents = []
    async for record in result:
        agents.append({
            "id": record["id"],
            "type": record["type"],
            "role": record["role"]
        })
    return agents

async def get_agent(session: AsyncSession, agent_id: str) -> Optional[Dict[str, Any]]:
    """Get a single agent from the database.
    
    Args:
        session: Database session
        agent_id: ID of the agent to get
        
    Returns:
        Agent dictionary or None if not found
    """
    result = await session.run(
        """
        MATCH (a:Agent {id: $id})
        RETURN a.id as id, a.type as type, a.role as role
        """,
        {"id": agent_id}
    )
    
    record = await result.single()
    if record:
        return {
            "id": record["id"],
            "type": record["type"],
            "role": record["role"]
        }
    return None
