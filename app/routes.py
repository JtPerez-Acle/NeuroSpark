"""API routes for the Agent Interaction Backend."""
from datetime import datetime, timezone, timedelta
import logging
from typing import Dict, Any, List, Optional
import uuid
from fastapi import APIRouter, FastAPI, Request, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError

from pydantic import BaseModel, Field
from .models import AgentInteraction, GraphQuery, SyntheticDataParams
from .database import get_database
from .websocket_handler import ConnectionManager
from .data_generator import DataGenerator

# Define models for database administration
class DatabaseOperation(BaseModel):
    """Database operation response."""
    success: bool = Field(..., description="Success status")
    message: str = Field(..., description="Operation message")
    details: Dict[str, Any] = Field(default_factory=dict, description="Operation details")

# Configure logging
logger = logging.getLogger("kqml-parser-backend")

# Create routers
agent_router = APIRouter()
network_router = APIRouter()
synthetic_router = APIRouter()
generate_router = APIRouter()  # New router for generate endpoints
interactions_router = APIRouter()  # New router for interactions
admin_router = APIRouter()  # New router for admin operations

def get_db(request: Request):
    """Get database instance from app state."""
    return request.app.state.db

@agent_router.post("",
    response_model=Dict[str, Any],
    summary="Create Agent",
    description="Create a new agent.",
    response_description="Status of agent creation.",
    responses={
        422: {"description": "Invalid agent data"},
        500: {"description": "Internal server error"}
    }
)
async def create_agent(agent_data: Dict[str, Any], request: Request) -> Dict[str, Any]:
    """Create a new agent."""
    try:
        db = get_db(request)
        
        # Validate required fields
        if "id" not in agent_data:
            raise ValidationError("Missing required field: id")
        if "type" not in agent_data:
            raise ValidationError("Missing required field: type")
        if "role" not in agent_data:
            raise ValidationError("Missing required field: role")
            
        # Add timestamp
        agent_data["timestamp"] = datetime.now(timezone.utc).isoformat()
        
        # Store agent
        await db.store_agent(agent_data)
        return {"message": "Agent created successfully", "agent": agent_data}
    except ValidationError as e:
        logger.error(f"Validation error creating agent: {str(e)}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating agent: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@interactions_router.get("/{interaction_id}",
    response_model=Dict[str, Any],
    summary="Get Interaction",
    description="Get a specific interaction by ID.",
    response_description="Interaction details.",
    responses={
        404: {"description": "Interaction not found"},
        500: {"description": "Internal server error"}
    }
)
async def get_interaction(interaction_id: str, request: Request) -> Dict[str, Any]:
    """Get a specific interaction by ID."""
    try:
        db = get_db(request)
        interaction = await db.get_interaction(interaction_id)
        if not interaction:
            raise HTTPException(status_code=404, detail=f"Interaction {interaction_id} not found")
        return interaction
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting interaction: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@interactions_router.get("",
    response_model=List[Dict[str, Any]],
    summary="Get Interactions",
    description="Get all interactions, with optional filtering.",
    response_description="List of interactions.",
    responses={
        500: {"description": "Internal server error"}
    }
)
async def get_interactions(
    request: Request,
    limit: Optional[int] = Query(100, description="Maximum number of interactions to return")
) -> List[Dict[str, Any]]:
    """Get interactions with optional filtering."""
    try:
        db = get_db(request)
        interactions = await db.get_interactions(limit)
        return interactions
    except Exception as e:
        logger.error(f"Error getting interactions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@interactions_router.post("",
    response_model=Dict[str, Any],
    summary="Store Agent Interaction",
    description="Store an interaction between agents.",
    response_description="Status of interaction storage.",
    responses={
        422: {"description": "Invalid interaction data"},
        500: {"description": "Internal server error"}
    }
)
async def store_interaction(interaction: AgentInteraction, request: Request) -> Dict[str, Any]:
    """Store an interaction between agents."""
    try:
        db = get_db(request)
        
        # Set timestamp to current time if not provided
        if not interaction.timestamp:
            interaction.timestamp = datetime.now(timezone.utc)
        
        # Generate run_id if not provided
        if not interaction.run_id:
            interaction.run_id = str(uuid.uuid4())
            
            # Store run data
            run_data = {
                "id": interaction.run_id,
                "agent_id": interaction.sender_id,
                "timestamp": interaction.timestamp.isoformat(),
                "status": "completed",
                "metrics": {}
            }
            await db.store_run(run_data)
        
        # Store interaction
        interaction_data = {
            "id": interaction.interaction_id,
            "sender_id": interaction.sender_id,
            "receiver_id": interaction.receiver_id,
            "topic": interaction.topic,
            "message": interaction.message,
            "interaction_type": interaction.interaction_type,
            "timestamp": interaction.timestamp.isoformat(),
            "run_id": interaction.run_id,
            "priority": interaction.priority,
            "sentiment": interaction.sentiment,
            "duration_ms": interaction.duration_ms,
            "metadata": interaction.metadata
        }
        await db.store_interaction(interaction_data)
        
        return {
            "status": "success",
            "interaction_id": interaction.interaction_id,
            "run_id": interaction.run_id,
            "topic": interaction.topic
        }
    except Exception as e:
        logger.error(f"Error storing interaction: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@agent_router.post("/message",
    response_model=Dict[str, Any],
    summary="Store Agent Interaction (Legacy)",
    description="Store an interaction between agents (legacy endpoint, use /interactions instead).",
    response_description="Status of interaction storage.",
    responses={
        422: {"description": "Invalid interaction data"},
        500: {"description": "Internal server error"}
    },
    deprecated=True
)
async def store_agent_interaction(interaction: AgentInteraction, request: Request) -> Dict[str, Any]:
    """Store an interaction between agents (legacy endpoint)."""
    # Log a warning about the deprecated endpoint
    logger.warning("The /agents/message endpoint is deprecated. Please use /interactions instead.")
    # Use the new endpoint logic
    return await store_interaction(interaction, request)

