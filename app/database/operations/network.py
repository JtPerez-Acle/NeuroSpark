"""Network query operations."""
from typing import Dict, Any, List
from neo4j import AsyncSession

async def get_network(session: AsyncSession, filters: Dict[str, Any] = None) -> Dict[str, Any]:
    """Get network data from the database with optional filters.
    
    Args:
        session: Database session
        filters: Optional dictionary of filters
        
    Returns:
        Dictionary containing nodes and edges
    """
    # Base query
    query = """
    MATCH (a:Agent)
    """
    
    # Add filter conditions if provided
    params = {}
    if filters:
        conditions = []
        if filters.get("agent_type"):
            conditions.append("a.type = $agent_type")
            params["agent_type"] = filters["agent_type"]
        if filters.get("role"):
            conditions.append("a.role = $role")
            params["role"] = filters["role"]
        if conditions:
            query += "\nWHERE " + " AND ".join(conditions)
    
    # Get filtered nodes
    nodes_query = query + "\nRETURN COLLECT(DISTINCT { id: a.id, type: a.type, role: a.role }) as nodes"
    nodes_result = await session.run(nodes_query, params)
    nodes_record = await nodes_result.single()
    nodes = nodes_record["nodes"]
    
    # Get edges between filtered nodes
    edges_query = """
    MATCH (a:Agent)-[r:INTERACTS_WITH]->(b:Agent)
    WHERE a.id IN $node_ids AND b.id IN $node_ids
    RETURN COLLECT(DISTINCT {
        source: a.id,
        target: b.id,
        messages: r.messages
    }) as edges
    """
    
    node_ids = [node["id"] for node in nodes]
    edges_result = await session.run(edges_query, {"node_ids": node_ids})
    edges_record = await edges_result.single()
    edges = edges_record["edges"]
    
    return {
        "nodes": nodes,
        "edges": edges
    }
