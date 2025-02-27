# API Endpoints Documentation

This document provides detailed information about all available API endpoints in the Agent Interaction Backend [0.7.1].

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

### Interaction Operations

#### Store Interaction
- **Endpoint**: `POST /interactions`
- **Description**: Store an interaction between agents
- **Request Body**:
  ```json
  {
    "sender_id": "string (agent ID)",
    "receiver_id": "string (agent ID)",
    "topic": "string (interaction topic)",
    "message": "string (interaction content)",
    "interaction_type": "string (message, query, response, etc.)",
    "priority": "integer (1-5, optional)",
    "sentiment": "float (-1 to 1, optional)",
    "metadata": "object (optional additional data)"
  }
  ```
- **Response**:
  ```json
  {
    "status": "success",
    "interaction_id": "string (UUID)",
    "run_id": "string (UUID)",
    "topic": "string"
  }
  ```
- **Error Codes**:
  - `422`: Invalid interaction data
  - `500`: Server error

#### Get Interactions
- **Endpoint**: `GET /interactions`
- **Description**: Get all interactions with optional filtering
- **Query Parameters**:
  - `limit`: integer (optional, default: 100) - Maximum number of interactions to return
- **Response**:
  ```json
  [
    {
      "id": "string (UUID)",
      "sender_id": "string",
      "receiver_id": "string",
      "topic": "string",
      "message": "string",
      "interaction_type": "string",
      "timestamp": "string (ISO datetime)",
      "priority": "integer (1-5)",
      "sentiment": "float (-1 to 1)",
      "duration_ms": "integer",
      "run_id": "string (UUID)",
      "metadata": "object"
    }
  ]
  ```
- **Error Codes**:
  - `500`: Server error

#### Get Specific Interaction
- **Endpoint**: `GET /interactions/{interaction_id}`
- **Description**: Get a specific interaction by ID
- **Parameters**:
  - `interaction_id`: string (path parameter)
- **Response**:
  ```json
  {
    "id": "string (UUID)",
    "sender_id": "string",
    "receiver_id": "string",
    "topic": "string",
    "message": "string",
    "interaction_type": "string",
    "timestamp": "string (ISO datetime)",
    "priority": "integer (1-5)",
    "sentiment": "float (-1 to 1)",
    "duration_ms": "integer",
    "run_id": "string (UUID)",
    "metadata": "object"
  }
  ```
- **Error Codes**:
  - `404`: Interaction not found
  - `500`: Server error

### Agent Operations

#### Create Agent
- **Endpoint**: `POST /agents`
- **Description**: Create a new agent
- **Request Body**:
  ```json
  {
    "id": "string (agent ID)",
    "type": "string (agent type)",
    "role": "string (agent role)",
    "properties": "object (optional additional properties)"
  }
  ```
- **Response**:
  ```json
  {
    "message": "Agent created successfully",
    "agent": {
      "id": "string",
      "type": "string",
      "role": "string",
      "timestamp": "string (ISO datetime)",
      "properties": "object"
    }
  }
  ```
- **Error Codes**:
  - `422`: Invalid agent data
  - `500`: Server error

#### Get Agents
- **Endpoint**: `GET /agents`
- **Description**: Get all agents
- **Response**:
  ```json
  [
    {
      "id": "string",
      "type": "string",
      "role": "string",
      "timestamp": "string (ISO datetime)"
    }
  ]
  ```
- **Error Codes**:
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
      "sender_id": "string",
      "receiver_id": "string",
      "topic": "string",
      "message": "string",
      "interaction_type": "string",
      "timestamp": "string (ISO datetime)",
      "priority": "integer (1-5)",
      "sentiment": "float (-1 to 1)",
      "duration_ms": "integer",
      "run_id": "string (UUID)",
      "metadata": "object"
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

