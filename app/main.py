"""Main application module for KQML Parser Backend."""
import uvicorn
import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any

from .routes import agents_router, network_router, synthetic_router
from .database import Neo4jDatabase, InMemoryDatabase

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="KQML Parser Backend",
    description="Backend service for parsing and storing KQML messages",
    version="1.0.0",
    redirect_slashes=False  # Prevent automatic redirects
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup."""
    if os.getenv("TESTING", "false").lower() == "true":
        db = InMemoryDatabase()
    else:
        db = Neo4jDatabase(
            uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            username=os.getenv("NEO4J_USER", "neo4j"),
            password=os.getenv("NEO4J_PASSWORD", "testpassword")
        )
    
    try:
        await db.connect()
        app.state.db = db
        logger.info("Successfully connected to database")
    except Exception as e:
        logger.error(f"Failed to connect to database: {str(e)}")
        raise e

@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown."""
    if hasattr(app.state, "db"):
        await app.state.db.disconnect()
        logger.info("Database connection closed")

# Include routers
app.include_router(agents_router, prefix="/agents", tags=["agents"])
app.include_router(network_router, prefix="/network", tags=["network"])
app.include_router(synthetic_router, prefix="/synthetic", tags=["synthetic"])

@app.get("/",
    response_model=Dict[str, Any],
    summary="Get API Information",
    description="Returns basic information about the API.",
    response_description="API information."
)
async def root():
    """Root endpoint that returns API information."""
    return {
        "status": "running",
        "service": "KQML Parser Backend",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)