"""API routes for the application."""
from fastapi import APIRouter, Request, HTTPException, Query, Path, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime, timezone
import asyncio
from loguru import logger

from .config import Settings
from .models import (
    ScenarioParams, SyntheticDataParams, DatabaseOperation,
    NaturalLanguageQuery, GraphData
)
from .data_generator import DataGenerator

# Define routers
generate_router = APIRouter()
admin_router = APIRouter()
compat_router = APIRouter(tags=["compatibility"])  # For backward compatibility

def get_db(request: Request):
    """Get a database connection from the request state."""
    if hasattr(request.app.state, "db"):
        return request.app.state.db
    else:
        raise HTTPException(status_code=500, detail="Database connection not available")

# Generate endpoints for synthetic blockchain data
@generate_router.post("/data",
    response_model=Dict[str, Any],
    summary="Generate Synthetic Blockchain Data",
    description="Generate synthetic blockchain data for testing.",
    response_description="Generated synthetic blockchain data."
)
async def generate_data(params: SyntheticDataParams, request: Request) -> Dict[str, Any]:
    """Generate synthetic blockchain data for testing."""
    try:
        db = get_db(request)
        generator = DataGenerator()
        
        # Generate synthetic blockchain data
        data = generator.generate_blockchain_data(params.numAgents, params.numInteractions)
        
        # Store wallets
        for wallet in data["agents"]:
            # Store wallet using appropriate method
            await db.store_wallet(wallet)
        
        # Store transactions
        for transaction in data["interactions"]:
            if "metadata" in transaction and "transaction" in transaction["metadata"]:
                tx_data = transaction["metadata"]["transaction"]
                await db.store_transaction(tx_data)
            else:
                # Skip invalid transactions
                logger.warning(f"Skipping invalid transaction without metadata: {transaction.get('interaction_id', 'unknown')}")
        
        return {
            "status": "success",
            "data": data
        }
    except Exception as e:
        logger.error(f"Error generating synthetic blockchain data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@generate_router.post("/scenario",
    response_model=Dict[str, Any],
    summary="Generate Blockchain Scenario Data",
    description="Generate synthetic blockchain data based on a specific scenario (dex, lending, nft, token_transfer).",
    response_description="Generated blockchain scenario data."
)
async def generate_scenario_data(params: ScenarioParams, request: Request) -> Dict[str, Any]:
    """Generate blockchain scenario-based synthetic data."""
    try:
        # Debug logging
        logger.info(f"Received blockchain scenario generation request: {params.model_dump()}")
        
        db = get_db(request)
        generator = DataGenerator(scenario=params.scenario)
        
        # Generate blockchain scenario-specific data with optional blocks parameter
        kwargs = {}
        if params.blocks is not None:
            kwargs["blocks"] = params.blocks
            
        logger.info(f"Generating blockchain scenario data for {params.scenario} with {params.numAgents} wallets, {params.numInteractions} transactions")
        data = generator.generate_blockchain_data(params.numAgents, params.numInteractions, **kwargs)
        
        # Store wallets
        for wallet in data["agents"]:
            await db.store_wallet(wallet)
        
        # Store transactions
        for transaction in data["interactions"]:
            if "metadata" in transaction and "transaction" in transaction["metadata"]:
                tx_data = transaction["metadata"]["transaction"]
                await db.store_transaction(tx_data)
            else:
                # Skip invalid transactions
                logger.warning(f"Skipping invalid transaction without metadata: {transaction.get('interaction_id', 'unknown')}")
        
        logger.info(f"Successfully generated blockchain scenario data: {params.scenario}")
        return {
            "status": "success",
            "scenario": params.scenario,
            "blockchain": "ethereum",
            "data": data
        }
    except Exception as e:
        logger.error(f"Error generating blockchain scenario data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@generate_router.post("/transaction",
    response_model=Dict[str, Any],
    summary="Generate Blockchain Transaction",
    description="Generate a blockchain transaction between wallets.",
    response_description="Generated blockchain transaction."
)
async def generate_transaction(request: Request) -> Dict[str, Any]:
    """Generate a blockchain transaction between wallets."""
    try:
        # Generate sender and receiver wallets
        generator = DataGenerator()
        sender = generator.create_wallet("EOA", "trader")
        receiver = generator.create_wallet("EOA", "trader")
        
        # Generate blockchain transaction
        transaction = generator.generate_transaction(sender, receiver)
        
        # Get database connection
        db = get_db(request)
        
        # Store the wallets
        await db.store_wallet(sender)
        await db.store_wallet(receiver)
        
        # Extract the transaction from metadata
        if "metadata" in transaction and "transaction" in transaction["metadata"]:
            tx_data = transaction["metadata"]["transaction"]
            # Store the transaction
            await db.store_transaction(tx_data)
        else:
            # Create a basic transaction if metadata is missing
            tx_data = {
                "hash": f"0x{uuid.uuid4().hex}",
                "from_address": sender["address"],
                "to_address": receiver["address"],
                "chain": "ethereum",
                "value": 0,
                "gas_used": 21000,
                "gas_price": 20000000000,
                "block_number": 123456,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "status": "success"
            }
            await db.store_transaction(tx_data)
            # Add transaction data to the interaction
            if "metadata" not in transaction:
                transaction["metadata"] = {}
            transaction["metadata"]["transaction"] = tx_data
        
        return {
            "status": "success",
            "sender": sender,
            "receiver": receiver,
            "transaction": transaction
        }
    except Exception as e:
        logger.error(f"Error generating blockchain transaction: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
        
@generate_router.get("/transaction",
    response_model=Dict[str, Any],
    summary="Generate Blockchain Transaction Sample",
    description="Generate a sample blockchain transaction without storing it.",
    response_description="Generated blockchain transaction sample."
)
async def generate_transaction_sample(request: Request) -> Dict[str, Any]:
    """Generate a sample blockchain transaction without storing it."""
    try:
        # Generate sender and receiver wallets
        generator = DataGenerator()
        sender = generator.create_wallet("EOA", "trader")
        receiver = generator.create_wallet("contract", "token")
        
        # Generate blockchain transaction
        transaction = generator.generate_transaction(sender, receiver)
        
        return {
            "status": "success",
            "sender": sender,
            "receiver": receiver,
            "transaction": transaction
        }
    except Exception as e:
        logger.error(f"Error generating blockchain transaction sample: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Admin endpoints for database management
@admin_router.post("/database/clear",
    response_model=DatabaseOperation,
    summary="Clear Database",
    description="Clear all data from the database.",
    response_description="Operation result."
)
async def clear_database(request: Request) -> DatabaseOperation:
    """Clear all data from the database."""
    try:
        # Get database connection from request state
        db = get_db(request)
        
        # Clear the database
        result = await db.clear_database()
        
        return DatabaseOperation(
            operation="clear_database",
            status="success",
            timestamp=datetime.now(timezone.utc).isoformat(),
            details=result
        )
    except Exception as e:
        logger.error(f"Error clearing database: {str(e)}")
        return DatabaseOperation(
            operation="clear_database",
            status="error",
            timestamp=datetime.now(timezone.utc).isoformat(),
            details=str(e)
        )

@admin_router.post("/database/reset",
    response_model=DatabaseOperation,
    summary="Reset Database",
    description="Reset the database to its initial state.",
    response_description="Operation result."
)
async def reset_database(request: Request) -> DatabaseOperation:
    """Reset the database to its initial state."""
    try:
        # Get database connection from request state
        db = get_db(request)
        
        # Reset the database
        result = await db.reset_database()
        
        return DatabaseOperation(
            operation="reset_database",
            status="success",
            timestamp=datetime.now(timezone.utc).isoformat(),
            details=result
        )
    except Exception as e:
        logger.error(f"Error resetting database: {str(e)}")
        return DatabaseOperation(
            operation="reset_database",
            status="error",
            timestamp=datetime.now(timezone.utc).isoformat(),
            details=str(e)
        )

@admin_router.get("/database/stats",
    response_model=Dict[str, Any],
    summary="Database Statistics",
    description="Get statistics about the database.",
    response_description="Database statistics."
)
async def database_stats(request: Request) -> Dict[str, Any]:
    """Get statistics about the database."""
    try:
        # Get database connection from request state
        db = get_db(request)
        
        # Get database statistics
        stats = await db.get_database_stats()
        
        return stats
    except Exception as e:
        logger.error(f"Error retrieving database statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Backward compatibility API endpoints for tests (agent-based model)

@compat_router.post("/agents", 
    response_model=Dict[str, Any],
    summary="Create Agent (Compatibility)",
    description="[Compatibility] Create an agent."
)
async def create_agent(agent: Dict[str, Any], request: Request) -> Dict[str, Any]:
    """Create an agent (compatibility endpoint)."""
    try:
        # Map to a wallet for blockchain model
        wallet_data = {
            "address": agent.get("id", f"0x{agent['id']}") if agent.get("id") else f"0x{uuid.uuid4().hex}",
            "chain": "ethereum",
            "wallet_type": "EOA",
            "role": agent.get("role", "user"),
            "tags": [agent.get("type", "human"), agent.get("role", "user")],
            "balance": 0.0,
            "first_seen": datetime.now(timezone.utc).isoformat(),
            "last_active": datetime.now(timezone.utc).isoformat()
        }
        
        # Get database connection
        db = get_db(request)
        
        # Store wallet
        await db.store_wallet(wallet_data)
        
        return {
            "status": "success",
            "agent": agent
        }
    except Exception as e:
        logger.error(f"Error creating agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@compat_router.post("/agents/message",
    response_model=Dict[str, Any],
    summary="Send Agent Message (Compatibility)",
    description="[Compatibility] Send a message between agents."
)
async def send_agent_message(message: Dict[str, Any], request: Request) -> Dict[str, Any]:
    """Send a message between agents (compatibility endpoint)."""
    try:
        # Map to a transaction for blockchain model
        transaction_data = {
            "hash": f"0x{uuid.uuid4().hex}",
            "from_address": message.get("sender_id", ""),
            "to_address": message.get("receiver_id", ""),
            "chain": "ethereum",
            "value": 0,
            "gas_used": 21000,
            "gas_price": 20000000000,
            "block_number": 123456,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "success",
            "message": message.get("message", ""),
            "topic": message.get("topic", ""),
            "interaction_type": message.get("interaction_type", "message")
        }
        
        # Get database connection
        db = get_db(request)
        
        # Store transaction
        await db.store_transaction(transaction_data)
        
        return {
            "status": "success",
            "interaction_id": transaction_data["hash"],
            "message": message
        }
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@compat_router.get("/agents/{agent_id}/runs",
    response_model=Dict[str, Any],
    summary="Get Agent Runs (Compatibility)",
    description="[Compatibility] Get runs for an agent."
)
async def get_agent_runs(agent_id: str, request: Request) -> Dict[str, Any]:
    """Get runs for an agent (compatibility endpoint)."""
    return {
        "agent_id": agent_id,
        "runs": []
    }

@compat_router.get("/agents/{agent_id}/interactions",
    response_model=Dict[str, Any],
    summary="Get Agent Interactions (Compatibility)",
    description="[Compatibility] Get interactions for an agent."
)
async def get_agent_interactions(agent_id: str, request: Request) -> Dict[str, Any]:
    """Get interactions for an agent (compatibility endpoint)."""
    try:
        # Map to wallet transactions for blockchain model
        db = get_db(request)
        
        transactions = await db.get_wallet_transactions(
            address=agent_id,
            limit=20
        )
        
        # Convert transactions to interaction format
        interactions = []
        for tx in transactions:
            interactions.append({
                "interaction_id": tx["hash"],
                "sender_id": tx["from_address"],
                "receiver_id": tx["to_address"],
                "timestamp": tx["timestamp"],
                "topic": tx.get("topic", "ethereum_transaction"),
                "message": tx.get("message", "Blockchain transaction"),
                "interaction_type": tx.get("interaction_type", "transaction")
            })
        
        return {
            "agent_id": agent_id,
            "interactions": interactions
        }
    except Exception as e:
        logger.error(f"Error getting agent interactions: {e}")
        return {
            "agent_id": agent_id,
            "interactions": []
        }

@compat_router.post("/synthetic/data",
    response_model=Dict[str, Any],
    summary="Generate Synthetic Data (Compatibility)",
    description="[Compatibility] Generate synthetic data."
)
async def generate_synthetic_data(params: Dict[str, Any], request: Request) -> Dict[str, Any]:
    """Generate synthetic data (compatibility endpoint)."""
    try:
        # Map to blockchain data generation
        num_agents = params.get("numAgents", 10)
        num_interactions = params.get("numInteractions", 20)
        
        generator = DataGenerator()
        data = generator.generate_blockchain_data(num_agents, num_interactions)
        
        # Store wallets and transactions
        db = get_db(request)
        for wallet in data["agents"]:
            await db.store_wallet(wallet)
        
        for transaction in data["interactions"]:
            await db.store_transaction(transaction)
        
        return {
            "status": "success",
            "data": data
        }
    except Exception as e:
        logger.error(f"Error generating synthetic data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@compat_router.get("/network",
    response_model=Dict[str, Any],
    summary="Get Network (Compatibility)",
    description="[Compatibility] Get network data."
)
async def get_network(
    request: Request,
    node_type: Optional[str] = None,
    time_range: Optional[str] = None
) -> Dict[str, Any]:
    """Get network data (compatibility endpoint)."""
    try:
        # Map to blockchain network
        db = get_db(request)
        
        # Convert agent node_type to wallet/contract type
        node_type_map = {
            "Agent": "wallet",
            "Human": "wallet",
            "AI": "contract"
        }
        
        wallet_type = node_type_map.get(node_type) if node_type else None
        
        # Get blockchain network data
        network = await db.get_network_data(
            node_type=wallet_type,
            time_range=time_range
        )
        
        return network
    except Exception as e:
        logger.error(f"Error getting network data: {e}")
        return {
            "nodes": [],
            "edges": []
        }

@compat_router.post("/network/query",
    response_model=Dict[str, Any],
    summary="Query Network (Compatibility)",
    description="[Compatibility] Query network data."
)
async def query_network(query: Dict[str, Any], request: Request) -> Dict[str, Any]:
    """Query network data (compatibility endpoint)."""
    try:
        # Map to blockchain network query
        db = get_db(request)
        
        # Convert parameters
        network = await db.query_network(
            node_type=query.get("node_type"),
            relationship_type=query.get("relationship_type"),
            start_time=query.get("start_time"),
            end_time=query.get("end_time"),
            agent_ids=query.get("agent_ids"),
            limit=query.get("limit"),
            include_properties=query.get("include_properties", True)
        )
        
        return network
    except Exception as e:
        logger.error(f"Error querying network data: {e}")
        raise HTTPException(status_code=422, detail=f"Invalid query parameters: {str(e)}")