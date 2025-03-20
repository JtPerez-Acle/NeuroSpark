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
        data = generator.generate_blockchain_data(params.numWallets, params.numTransactions)
        
        # Store wallets
        for wallet in data["wallets"]:
            # Store wallet using appropriate method
            await db.store_wallet(wallet)
        
        # Store transactions
        for transaction in data["transactions"]:
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
            
        logger.info(f"Generating blockchain scenario data for {params.scenario} with {params.numWallets} wallets, {params.numTransactions} transactions")
        data = generator.generate_blockchain_data(params.numWallets, params.numTransactions, **kwargs)
        
        # Store wallets
        for wallet in data["wallets"]:
            await db.store_wallet(wallet)
        
        # Store transactions
        for transaction in data["transactions"]:
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
        
        # Ensure blockchain collections are set up
        await db.setup_blockchain_collections()
        
        # Store the wallets
        await db.store_wallet(sender)
        await db.store_wallet(receiver)
        
        # Extract the transaction from metadata
        if "metadata" in transaction and "transaction" in transaction["metadata"]:
            tx_data = transaction["metadata"]["transaction"]
            
            # Ensure transaction has proper key format for blockchain routes
            if "from_address" not in tx_data and "from" in tx_data:
                tx_data["from_address"] = tx_data["from"]
                
            if "to_address" not in tx_data and "to" in tx_data:
                tx_data["to_address"] = tx_data["to"]
                
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

# Legacy compatibility endpoints removed - migrated to blockchain architecture