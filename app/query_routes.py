"""Query routes for the Agent Interaction Backend."""
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging
import re

# Configure logging
logger = logging.getLogger("kqml-parser-backend")

# Create router
query_router = APIRouter()

class Query(BaseModel):
    """Natural language query model."""
    query: str

def get_db(request: Request):
    """Get database instance from app state."""
    return request.app.state.db

@query_router.post("",
    response_model=Dict[str, Any],
    summary="Query Interactions",
    description="Query interactions using natural language.",
    response_description="Query results with matching interactions.",
    responses={
        422: {"description": "Invalid query"},
        500: {"description": "Internal server error"}
    }
)
async def query_interactions(query: Query, request: Request) -> Dict[str, Any]:
    """Query interactions using natural language."""
    try:
        db = get_db(request)
        query_text = query.query.lower()
        
        # Get all interactions
        interactions = await db.get_interactions(limit=1000)
        
        # Simple filtering based on the query text
        filtered_interactions = []
        
        # Extract key terms from the query
        priority_match = re.search(r'priority (?:greater than|higher than|above|more than|>) (\d)', query_text)
        priority_threshold = int(priority_match.group(1)) if priority_match else None
        
        # Look for topic mentions
        topic_match = re.search(r'topic[: ]([a-zA-Z0-9_]+)', query_text)
        topic = topic_match.group(1) if topic_match else None
        
        # Look for agent mentions
        agent_match = re.search(r'(?:from|by|sent by) ([a-zA-Z0-9_]+)', query_text)
        agent = agent_match.group(1) if agent_match else None
        
        # Basic filtering logic
        for interaction in interactions:
            # Priority filter
            if priority_threshold and interaction.get("priority"):
                if interaction["priority"] <= priority_threshold:
                    continue
                    
            # Topic filter
            if topic and interaction.get("topic"):
                if topic.lower() not in interaction["topic"].lower():
                    continue
                    
            # Agent filter
            if agent and interaction.get("sender_id"):
                if agent.lower() not in interaction["sender_id"].lower():
                    continue
                    
            # Message content search
            if "message" in interaction and any(term in interaction["message"].lower() for term in query_text.split()):
                filtered_interactions.append(interaction)
                continue
                
            # Default: add if no specific filters or if it passed all filters
            if not (priority_threshold or topic or agent) or len(filtered_interactions) == 0:
                filtered_interactions.append(interaction)
                
        return {
            "interactions": filtered_interactions
        }
    except Exception as e:
        logger.error(f"Error querying interactions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))