#### Store Agent Interaction (Deprecated)
- **Endpoint**: `POST /agents/message`
- **Description**: Store an interaction between agents (use `/interactions` instead)
- **Request Body**: Same as `POST /interactions`
- **Response**: Same as `POST /interactions`
- **Error Codes**:
  - `422`: Invalid interaction data
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
    "links": [
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
    "node_type": "string",
    "relationship_type": "string (optional)",
    "start_time": "string (ISO datetime, optional)",
    "end_time": "string (ISO datetime, optional)",
    "agent_ids": ["string"] (optional),
    "limit": "integer (optional)",
    "include_properties": "boolean (optional, default: true)"
  }
  ```
- **Response**: Same as GET /network
- **Error Codes**:
  - `422`: Invalid query parameters
  - `500`: Server error

### Data Generation Operations

#### Generate Synthetic Data
- **Endpoint**: `POST /generate/data`
- **Description**: Generate synthetic data for testing
- **Request Body**:
  ```json
  {
    "numAgents": "integer",
    "numInteractions": "integer"
  }
  ```
- **Response**:
  ```json
  {
    "status": "success",
    "data": {
      "agents": [
        {
          "id": "string",
          "type": "string",
          "role": "string"
        }
      ],
      "interactions": [
        {
          "id": "string (UUID)",
          "sender_id": "string",
          "receiver_id": "string",
          "topic": "string",
          "message": "string",
          "interaction_type": "string",
          "timestamp": "string (ISO datetime)",
          "priority": "integer (1-5)"
        }
      ]
    }
  }
  ```
- **Error Codes**:
  - `422`: Invalid parameters
  - `500`: Server error

#### Generate Synthetic Interaction
- **Endpoint**: `POST /generate/kqml`
- **Description**: Generate a synthetic agent interaction
- **Response**:
  ```json
  {
    "interaction_id": "string (UUID)",
    "sender_id": "string",
    "receiver_id": "string",
    "topic": "string",
    "message": "string",
    "interaction_type": "string",
    "timestamp": "string (ISO datetime)",
    "priority": "integer (1-5)",
    "run_id": "string (UUID)",
    "metadata": {
      "synthetic": true,
      "generated_at": "string (ISO datetime)"
    }
  }
  ```
- **Error Codes**:
  - `500`: Server error

#### Generate Synthetic Data (Deprecated)
- **Endpoint**: `POST /synthetic/data`
- **Description**: Generate synthetic data for testing (use `/generate/data` instead)
- **Request Body**: Same as `POST /generate/data`
- **Response**: Same as `POST /generate/data`
- **Error Codes**:
  - `422`: Invalid parameters
  - `500`: Server error

#### Generate Synthetic Interaction (Deprecated)
- **Endpoint**: `POST /synthetic/kqml`
- **Description**: Generate a synthetic agent interaction (use `/generate/kqml` instead)
- **Response**: Same as `POST /generate/kqml`
- **Error Codes**:
  - `500`: Server error

### Admin Operations

#### Clear Database
- **Endpoint**: `POST /admin/database/clear`
- **Description**: Clear all data from the database
- **Response**:
  ```json
  {
    "success": true,
    "message": "Database cleared successfully",
    "details": {
      "success": true,
      "nodes_deleted": 42,
      "relationships_deleted": 56
    }
  }
  ```
- **Error Codes**:
  - `500`: Server error


## Models

### AgentInteraction
```python
{
    "interaction_id": str,       # Unique identifier
    "sender_id": str,            # Sender agent ID
    "receiver_id": str,          # Receiver agent ID
    "topic": str,                # Interaction topic
    "message": str,              # Interaction content
    "interaction_type": str,     # Type (message, query, response, etc.)
    "timestamp": datetime,       # Interaction timestamp
    "priority": int,             # Priority level (1-5, optional)
    "sentiment": float,          # Sentiment score (-1 to 1, optional)
    "duration_ms": int,          # Processing time in milliseconds (optional)
    "run_id": str,               # Run ID (optional)
    "metadata": dict             # Additional metadata (optional)
}
```

### GraphQuery
```python
{
    "node_type": str,               # Node type to query
    "relationship_type": str,       # Relationship type (optional)
    "start_time": str,              # Start time filter (optional)
    "end_time": str,                # End time filter (optional)
    "agent_ids": List[str],         # Agent IDs to filter (optional)
    "limit": int,                   # Result limit (optional)
    "include_properties": bool      # Include properties in result (optional)
}
```

### GraphData
```python
{
    "nodes": List[GraphNode],
    "links": List[GraphRelationship]
}
```

### SyntheticDataParams
```python
{
    "numAgents": int,          # Number of agents to generate
    "numInteractions": int     # Number of interactions to generate
}
```


### DatabaseOperation
```python
{
    "success": bool,           # Success status
    "message": str,            # Operation message
    "details": dict            # Operation details
}
```