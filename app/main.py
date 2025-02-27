"""Main application module."""
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import uuid
from loguru import logger
import random

from .database import create_database
from .monitoring.metrics import instrument_app
from .monitoring.logging_config import setup_logging
from .websocket_handler import ConnectionManager
from .kqml_handler import process_interaction, generate_synthetic_interaction
from .data_generator import DataGenerator
from .routes import agent_router, network_router, synthetic_router, generate_router, interactions_router, admin_router

# Configure logging
setup_logging()

# Initialize FastAPI app
app = FastAPI(title="Agent Interaction Backend")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize WebSocket connection manager
manager = ConnectionManager()

# Add routers
app.include_router(agent_router, prefix="/agents", tags=["agents"])
app.include_router(network_router, prefix="/network", tags=["network"])
app.include_router(synthetic_router, prefix="/synthetic", tags=["synthetic"])
app.include_router(generate_router, prefix="/generate", tags=["generate"])
app.include_router(interactions_router, prefix="/interactions", tags=["interactions"])
app.include_router(admin_router, prefix="/admin", tags=["admin"])

# Initialize database
@app.on_event("startup")
async def startup():
    """Initialize the application."""
    try:
        db = await create_database()
        app.state.db = db
        logger.info("Successfully initialized ArangoDB connection")
    except Exception as e:
        logger.error(f"Failed to initialize ArangoDB: {e}")
        # Don't raise here, let the app start and handle DB errors per-request
        app.state.db = None

@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    """Ensure database is connected for each request."""
    if not request.app.state.db:
        try:
            request.app.state.db = await create_database()
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"detail": "Database connection failed"}
            )
    response = await call_next(request)
    return response

@app.on_event("shutdown")
async def shutdown():
    """Clean up the application."""
    if hasattr(app.state, "db"):
        await app.state.db.disconnect()

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Agent Interaction Backend API"}

# Add WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Initialize metrics
instrument_app(app)