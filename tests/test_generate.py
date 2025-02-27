"""Tests for the generate API endpoints."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch
import uuid
from datetime import datetime, timezone

from app.main import app
from app.data_generator import DataGenerator


@pytest.fixture
def client():
    """Test client fixture."""
    return TestClient(app)


@pytest.fixture
def mock_db():
    """Mock database fixture."""
    with patch("app.routes.get_db") as mock_get_db, \
         patch("app.main.app.state", create=True) as mock_state:
        
        # Create mock db
        db = AsyncMock()
        db.store_agent = AsyncMock()
        db.store_interaction = AsyncMock()
        
        # Set up mocks
        mock_get_db.return_value = db
        mock_state.db = db
        
        yield db


@pytest.fixture
def mock_generator():
    """Mock data generator fixture."""
    with patch("app.routes.DataGenerator") as mock:
        generator = MagicMock()
        generator.generate_synthetic_data.return_value = {
            "agents": [
                {
                    "id": "agent-1",
                    "type": "sensor",
                    "role": "temperature"
                },
                {
                    "id": "agent-2",
                    "type": "coordinator",
                    "role": "system"
                }
            ],
            "interactions": [
                {
                    "id": str(uuid.uuid4()),
                    "sender_id": "agent-1",
                    "receiver_id": "agent-2",
                    "topic": "temperature_reading",
                    "message": "Temperature is 25.5°C",
                    "interaction_type": "report",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "priority": 3
                }
            ]
        }
        generator.create_agent_profile.side_effect = [
            {"id": "agent-3", "type": "sensor", "role": "temperature"},
            {"id": "agent-4", "type": "coordinator", "role": "system"}
        ]
        generator.random_float.return_value = 22.5
        generator.random_int.return_value = 2
        mock.return_value = generator
        yield generator


@pytest.fixture
def mock_kqml_handler():
    """Mock KQML handler fixture."""
    with patch("app.kqml_handler.generate_synthetic_interaction") as mock, \
         patch("app.main.app.state", create=True) as mock_state:
        
        # Create a mock db instance for state
        if not hasattr(mock_state, 'db'):
            mock_state.db = AsyncMock()
        
        mock.return_value = {
            "interaction_id": str(uuid.uuid4()),
            "sender_id": "agent-3",
            "receiver_id": "agent-4",
            "topic": "temperature_reading",
            "message": "Current temperature is 22.5°C",
            "interaction_type": "report",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "priority": 2,
            "run_id": str(uuid.uuid4()),
            "metadata": {
                "synthetic": True,
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
        }
        yield mock


def test_generate_data(client, mock_db, mock_generator):
    """Test generating synthetic data."""
    # Create test data
    params = {
        "numAgents": 2,
        "numInteractions": 1
    }
    
    # Make request
    response = client.post("/generate/data", json=params)
    
    # Verify response
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert "agents" in response.json()["data"]
    assert "interactions" in response.json()["data"]
    assert len(response.json()["data"]["agents"]) == 2
    assert len(response.json()["data"]["interactions"]) == 1
    
    # Verify generator calls
    mock_generator.generate_synthetic_data.assert_called_once_with(2, 1)
    
    # Verify DB calls
    assert mock_db.store_agent.call_count == 2
    assert mock_db.store_interaction.call_count == 1


def test_generate_kqml(client, mock_generator, mock_kqml_handler):
    """Test generating a synthetic KQML interaction."""
    # Make request
    response = client.post("/generate/kqml")
    
    # Verify response
    assert response.status_code == 200
    assert "interaction_id" in response.json()
    assert "sender_id" in response.json()
    assert "receiver_id" in response.json()
    assert "topic" in response.json()
    assert "message" in response.json()
    assert "interaction_type" in response.json()
    assert "priority" in response.json()
    
    # Verify generator calls
    mock_generator.create_agent_profile.assert_called()
    mock_generator.random_float.assert_called_once()
    mock_generator.random_int.assert_called_once()
    
    # Verify KQML handler calls
    mock_kqml_handler.assert_called_once()


def test_legacy_generate_data(client, mock_db, mock_generator):
    """Test the legacy synthetic data generation endpoint."""
    # Create test data
    params = {
        "numAgents": 2,
        "numInteractions": 1
    }
    
    # Make request to legacy endpoint
    response = client.post("/synthetic/data", json=params)
    
    # Verify response
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert "agents" in response.json()["data"]
    assert "interactions" in response.json()["data"]
    
    # Verify generator calls
    mock_generator.generate_synthetic_data.assert_called_once_with(2, 1)


def test_legacy_generate_kqml(client, mock_generator, mock_kqml_handler):
    """Test the legacy synthetic KQML generation endpoint."""
    # Make request to legacy endpoint
    response = client.post("/synthetic/kqml")
    
    # Verify response
    assert response.status_code == 200
    assert "interaction_id" in response.json()
    assert "sender_id" in response.json()
    assert "receiver_id" in response.json()
    
    # Verify KQML handler calls
    mock_kqml_handler.assert_called_once()