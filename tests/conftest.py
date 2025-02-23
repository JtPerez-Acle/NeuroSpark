"""Test configuration."""
import os
import tempfile
import pytest
import pytest_asyncio
import httpx
from typing import Dict, Any, List
from fastapi import FastAPI
from httpx import AsyncClient
from app.database.core.database import Neo4jDatabase

# Set test environment variables if not already set
os.environ.setdefault("NEO4J_URI", "bolt://localhost:7687")
os.environ.setdefault("NEO4J_USER", "neo4j")
os.environ.setdefault("NEO4J_PASSWORD", "kqml_dev_2025")

@pytest.fixture(scope="session")
def test_log_dir():
    """Create a temporary directory for test logs."""
    with tempfile.TemporaryDirectory() as temp_dir:
        os.environ["TEST_LOG_DIR"] = temp_dir
        os.environ["TESTING"] = "1"
        yield temp_dir

# Import app after setting up test log directory
from app.main import app

@pytest_asyncio.fixture
async def test_db_neo4j():
    """Create test database."""
    db = Neo4jDatabase(
        uri=os.environ["NEO4J_URI"],
        username=os.environ["NEO4J_USER"],
        password=os.environ["NEO4J_PASSWORD"]
    )
    await db.connect()
    
    try:
        # Clean up any existing data
        async with await db.get_session() as session:
            await session.run("MATCH (n) DETACH DELETE n")
        yield db
    finally:
        await db.disconnect()

@pytest_asyncio.fixture
async def test_app(test_db_neo4j) -> FastAPI:
    """Create test FastAPI application."""
    app.state.db = test_db_neo4j
    return app

@pytest_asyncio.fixture
async def async_client(test_app):
    """Create async test client."""
    base_url = "http://test"
    transport = httpx.ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url=base_url) as client:
        yield client

@pytest.fixture
def test_agents() -> List[Dict[str, Any]]:
    """Get test agents data."""
    return [
        {
            "id": "test_agent",
            "type": "human",
            "role": "system"
        }
    ]
