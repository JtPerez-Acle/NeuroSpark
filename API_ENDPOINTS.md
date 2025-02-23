# API Endpoints Documentation

This document provides detailed information about all available API endpoints in the KQML Parser Backend [0.2.3].

## Base URL

```
http://localhost:8000
```

## WebSocket Endpoint

```
ws://localhost:8000/ws
```

Provides real-time updates for agent interactions and system events.

## REST Endpoints

### Agent Operations

#### Store Agent Message
- **Endpoint**: `POST /agents/message`
- **Description**: Store a KQML message from an agent
- **Request Body**:
  ```json
  {
    "message": "string (KQML message)",
    "sender": "string (agent ID)",
    "receiver": "string (agent ID)",
    "content": "string (message content)",
    "performative": "string (KQML performative)"
  }
  ```
- **Response**:
  ```json
  {
    "status": "success",
    "message_id": "string (UUID)",
    "run_id": "string (UUID)"
  }
  ```
- **Error Codes**:
  - `422`: Invalid message format
  - `500`: Server error

#### Get Agent Interactions
- **Endpoint**: `GET /agents/{agent_id}/interactions`
- **Description**: Get all interactions associated with an agent
- **Parameters**:
  - `agent_id`: string (path parameter)
- **Response**:
  ```json
  [
    {
      "id": "string (UUID)",
      "content": "string",
      "performative": "string",
      "timestamp": "string (ISO datetime)",
      "sender": "string",
      "receiver": "string"
    }
  ]
  ```
- **Error Codes**:
  - `404`: Agent not found
  - `500`: Server error

#### Get Agent Runs
- **Endpoint**: `GET /agents/{agent_id}/runs`
- **Description**: Get all runs associated with an agent
- **Parameters**:
  - `agent_id`: string (path parameter)
- **Response**:
  ```json
  [
    {
      "id": "string (UUID)",
      "timestamp": "string (ISO datetime)"
    }
  ]
  ```
- **Error Codes**:
  - `404`: Agent not found
  - `500`: Server error

#### Get Agent Statistics
- **Endpoint**: `GET /agents/stats`
- **Description**: Get statistics about agent interactions
- **Response**:
  ```json
  {
    "total_agents": "integer",
    "total_interactions": "integer",
    "active_agents": "integer",
    "interactions_per_agent": {
      "agent_id": "integer"
    }
  }
  ```
- **Error Codes**:
  - `500`: Server error

### Network Operations

#### Get Network Graph
- **Endpoint**: `GET /network`
- **Description**: Get all nodes and relationships in the agent network graph
- **Query Parameters**:
  - `node_type`: string (optional) - Filter by node type
  - `time_range`: string (optional) - Time range filter (24h, 7d, 30d, all)
- **Response**:
  ```json
  {
    "nodes": [
      {
        "id": "string",
        "type": "string",
        "properties": {}
      }
    ],
    "relationships": [
      {
        "source": "string",
        "target": "string",
        "type": "string",
        "properties": {}
      }
    ]
  }
  ```
- **Error Codes**:
  - `500`: Server error

#### Query Network
- **Endpoint**: `POST /network/query`
- **Description**: Query network graph data with filters
- **Request Body**:
  ```json
  {
    "node_types": ["string"],
    "relationship_types": ["string"],
    "time_range": "string (24h, 7d, 30d, all)",
    "properties": {
      "key": "value"
    }
  }
  ```
- **Response**: Same as GET /network
- **Error Codes**:
  - `422`: Invalid query parameters
  - `500`: Server error

### Synthetic Data Operations

#### Generate Synthetic Data
- **Endpoint**: `POST /synthetic/generate`
- **Description**: Generate synthetic data for testing
- **Request Body**:
  ```json
  {
    "num_agents": "integer",
    "num_messages": "integer",
    "time_range": "string (duration)",
    "seed": "integer (optional)"
  }
  ```
- **Response**:
  ```json
  {
    "status": "success",
    "generated": {
      "agents": "integer",
      "messages": "integer",
      "runs": "integer"
    }
  }
  ```
- **Error Codes**:
  - `422`: Invalid parameters
  - `500`: Server error

#### Generate Synthetic KQML Message
- **Endpoint**: `GET /synthetic/kqml`
- **Description**: Generate a synthetic KQML message
- **Response**:
  ```json
  {
    "message": "string (KQML message)",
    "performative": "string",
    "content": "string",
    "language": "string",
    "ontology": "string",
    "agent_id": "string"
  }
  ```
- **Error Codes**:
  - `500`: Server error

## Models

### KQMLMessageModel
```python
{
    "message": str,          # Raw KQML message
    "sender": str,           # Sender agent ID
    "receiver": str,         # Receiver agent ID
    "content": str,          # Message content
    "performative": str,     # KQML performative
    "timestamp": datetime,   # Message timestamp (optional)
    "run_id": str,          # Run ID (optional)
    "message_id": str       # Message ID (optional)
}
```

### GraphQuery
```python
{
    "filters": {
        "node_types": List[str],        # Node types to include
        "relationship_types": List[str], # Relationship types to include
        "time_range": str,              # Time range filter
        "properties": Dict[str, Any]    # Additional property filters
    }
}
```

### GraphData
```python
{
    "nodes": List[GraphNode],
    "links": List[GraphRelationship]
}