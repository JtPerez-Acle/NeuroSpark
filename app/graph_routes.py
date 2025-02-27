"""Graph routes for the Agent Interaction Backend."""
from fastapi import APIRouter, Request, HTTPException
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timezone

# Configure logging
logger = logging.getLogger("kqml-parser-backend")

# Create router
graph_router = APIRouter()

def get_db(request: Request):
    """Get database instance from app state."""
    return request.app.state.db

@graph_router.get("",
    response_model=Dict[str, Any],
    summary="Get Graph Data",
    description="Get all nodes and links for graph visualization.",
    response_description="Graph visualization data with nodes and links.",
    responses={
        500: {"description": "Internal server error"}
    }
)
async def get_graph_data(request: Request) -> Dict[str, Any]:
    """Get all nodes and links for graph visualization."""
    try:
        db = get_db(request)
        
        # Get all agents as nodes
        agents = await db.get_agents()
        nodes = []
        for agent in agents:
            nodes.append({
                "id": agent["id"],
                "label": agent.get("role", "agent"),
                "type": agent.get("type", "unknown"),
                "details": f"Type: {agent.get('type', 'unknown')}, Role: {agent.get('role', 'unknown')}",
                "timestamp": agent.get("timestamp", datetime.now(timezone.utc).isoformat())
            })
            
        # Get all interactions as links
        interactions = await db.get_interactions(limit=500)  # Limit to avoid overloading the visualization
        links = []
        
        for interaction in interactions:
            link_id = interaction.get("id", "unknown")
            source = interaction.get("sender_id", "unknown")
            target = interaction.get("receiver_id", "unknown")
            
            # Skip links with unknown source or target (they would break the graph)
            if source == "unknown" or target == "unknown":
                continue
                
            links.append({
                "id": link_id,
                "source": source,
                "target": target,
                "type": interaction.get("interaction_type", "interaction"),
                "label": interaction.get("topic", "interaction")
            })
            
        return {
            "nodes": nodes,
            "links": links
        }
    except Exception as e:
        logger.error(f"Error fetching graph data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))