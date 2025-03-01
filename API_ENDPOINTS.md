# KQML Parser Backend - API Documentation

This document provides detailed information about all available API endpoints in the Agent Interaction Backend.

## Version

Current Version: **0.8.2**

Latest changes:
- Added NetworkX integration for advanced graph analysis
- Temporal analysis of interactions
- Community detection algorithms
- Node centrality metrics
- Enhanced graph visualization

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

### Network Analysis Operations

#### Get Graph Metrics
- **Endpoint**: `GET /analysis/metrics`
- **Description**: Get comprehensive graph metrics
- **Query Parameters**:
  - `directed`: boolean (optional, default: true) - Whether to treat graph as directed
  - `link_limit`: integer (optional, default: 1000) - Maximum number of links to analyze
- **Response**:
  ```json
  {
    "message": "Graph metrics calculated successfully",
    "node_count": 42,
    "link_count": 156,
    "metrics": {
      "node_count": 42,
      "edge_count": 156,
      "density": 0.0897,
      "average_degree": 3.714,
      "is_strongly_connected": false,
      "strongly_connected_components": 5,
      "is_weakly_connected": true,
      "weakly_connected_components": 1,
      "average_clustering": 0.243,
      "diameter_largest_component": 6,
      "average_shortest_path_length_largest_component": 2.85,
      "largest_component_size": 37,
      "largest_component_percentage": 0.881
    }
  }
  ```
- **Error Codes**:
  - `500`: Server error

#### Get Node Centrality
- **Endpoint**: `GET /analysis/centrality`
- **Description**: Calculate centrality metrics for nodes
- **Query Parameters**:
  - `directed`: boolean (optional, default: true) - Whether to treat graph as directed
  - `top_n`: integer (optional, default: 10) - Limit results to top N nodes
  - `link_limit`: integer (optional, default: 1000) - Maximum number of links to analyze
  - `normalized`: boolean (optional, default: true) - Whether to normalize centrality values
- **Response**:
  ```json
  {
    "message": "Node centrality calculated successfully",
    "node_count": 42,
    "centrality": {
      "in_degree": {
        "agent_123": 0.951,
        "agent_456": 0.875,
        "agent_789": 0.723
      },
      "out_degree": {
        "agent_123": 0.857,
        "agent_456": 0.754,
        "agent_789": 0.651
      },
      "betweenness": {
        "agent_123": 0.623,
        "agent_456": 0.542,
        "agent_789": 0.498
      },
      "closeness": {
        "agent_123": 0.721,
        "agent_456": 0.689,
        "agent_789": 0.623
      },
      "pagerank": {
        "agent_123": 0.157,
        "agent_456": 0.132,
        "agent_789": 0.098
      }
    }
  }
  ```
- **Error Codes**:
  - `500`: Server error

#### Detect Communities
- **Endpoint**: `GET /analysis/communities`
- **Description**: Detect communities in the graph
- **Query Parameters**:
  - `algorithm`: string (optional, default: "louvain") - Community detection algorithm
  - `directed`: boolean (optional, default: false) - Whether to treat graph as directed
  - `link_limit`: integer (optional, default: 1000) - Maximum number of links to analyze
- **Response**:
  ```json
  {
    "message": "Communities detected successfully",
    "node_count": 42,
    "algorithm": "louvain",
    "communities": {
      "community_count": 3,
      "communities": [
        ["agent_1", "agent_2", "agent_3"],
        ["agent_4", "agent_5", "agent_6"],
        ["agent_7", "agent_8", "agent_9"]
      ],
      "algorithm": "louvain",
      "modularity": 0.423,
      "community_sizes": [3, 3, 3]
    }
  }
  ```
- **Error Codes**:
  - `500`: Server error

#### Get Graph Layout
- **Endpoint**: `GET /analysis/layout`
- **Description**: Generate layout coordinates for graph visualization
- **Query Parameters**:
  - `layout`: string (optional, default: "spring") - Layout algorithm
  - `directed`: boolean (optional, default: true) - Whether to treat graph as directed
  - `dimensions`: integer (optional, default: 2) - Number of dimensions (2 or 3)
  - `scale`: float (optional, default: 100.0) - Scale factor for the layout
  - `link_limit`: integer (optional, default: 1000) - Maximum number of links to analyze
