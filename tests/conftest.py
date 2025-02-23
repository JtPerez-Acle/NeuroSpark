"""Test configuration module."""
import pytest
from datetime import datetime, timedelta, timezone
import uuid
from httpx import AsyncClient
from fastapi import FastAPI
from typing import List, Dict
import os

from app.main import app
from app.database import InMemoryDatabase
from app.models import RunData, InteractionData

@pytest.fixture(autouse=True)
def setup_test_env():
    """Set up test environment."""
    os.environ["TESTING"] = "true"
    yield
    os.environ.pop("TESTING", None)

@pytest.fixture
async def test_db():
    """Create test database."""
    db = InMemoryDatabase()
    await db.connect()
    yield db
    await db.disconnect()

@pytest.fixture
async def test_app(test_db) -> FastAPI:
    """Create test application with in-memory database."""
    app.dependency_overrides = {}  # Reset any existing overrides
    app.state.db = test_db
    return app

@pytest.fixture
async def async_client(test_app):
    """Create async test client."""
    async with AsyncClient(app=test_app, base_url="http://test") as client:
        yield client

@pytest.fixture
def client(test_app):
    return test_app

@pytest.fixture
def test_timestamp():
    """Fixture to provide a test timestamp."""
    return datetime.now(timezone.utc).isoformat()

@pytest.fixture
def test_agent_id():
    """Fixture to provide a unique test agent ID."""
    return f"test_agent_{uuid.uuid4().hex[:8]}"

@pytest.fixture
def test_run_id():
    """Fixture to provide a unique test run ID."""
    return f"test_run_{uuid.uuid4().hex[:8]}"

@pytest.fixture
def sample_kqml_message():
    """Fixture to provide a sample KQML message."""
    return "(tell temperature 25 :sender sensor1 :receiver agent1)"

@pytest.fixture
async def sample_run(test_db, test_run_id, test_timestamp) -> RunData:
    """Fixture to provide a sample run."""
    run_data = await test_db.create_run(test_run_id, test_timestamp)
    return run_data

@pytest.fixture
async def sample_interaction(test_db, test_timestamp, sample_run) -> InteractionData:
    """Fixture to provide a sample interaction."""
    interaction = {
        "performative": "tell",
        "content": "temperature 25",
        "sender": "sensor1",
        "receiver": "agent1",
        "timestamp": test_timestamp,
        "run_id": sample_run["run_id"] if sample_run else None
    }
    await test_db.store_interaction(interaction)
    return interaction

@pytest.fixture
async def test_agents(test_db) -> List[str]:
    """Fixture to provide test agents."""
    agents = ["agent1", "agent2", "sensor1", "sensor2"]
    for agent_id in agents:
        await test_db.create_agent(agent_id)
    return agents

@pytest.fixture
async def test_runs(test_db) -> List[RunData]:
    """Fixture to provide test runs."""
    runs = []
    for i in range(3):
        timestamp = (datetime.now(timezone.utc) - timedelta(hours=i)).isoformat()
        run_id = f"test_run_{i}"
        run_data = await test_db.create_run(run_id, timestamp)
        runs.append(run_data)
    return runs

@pytest.fixture
async def test_interactions(test_db, test_agents, test_runs) -> List[InteractionData]:
    """Fixture to provide test interactions."""
    interactions = []
    for i, run in enumerate(test_runs):
        for j in range(2):
            interaction = {
                "performative": "tell",
                "content": f"data_{i}_{j}",
                "sender": test_agents[i % len(test_agents)],
                "receiver": test_agents[(i + 1) % len(test_agents)],
                "timestamp": (datetime.now(timezone.utc) - timedelta(hours=i)).isoformat(),
                "run_id": run["run_id"]
            }
            await test_db.store_interaction(interaction)
            interactions.append(interaction)
    return interactions
