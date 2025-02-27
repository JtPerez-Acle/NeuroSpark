"""Tests for the interactions API endpoints."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch
import uuid
from datetime import datetime, timezone

from app.main import app


@pytest.fixture
def client():
    """Test client fixture."""
    return TestClient(app)


@pytest.fixture
def mock_db():
    """Mock database fixture."""
    with patch("app.routes.get_db") as mock_get_db, \
         patch("app.main.app.state") as mock_state:
        
        # Create mock db
        db = AsyncMock()
        db.store_interaction = AsyncMock()
        db.get_interactions = AsyncMock(return_value=[])
        db.get_interaction = AsyncMock(return_value=None)
        db.store_run = AsyncMock()
        
        # Set up mocks
        mock_get_db.return_value = db
        mock_state.db = db
        
        yield db


def test_store_interaction(client, mock_db):
    """Test storing an interaction."""
    # Setup mock return values
    interaction_id = str(uuid.uuid4())
    run_id = str(uuid.uuid4())
    
    # Create test data
    interaction_data = {
        "interaction_id": interaction_id,
        "sender_id": "agent-1",
        "receiver_id": "agent-2",
        "topic": "test-topic",
        "message": "Hello, Agent 2!",
        "interaction_type": "message",
        "priority": 3,
        "sentiment": 0.8,
        "duration_ms": 150,
        "metadata": {"test": True}
    }
    
    # Make request
    response = client.post("/interactions", json=interaction_data)
    
    # Verify response
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["interaction_id"] == interaction_id
    assert response.json()["topic"] == "test-topic"
    
    # Verify DB calls
    mock_db.store_interaction.assert_called_once()
    call_args = mock_db.store_interaction.call_args[0][0]
    assert call_args["id"] == interaction_id
    assert call_args["sender_id"] == "agent-1"
    assert call_args["receiver_id"] == "agent-2"
    assert call_args["topic"] == "test-topic"
    assert call_args["message"] == "Hello, Agent 2!"
    assert call_args["priority"] == 3
    assert call_args["sentiment"] == 0.8


def test_get_interactions(client, mock_db):
    """Test getting all interactions."""
    # Setup mock return values
    timestamp = datetime.now(timezone.utc).isoformat()
    mock_db.get_interactions.return_value = [
        {
            "id": str(uuid.uuid4()),
            "sender_id": "agent-1",
            "receiver_id": "agent-2",
            "topic": "topic-1",
            "message": "Hello",
            "interaction_type": "message",
            "timestamp": timestamp,
            "priority": 3,
            "sentiment": 0.5,
            "duration_ms": 100,
            "run_id": str(uuid.uuid4()),
            "metadata": {}
        },
        {
            "id": str(uuid.uuid4()),
            "sender_id": "agent-2",
            "receiver_id": "agent-1",
            "topic": "topic-1",
            "message": "Hi there",
            "interaction_type": "response",
            "timestamp": timestamp,
            "priority": 2,
            "sentiment": 0.7,
            "duration_ms": 80,
            "run_id": str(uuid.uuid4()),
            "metadata": {}
        }
    ]
    
    # Make request
    response = client.get("/interactions")
    
    # Verify response
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["sender_id"] == "agent-1"
    assert response.json()[1]["sender_id"] == "agent-2"
    
    # Verify DB calls
    mock_db.get_interactions.assert_called_once()


def test_get_interaction(client, mock_db):
    """Test getting a specific interaction."""
    # Setup mock return values
    interaction_id = str(uuid.uuid4())
    timestamp = datetime.now(timezone.utc).isoformat()
    mock_db.get_interaction.return_value = {
        "id": interaction_id,
        "sender_id": "agent-1",
        "receiver_id": "agent-2",
        "topic": "topic-1",
        "message": "Hello",
        "interaction_type": "message",
        "timestamp": timestamp,
        "priority": 3,
        "sentiment": 0.5,
        "duration_ms": 100,
        "run_id": str(uuid.uuid4()),
        "metadata": {}
    }
    
    # Make request
    response = client.get(f"/interactions/{interaction_id}")
    
    # Verify response
    assert response.status_code == 200
    assert response.json()["id"] == interaction_id
    assert response.json()["sender_id"] == "agent-1"
    assert response.json()["receiver_id"] == "agent-2"
    
    # Verify DB calls
    mock_db.get_interaction.assert_called_once_with(interaction_id)


def test_get_interaction_not_found(client, mock_db):
    """Test getting a non-existent interaction."""
    # Setup mock return values
    interaction_id = str(uuid.uuid4())
    mock_db.get_interaction.return_value = None
    
    # Make request
    response = client.get(f"/interactions/{interaction_id}")
    
    # Verify response
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]
    
    # Verify DB calls
    mock_db.get_interaction.assert_called_once_with(interaction_id)


def test_store_interaction_error(client, mock_db):
    """Test storing an interaction with an error."""
    # Setup mock return values
    mock_db.store_interaction.side_effect = Exception("Database error")
    
    # Create test data
    interaction_data = {
        "sender_id": "agent-1",
        "receiver_id": "agent-2",
        "topic": "test-topic",
        "message": "Hello, Agent 2!",
        "interaction_type": "message"
    }
    
    # Make request
    response = client.post("/interactions", json=interaction_data)
    
    # Verify response
    assert response.status_code == 500
    assert "Database error" in response.json()["detail"]
    
    # Verify DB calls
    mock_db.store_interaction.assert_called_once()


def test_legacy_endpoint_redirect(client, mock_db):
    """Test that the legacy endpoint redirects to the new one."""
    # Create test data
    interaction_id = str(uuid.uuid4())
    interaction_data = {
        "interaction_id": interaction_id,
        "sender_id": "agent-1",
        "receiver_id": "agent-2",
        "topic": "test-topic",
        "message": "Hello, Agent 2!",
        "interaction_type": "message"
    }
    
    # Make request to legacy endpoint
    response = client.post("/agents/message", json=interaction_data)
    
    # Verify response
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["interaction_id"] == interaction_id
    
    # Verify DB calls
    mock_db.store_interaction.assert_called_once()