- **Response**:
  ```json
  {
    "message": "spring layout generated successfully",
    "layout": "spring",
    "dimensions": 2,
    "positions": {
      "agent_1": [45.2, 67.8],
      "agent_2": [23.1, 98.4],
      "agent_3": [78.5, 34.2]
    }
  }
  ```
- **Error Codes**:
  - `500`: Server error

#### Get Temporal Analysis
- **Endpoint**: `GET /analysis/temporal`
- **Description**: Analyze graph metrics over time
- **Query Parameters**:
  - `window_size`: integer (optional, default: 86400) - Window size in seconds
  - `max_windows`: integer (optional, default: 30) - Maximum number of windows
  - `directed`: boolean (optional, default: true) - Whether to treat graph as directed
  - `link_limit`: integer (optional, default: 5000) - Maximum number of links to analyze
- **Response**:
  ```json
  {
    "message": "Temporal analysis completed successfully",
    "window_size_seconds": 86400,
    "max_windows": 30,
    "temporal_metrics": {
      "window_size_seconds": 86400,
      "metrics_over_time": [
        {
          "window_start": "2025-02-01T00:00:00",
          "window_end": "2025-02-02T00:00:00",
          "link_count": 42,
          "metrics": {
            "node_count": 15,
            "edge_count": 42,
            "density": 0.2
          }
        },
        {
          "window_start": "2025-02-02T00:00:00",
          "window_end": "2025-02-03T00:00:00",
          "link_count": 56,
          "metrics": {
            "node_count": 18,
            "edge_count": 56,
            "density": 0.18
          }
        }
      ]
    }
  }
  ```
- **Error Codes**:
  - `500`: Server error

#### Get Advanced Visualization
- **Endpoint**: `GET /analysis/visualization`
- **Description**: Get network visualization data with enhanced metrics and layouts
- **Query Parameters**:
  - `layout`: string (optional, default: "spring") - Layout algorithm
  - `directed`: boolean (optional, default: true) - Whether to treat graph as directed
  - `include_communities`: boolean (optional, default: false) - Include community detection
  - `include_metrics`: boolean (optional, default: false) - Include node metrics
  - `community_algorithm`: string (optional, default: "louvain") - Community algorithm
  - `link_limit`: integer (optional, default: 1000) - Maximum number of links to analyze
- **Response**:
  ```json
  {
    "message": "Visualization data generated successfully",
    "visualization": {
      "nodes": [
        {
          "id": "agent_1",
          "label": "sensor",
          "type": "temperature",
          "x": 45.2,
          "y": 67.8,
          "community": 0,
          "metrics": {
            "in_degree": 0.5,
            "betweenness": 0.3
          }
        }
      ],
      "links": [
        {
          "id": "interaction_1",
          "source": "agent_1",
          "target": "agent_2",
          "type": "message"
        }
      ],
      "layout": "spring",
      "graph_metrics": {
        "node_count": 42,
        "edge_count": 78,
        "density": 0.045
      },
      "communities": {
        "community_count": 3,
        "communities": [
          ["agent_1", "agent_3"],
          ["agent_2", "agent_4"]
        ]
      }
    }
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

#### Generate Scenario-Based Data
- **Endpoint**: `POST /generate/scenario`
- **Description**: Generate synthetic data based on specific simulation scenarios
- **Request Body**:
  ```json
  {
    "scenario": "string (pd, predator_prey, pursuer_evader, search_rescue)",
    "numAgents": "integer",
    "numInteractions": "integer",
    "rounds": "integer (optional)"
  }
  ```
- **Response**:
  ```json
  {
    "status": "success",
    "scenario": "string",
    "data": {
      "agents": [
        {
          "id": "string",
          "type": "string",
          "role": "string",
          // Scenario-specific properties
        }
      ],
      "interactions": [
        {
          "interaction_id": "string (UUID)",
          "sender_id": "string",
          "receiver_id": "string",
          "topic": "string",
          "message": "string",
          "interaction_type": "string",
          "timestamp": "string (ISO datetime)",
          "run_id": "string (UUID)",
          "metadata": {
            "scenario": "string",
            // Scenario-specific metadata
          }
        }
      ],
      "run_id": "string (UUID)",
      "scenario": "string"
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

### ScenarioParams
```json
{
  "scenario": "string (pd, predator_prey, pursuer_evader, search_rescue)",
  "numAgents": "integer",
  "numInteractions": "integer",
  "rounds": "integer (optional)"
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