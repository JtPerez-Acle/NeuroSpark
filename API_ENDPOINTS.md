# KQML Parser Backend - API Documentation

This document provides detailed information about all available API endpoints in the Agent Interaction Backend.

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

### Root

- **Endpoint**: `GET /`
- **Description**: Root endpoint for API verification
- **Response**: 
  ```json
  {
    "message": "Agent Interaction Backend API"
  }
  ```

### Interactions

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

#### Store Agent Interaction
- **Endpoint**: `POST /agents/interaction`
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
      "agent_id": "string",
      "timestamp": "string (ISO datetime)",
      "status": "string",
      "metrics": "object"
    }
  ]
  ```
- **Error Codes**:
  - `404`: Agent not found
  - `500`: Server error

### Network Operations

#### Get Network Graph
- **Endpoint**: `GET /graph`
- **Description**: Get all nodes and relationships in the agent network graph
- **Response**:
  ```json
  {
    "nodes": [
      {
        "id": "string",
        "label": "string",
        "type": "string",
        "details": "string (optional)",
        "timestamp": "string (ISO datetime, optional)"
      }
    ],
    "links": [
      {
        "id": "string",
        "source": "string",
        "target": "string",
        "type": "string",
        "label": "string (optional)"
      }
    ]
  }
  ```
- **Error Codes**:
  - `500`: Server error

#### Get Network Data
- **Endpoint**: `GET /network`
- **Description**: Get all nodes and relationships in the agent network graph with filtering
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
- **Description**: Query network graph data with complex filters
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

### Query Operations

#### Query Interactions
- **Endpoint**: `POST /query`
- **Description**: Query interactions using natural language
- **Request Body**:
  ```json
  {
    "query": "string (natural language query)"
  }
  ```
- **Response**:
  ```json
  {
    "interactions": [
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
  }
  ```
- **Error Codes**:
  - `422`: Invalid query
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
- **Endpoint**: `GET /generate/interaction`
- **Description**: Generate a single synthetic agent interaction
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
    "priority": "integer (1-5)"
  }
  ```
- **Error Codes**:
  - `500`: Server error

### Database Operations

#### Clear Database
- **Endpoint**: `DELETE /database/clear`
- **Description**: Clear all data from the database
- **Response**:
  ```json
  {
    "success": true,
    "message": "Database cleared successfully",
    "details": {
      "nodes_deleted": 42,
      "relationships_deleted": 56
    }
  }
  ```
- **Error Codes**:
  - `500`: Server error

#### Clean Database
- **Endpoint**: `POST /database/clean`
- **Description**: Clean the database by removing orphaned nodes and invalid relationships
- **Response**:
  ```json
  {
    "success": true,
    "message": "Database cleaned successfully",
    "stats": {
      "orphaned_nodes_removed": 5,
      "invalid_relationships_removed": 3
    }
  }
  ```
- **Error Codes**:
  - `500`: Server error

## Models

### AgentInteraction
```json
{
  "interaction_id": "string (UUID)",
  "sender_id": "string",
  "receiver_id": "string",
  "topic": "string",
  "message": "string",
  "interaction_type": "string",
  "timestamp": "string (ISO datetime)",
  "priority": "integer (1-5, optional)",
  "sentiment": "float (-1 to 1, optional)",
  "duration_ms": "integer (optional)",
  "run_id": "string (UUID, optional)",
  "metadata": "object (optional)"
}
```

### GraphData
```json
{
  "nodes": [
    {
      "id": "string",
      "label": "string",
      "type": "string",
      "details": "string (optional)",
      "timestamp": "string (ISO datetime, optional)"
    }
  ],
  "links": [
    {
      "id": "string",
      "source": "string",
      "target": "string",
      "type": "string",
      "label": "string (optional)"
    }
  ]
}
```

### GraphQuery
```json
{
  "node_type": "string",
  "relationship_type": "string (optional)",
  "start_time": "string (ISO datetime, optional)",
  "end_time": "string (ISO datetime, optional)",
  "agent_ids": ["string (optional)"],
  "limit": "integer (optional)",
  "include_properties": "boolean (optional, default: true)"
}
```

### SyntheticDataParams
```json
{
  "numAgents": "integer",
  "numInteractions": "integer"
}
```

### Query
```json
{
  "query": "string (natural language query)"
}
```

### DatabaseOperation
```json
{
  "success": "boolean",
  "message": "string",
  "details": "object"
}
```