@agent_router.get("/{agent_id}/interactions",
    response_model=List[Dict[str, Any]],
    summary="Get Agent Interactions",
    description="Get all interactions associated with an agent.",
    response_description="List of agent interactions.",
    responses={
        404: {"description": "Agent not found"},
        500: {"description": "Internal server error"}
    }
)
async def get_agent_interactions(agent_id: str, request: Request) -> List[Dict[str, Any]]:
    """Get all interactions associated with an agent."""
    try:
        db = get_db(request)
        # First check if agent exists
        agent = await db.get_agent(agent_id)
        if agent is None:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
        
        interactions = await db.get_agent_interactions(agent_id)
        return interactions
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting agent interactions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@agent_router.get("/{agent_id}/runs",
    response_model=List[Dict[str, Any]],
    summary="Get Agent Runs",
    description="Get all runs associated with an agent.",
    response_description="List of agent runs.",
    responses={
        404: {"description": "Agent not found"},
        500: {"description": "Internal server error"}
    }
)
async def get_agent_runs(agent_id: str, request: Request) -> List[Dict[str, Any]]:
    """Get all runs associated with an agent."""
    try:
        db = get_db(request)
        # First check if agent exists
        agent = await db.get_agent(agent_id)
        if agent is None:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
            
        runs = await db.get_runs(agent_id)
        return runs
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting agent runs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@agent_router.get("/stats",
    response_model=Dict[str, Any],
    summary="Get Agent Statistics",
    description="Get statistics about agent interactions.",
    response_description="Agent interaction statistics."
)
async def get_agent_stats(agent_id: str, request: Request) -> Dict[str, Any]:
    """Get statistics about agent interactions."""
    try:
        db = get_db(request)
        interactions = await db.get_agent_interactions(agent_id)
        
        # Calculate basic statistics
        total_interactions = len(interactions)
        if total_interactions == 0:
            return {
                "agent_id": agent_id,
                "total_interactions": 0,
                "first_interaction": None,
                "last_interaction": None,
                "performatives": {}
            }
            
        # Sort interactions by timestamp
        interactions.sort(key=lambda x: x["timestamp"])
        
        # Count performatives
        performatives = {}
        for interaction in interactions:
            perf = interaction["performative"]
            performatives[perf] = performatives.get(perf, 0) + 1
            
        return {
            "agent_id": agent_id,
            "total_interactions": total_interactions,
            "first_interaction": interactions[0]["timestamp"],
            "last_interaction": interactions[-1]["timestamp"],
            "performatives": performatives
        }
    except Exception as e:
        logger.error(f"Error getting agent stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@agent_router.get("/stats",
    response_model=Dict[str, Any],
    summary="Get Agent Statistics",
    description="Get statistics about all agent interactions.",
    response_description="Agent interaction statistics."
)
async def get_agents_stats(request: Request) -> Dict[str, Any]:
    """Get statistics about all agent interactions."""
    try:
        db = get_db(request)
        agents = await db.get_agents()
        total_agents = len(agents)
        
        # Get all interactions
        total_interactions = 0
        interactions_per_agent = {}
        
        for agent in agents:
            agent_id = agent["id"]
            interactions = await db.get_agent_interactions(agent_id)
            num_interactions = len(interactions)
            total_interactions += num_interactions
            interactions_per_agent[agent_id] = num_interactions
        
        # Count active agents (those with interactions in the last 24 hours)
        now = datetime.now(timezone.utc)
        active_agents = 0
        for agent in agents:
            agent_id = agent["id"]
            interactions = await db.get_agent_interactions(agent_id)
            if any(
                (now - datetime.fromisoformat(i["timestamp"])).total_seconds() < 86400
                for i in interactions
            ):
                active_agents += 1
        
        return {
            "total_agents": total_agents,
            "total_interactions": total_interactions,
            "active_agents": active_agents,
            "interactions_per_agent": interactions_per_agent
        }
    except Exception as e:
        logger.error(f"Error getting agent stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@agent_router.get("",
    response_model=List[Dict[str, Any]],
    summary="Get Agents",
    description="Get all agents.",
    response_description="List of agents.",
    responses={
        500: {"description": "Internal server error"}
    }
)
async def get_agents(request: Request) -> List[Dict[str, Any]]:
    """Get all agents."""
    try:
        db = get_db(request)
        agents = await db.get_agents()
        return agents
    except Exception as e:
        logger.error(f"Error getting agents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@network_router.get("",
    response_model=Dict[str, Any],
    summary="Get Network Data",
    description="Get all nodes and relationships in the agent network graph.",
    response_description="Network graph data.",
    responses={
        500: {"description": "Internal server error"}
    }
)
async def get_network(
    request: Request,
    node_type: Optional[str] = Query(None, description="Filter by node type"),
    time_range: Optional[str] = Query(None, description="Time range filter (24h, 7d, 30d, all)")
) -> Dict[str, Any]:
    """Get all nodes and relationships in the agent network graph."""
    try:
        db = get_db(request)
        data = await db.get_network_data(node_type, time_range)
        return data
    except Exception as e:
        logger.error(f"Error getting network data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@network_router.post("/query",
    response_model=Dict[str, Any],
    summary="Query Network Data",
    description="Query network graph data with filters.",
    response_description="Network graph data.",
    responses={
        422: {"description": "Invalid query parameters"},
        500: {"description": "Internal server error"}
    }
)
async def query_network(query: GraphQuery, request: Request) -> Dict[str, Any]:
    """Query network graph data with filters."""
    try:
        db = get_db(request)
        data = await db.query_network(
            node_type=query.node_type,
            relationship_type=query.relationship_type,
            start_time=query.start_time,
            end_time=query.end_time,
            agent_ids=query.agent_ids,
            limit=query.limit,
            include_properties=query.include_properties
        )
        return data
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Error querying network data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@generate_router.post("/data",
    response_model=Dict[str, Any],
    summary="Generate Synthetic Data",
    description="Generate synthetic data for testing.",
    response_description="Generated synthetic data."
)
async def generate_data(params: SyntheticDataParams, request: Request) -> Dict[str, Any]:
    """Generate synthetic data for testing."""
    try:
        db = get_db(request)
        generator = DataGenerator()
        
        # Generate synthetic data
        data = generator.generate_synthetic_data(params.numAgents, params.numInteractions)
        
        # Store agents
        for agent in data["agents"]:
            await db.store_agent(agent)
        
        # Store interactions
        for interaction in data["interactions"]:
            await db.store_interaction(interaction)
        
        return {
            "status": "success",
            "data": data
        }
    except Exception as e:
        logger.error(f"Error generating synthetic data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@generate_router.post("/kqml",
    response_model=Dict[str, Any],
    summary="Generate Synthetic Interaction",
    description="Generate a synthetic agent interaction.",
    response_description="Generated agent interaction."
)
async def generate_kqml(request: Request) -> Dict[str, Any]:
    """Generate a synthetic agent interaction."""
    try:
        from app.kqml_handler import generate_synthetic_interaction as gen_interaction
        
        # Generate sender and receiver agents
        generator = DataGenerator()
        sender = generator.create_agent_profile("sensor", "temperature")
        receiver = generator.create_agent_profile("coordinator", "system")
        
        # Generate topic and message content
        topic = "temperature_reading"
        message = f"Current temperature is {generator.random_float(15.0, 30.0):.1f}°C"
        
        # Generate synthetic interaction
        interaction_data = gen_interaction(
            sender_id=sender["id"],
            receiver_id=receiver["id"],
            topic=topic,
            message=message,
            interaction_type="report",
            priority=generator.random_int(1, 5)
        )
        
        return interaction_data
    except Exception as e:
        logger.error(f"Error generating synthetic interaction: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@synthetic_router.post("/data",
    response_model=Dict[str, Any],
    summary="Generate Synthetic Data (Legacy)",
    description="Generate synthetic data for testing (legacy endpoint, use /generate/data instead).",
    response_description="Generated synthetic data.",
    deprecated=True
)
async def generate_synthetic_data(params: SyntheticDataParams, request: Request) -> Dict[str, Any]:
    """Generate synthetic data for testing (legacy endpoint)."""
    logger.warning("The /synthetic/data endpoint is deprecated. Please use /generate/data instead.")
    return await generate_data(params, request)

@synthetic_router.post("/kqml",
    response_model=Dict[str, Any],
    summary="Generate Synthetic Interaction (Legacy)",
    description="Generate a synthetic agent interaction (legacy endpoint, use /generate/kqml instead).",
    response_description="Generated agent interaction.",
    deprecated=True
)
async def generate_synthetic_kqml(request: Request) -> Dict[str, Any]:
    """Generate a synthetic agent interaction (legacy endpoint)."""
    logger.warning("The /synthetic/kqml endpoint is deprecated. Please use /generate/kqml instead.")
    return await generate_kqml(request)

# Admin endpoints for database management
@admin_router.post("/database/clear",
    response_model=DatabaseOperation,
    summary="Clear Database",
    description="Clear all data from the database.",
    response_description="Result of clearing the database.",
    responses={
        500: {"description": "Internal server error"}
    }
)
async def clear_database(request: Request) -> DatabaseOperation:
    """Clear all data from the database."""
    try:
        db = get_db(request)
        result = await db.clear_database()
        
        return DatabaseOperation(
            success=result.get("success", True),
            message="Database cleared successfully",
            details=result
        )
    except Exception as e:
        logger.error(f"Error clearing database: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
