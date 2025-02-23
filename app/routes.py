"""API routes for the KQML Parser Backend."""
from datetime import datetime, timezone, timedelta
import logging
from typing import Dict, Any, List, Optional
import uuid

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import ValidationError

from .models import (
    KQMLMessageModel,
    GraphQuery,
    GraphData,
    SyntheticDataParams,
    GraphNode,
    GraphRelationship
)
from .database import DatabaseInterface

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create routers
agents_router = APIRouter()
network_router = APIRouter()
synthetic_router = APIRouter()

def get_db(request: Request) -> DatabaseInterface:
    """Get database instance from app state."""
    return request.app.state.db

@agents_router.post("/message",
    response_model=Dict[str, Any],
    summary="Store Agent Message",
    description="Store a KQML message from an agent.",
    response_description="Status and message ID."
)
async def store_agent_message(message: KQMLMessageModel, request: Request):
    """Store a KQML message from an agent."""
    try:
        message_id = str(uuid.uuid4())
        run_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc)
        
        message_data = message.dict()
        message_data.update({
            "message_id": message_id,
            "run_id": run_id,
            "timestamp": timestamp.isoformat()
        })
        
        db = get_db(request)
        await db.store_interaction(message_data)
        
        return {
            "status": "success",
            "message_id": message_id,
            "run_id": run_id
        }
    except Exception as e:
        logger.error(f"Error storing message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@agents_router.get("/{agent_id}/interactions",
    response_model=List[Dict[str, Any]],
    summary="Get Agent Interactions",
    description="Get all interactions associated with an agent.",
    response_description="List of interactions."
)
async def get_agent_interactions(agent_id: str, request: Request) -> List[Dict[str, Any]]:
    """Get all interactions associated with an agent."""
    try:
        db = get_db(request)
        interactions = await db.query_nodes({"id": agent_id})
        if not interactions:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
        return interactions
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting agent interactions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@agents_router.get("/{agent_id}/runs",
    response_model=List[Dict[str, Any]],
    summary="Get Agent Runs",
    description="Get all runs associated with an agent.",
    response_description="List of runs."
)
async def get_agent_runs(agent_id: str, request: Request) -> List[Dict[str, Any]]:
    """Get all runs associated with an agent."""
    try:
        db = get_db(request)
        runs = await db.get_agent_runs(agent_id)
        if not runs:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
        return runs
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting agent runs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@agents_router.get("/{agent_id}/stats",
    response_model=Dict[str, Any],
    summary="Get Agent Statistics",
    description="Get statistics about agent interactions.",
    response_description="Agent statistics."
)
async def get_agent_stats(agent_id: str, request: Request) -> Dict[str, Any]:
    """Get statistics about agent interactions."""
    try:
        db = get_db(request)
        interactions = await db.query_nodes({"id": agent_id})
        if not interactions:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
        return {
            "total_interactions": len(interactions),
            "agent_id": agent_id
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting agent stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@network_router.get("/",
    response_model=GraphData,
    summary="Get Network Graph",
    description="Get all nodes and relationships in the agent network graph.",
    response_description="Network graph data."
)
async def get_network(
    request: Request,
    node_type: Optional[str] = Query(None, description="Filter by node type"),
    time_range: Optional[str] = Query(None, description="Time range filter (24h, 7d, 30d, all)")
) -> GraphData:
    """Get all nodes and relationships in the agent network graph."""
    try:
        db = get_db(request)
        
        # Get nodes and relationships
        nodes = await db.get_all_nodes()
        relationships = await db.get_all_relationships()
        
        # Convert to GraphData model
        return GraphData(
            nodes=[GraphNode(**node) for node in nodes],
            relationships=[GraphRelationship(**rel) for rel in relationships]
        )
    except Exception as e:
        logger.error(f"Error getting network graph: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@network_router.post("/query",
    response_model=GraphData,
    summary="Query Network Graph",
    description="Query network graph data with filters.",
    response_description="Filtered network graph data."
)
async def query_network(query: GraphQuery, request: Request) -> GraphData:
    """Query network graph data with filters."""
    try:
        db = get_db(request)
        
        # Query nodes and relationships
        nodes = await db.query_nodes(query)
        relationships = await db.query_relationships(query)
        
        # Convert to GraphData model
        return GraphData(
            nodes=[GraphNode(**node) for node in nodes],
            relationships=[GraphRelationship(**rel) for rel in relationships]
        )
    except Exception as e:
        logger.error(f"Error querying network graph: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@synthetic_router.post("/data",
    response_model=Dict[str, Any],
    summary="Generate Synthetic Dataset",
    description="Generate a synthetic dataset with the specified number of agents and interactions.",
    response_description="Status of dataset generation."
)
async def generate_synthetic_data(params: SyntheticDataParams, request: Request) -> Dict[str, Any]:
    """Generate a synthetic dataset."""
    try:
        db = get_db(request)
        await db.generate_synthetic_data(params.numAgents, params.numInteractions)
        return {
            "status": "success",
            "message": f"Generated {params.numInteractions} synthetic interactions between {params.numAgents} agents"
        }
    except Exception as e:
        logger.error(f"Error generating synthetic data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
