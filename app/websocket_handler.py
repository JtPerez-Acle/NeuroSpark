"""WebSocket handling module."""
from enum import Enum
from typing import Dict, Set, List, Any, Optional
from fastapi import WebSocket
from pydantic import BaseModel
from loguru import logger
from datetime import datetime
from uuid import uuid4


class ConnectionType(str, Enum):
    """Type of WebSocket connection."""
    FRONTEND = "frontend"
    BLOCKCHAIN = "blockchain"


class WebSocketConnection:
    """Represents a WebSocket connection with its properties."""
    
    def __init__(self, client_id: str, connection_type: ConnectionType):
        """Initialize a new WebSocket connection."""
        if not client_id:
            raise ValueError("client_id cannot be empty")
            
        self.client_id = client_id
        self.connection_type = connection_type
        self.websocket: Optional[WebSocket] = None
        self.subscriptions: Set[str] = set()
        self.is_active = False

    def subscribe(self, event_type: str) -> None:
        """Subscribe to an event type."""
        if not event_type:
            raise ValueError("event_type cannot be empty")
        self.subscriptions.add(event_type)

    def unsubscribe(self, event_type: str) -> None:
        """Unsubscribe from an event type."""
        self.subscriptions.discard(event_type)

    async def send_message(self, message: Dict[str, Any]) -> None:
        """Send a message through the WebSocket connection."""
        if self.websocket and self.is_active:
            try:
                await self.websocket.send_json(message)
            except Exception as e:
                self.is_active = False
                raise e


class ConnectionManager:
    """Manages WebSocket connections."""
    
    def __init__(self):
        """Initialize the connection manager."""
        self.active_connections: Dict[str, WebSocketConnection] = {}

    async def connect(
        self,
        client_id: str,
        websocket: WebSocket,
        connection_type: ConnectionType
    ) -> None:
        """Accept a new WebSocket connection."""
        await websocket.accept()
        connection = WebSocketConnection(client_id, connection_type)
        connection.websocket = websocket
        connection.is_active = True
        logger.info(
            "New WebSocket connection",
            extra={
                "type": "websocket",
                "data": {
                    "connection_id": client_id,
                    "client_ip": websocket.client.host,
                    "user_agent": websocket.headers.get("user-agent")
                }
            }
        )
        self.active_connections[client_id] = connection

    async def disconnect(self, client_id: str) -> None:
        """Disconnect a WebSocket connection."""
        if client_id in self.active_connections:
            logger.info(
                "WebSocket disconnected",
                extra={
                    "type": "websocket",
                    "data": {"connection_id": client_id}
                }
            )
            connection = self.active_connections[client_id]
            connection.is_active = False
            if connection.websocket:
                try:
                    await connection.websocket.close()
                except Exception:
                    pass  # Ignore errors during close
            del self.active_connections[client_id]

    def is_connected(self, client_id: str) -> bool:
        """Check if a client is connected."""
        return client_id in self.active_connections


class WebSocketManager:
    """Manages WebSocket connections and event broadcasting."""
    
    def __init__(self):
        """Initialize the WebSocket manager."""
        self.connection_manager = ConnectionManager()

    async def connect(
        self,
        client_id: str,
        websocket: WebSocket,
        connection_type: ConnectionType
    ) -> None:
        """Connect a new client."""
        await self.connection_manager.connect(client_id, websocket, connection_type)

    async def disconnect(self, client_id: str) -> None:
        """Disconnect a client."""
        await self.connection_manager.disconnect(client_id)

    def is_connected(self, client_id: str) -> bool:
        """Check if a client is connected."""
        return self.connection_manager.is_connected(client_id)

    async def broadcast_event(
        self,
        event_type: str,
        data: Dict[str, Any]
    ) -> List[str]:
        """Broadcast an event to all subscribed clients."""
        if not event_type:
            raise ValueError("event_type cannot be empty")
        if data is None:
            raise ValueError("data cannot be None")

        message = {"type": event_type, "data": data}
        recipients = []
        
        for client_id, connection in self.connection_manager.active_connections.items():
            if event_type in connection.subscriptions:
                try:
                    await connection.send_message(message)
                    recipients.append(client_id)
                except Exception as e:
                    logger.error(
                        "Failed to send WebSocket message",
                        extra={
                            "type": "websocket",
                            "data": {
                                "connection_id": client_id,
                                "error": str(e)
                            }
                        }
                    )
                    await self.disconnect(client_id)
        
        logger.info(
            "Broadcast WebSocket message",
            extra={
                "type": "websocket",
                "data": {
                    "total_connections": len(self.connection_manager.active_connections),
                    "success_count": len(recipients),
                    "error_count": len(self.connection_manager.active_connections) - len(recipients),
                    "process_time_ms": 0  # Not implemented
                }
            }
        )
        return recipients

    async def broadcast_to_address(
        self,
        address: str,
        event_type: str,
        data: Dict[str, Any]
    ) -> List[str]:
        """Broadcast an event to a specific blockchain address."""
        if not address:
            raise ValueError("address cannot be empty")
        if not event_type:
            raise ValueError("event_type cannot be empty")
        if data is None:
            raise ValueError("data cannot be None")

        message = {"type": event_type, "data": data}
        recipients = []
        
        if address in self.connection_manager.active_connections:
            connection = self.connection_manager.active_connections[address]
            if event_type in connection.subscriptions:
                try:
                    await connection.send_message(message)
                    recipients.append(address)
                except Exception as e:
                    logger.error(
                        "Failed to send WebSocket message",
                        extra={
                            "type": "websocket",
                            "data": {
                                "connection_id": address,
                                "error": str(e)
                            }
                        }
                    )
                    await self.disconnect(address)
        
        logger.info(
            "Broadcast WebSocket message to blockchain address",
            extra={
                "type": "websocket",
                "data": {
                    "total_connections": len(self.connection_manager.active_connections),
                    "success_count": len(recipients),
                    "error_count": len(self.connection_manager.active_connections) - len(recipients),
                    "process_time_ms": 0  # Not implemented
                }
            }
        )
        return recipients
