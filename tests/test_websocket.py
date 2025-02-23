"""Test WebSocket functionality."""
import pytest
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocket
from typing import List, Dict, Any
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from app.websocket_handler import (
    WebSocketManager,
    ConnectionManager,
    WebSocketConnection,
    ConnectionType
)

# Test WebSocket Connection Management
async def test_websocket_connection_creation():
    """Test creating a new WebSocket connection."""
    manager = WebSocketManager()
    client_id = "test_client"
    connection = WebSocketConnection(
        client_id=client_id,
        connection_type=ConnectionType.FRONTEND
    )
    
    assert connection.client_id == client_id
    assert connection.connection_type == ConnectionType.FRONTEND
    assert connection.subscriptions == set()

async def test_websocket_connection_subscription():
    """Test subscribing to events."""
    manager = WebSocketManager()
    client_id = "test_client"
    connection = WebSocketConnection(
        client_id=client_id,
        connection_type=ConnectionType.FRONTEND
    )
    
    # Subscribe to events
    events = {"agent_update", "graph_update"}
    for event in events:
        connection.subscribe(event)
    
    assert connection.subscriptions == events

# Test Connection Manager
async def test_connection_manager_add_connection():
    """Test adding a connection to the manager."""
    manager = ConnectionManager()
    client_id = "test_client"
    mock_websocket = AsyncMock()
    mock_websocket.accept = AsyncMock()
    mock_websocket.close = AsyncMock()
    
    await manager.connect(
        client_id=client_id,
        websocket=mock_websocket,
        connection_type=ConnectionType.FRONTEND
    )
    
    assert client_id in manager.active_connections
    assert len(manager.active_connections) == 1
    mock_websocket.accept.assert_awaited_once()

async def test_connection_manager_remove_connection():
    """Test removing a connection from the manager."""
    manager = ConnectionManager()
    client_id = "test_client"
    mock_websocket = AsyncMock()
    mock_websocket.accept = AsyncMock()
    mock_websocket.close = AsyncMock()
    
    await manager.connect(
        client_id=client_id,
        websocket=mock_websocket,
        connection_type=ConnectionType.FRONTEND
    )
    await manager.disconnect(client_id)
    
    assert client_id not in manager.active_connections
    assert len(manager.active_connections) == 0
    mock_websocket.close.assert_awaited_once()

# Test Event Broadcasting
async def test_broadcast_event():
    """Test broadcasting events to subscribed clients."""
    manager = WebSocketManager()
    client_id = "test_client"
    mock_websocket = AsyncMock()
    mock_websocket.accept = AsyncMock()
    mock_websocket.send_json = AsyncMock()
    
    # Connect and subscribe client
    await manager.connect(
        client_id=client_id,
        websocket=mock_websocket,
        connection_type=ConnectionType.FRONTEND
    )
    manager.connection_manager.active_connections[client_id].subscribe("agent_update")
    
    # Mock event data
    event_data = {
        "type": "agent_update",
        "data": {"agent_id": "agent1", "status": "active"}
    }
    
    # Test broadcasting
    recipients = await manager.broadcast_event(
        event_type="agent_update",
        data=event_data
    )
    assert len(recipients) == 1
    assert client_id in recipients
    mock_websocket.send_json.assert_awaited_once_with({
        "type": "agent_update",
        "data": event_data
    })

# Test Agent-Specific Events
async def test_agent_specific_broadcast():
    """Test broadcasting events to specific agents."""
    manager = WebSocketManager()
    agent_id = "agent1"
    mock_websocket = AsyncMock()
    mock_websocket.accept = AsyncMock()
    mock_websocket.send_json = AsyncMock()
    
    # Connect and subscribe agent
    await manager.connect(
        client_id=agent_id,
        websocket=mock_websocket,
        connection_type=ConnectionType.AGENT
    )
    manager.connection_manager.active_connections[agent_id].subscribe("command")
    
    # Mock command data
    command_data = {
        "type": "command",
        "data": {"action": "measure_temperature"}
    }
    
    # Test broadcasting to specific agent
    recipients = await manager.broadcast_to_agent(
        agent_id=agent_id,
        event_type="command",
        data=command_data
    )
    assert len(recipients) == 1
    assert agent_id in recipients
    mock_websocket.send_json.assert_awaited_once_with({
        "type": "command",
        "data": command_data
    })

# Test Connection State Management
async def test_connection_state_tracking():
    """Test tracking connection state changes."""
    manager = WebSocketManager()
    client_id = "test_client"
    mock_websocket = AsyncMock()
    mock_websocket.accept = AsyncMock()
    mock_websocket.close = AsyncMock()
    
    # Test connection state changes
    await manager.connect(
        client_id=client_id,
        websocket=mock_websocket,
        connection_type=ConnectionType.FRONTEND
    )
    assert manager.is_connected(client_id)
    mock_websocket.accept.assert_awaited_once()
    
    await manager.disconnect(client_id)
    assert not manager.is_connected(client_id)
    mock_websocket.close.assert_awaited_once()

# Test Error Handling
async def test_invalid_subscription():
    """Test handling invalid subscription requests."""
    connection = WebSocketConnection(
        client_id="test_client",
        connection_type=ConnectionType.FRONTEND
    )
    
    with pytest.raises(ValueError):
        connection.subscribe("")  # Empty event type
    
    with pytest.raises(ValueError):
        connection.subscribe(None)  # None event type

async def test_invalid_broadcast():
    """Test handling invalid broadcast requests."""
    manager = WebSocketManager()
    
    with pytest.raises(ValueError):
        await manager.broadcast_event("", {})  # Empty event type
    
    with pytest.raises(ValueError):
        await manager.broadcast_event("test_event", None)  # None data
