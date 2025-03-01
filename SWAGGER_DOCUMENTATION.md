# KQML Parser API Swagger Documentation

This document provides information about the Swagger API documentation for the KQML Parser Backend.

## Accessing Swagger Documentation

When the backend is running, you can access the Swagger UI documentation at:

```
http://localhost:8000/docs
```

And the ReDoc alternative documentation at:

```
http://localhost:8000/redoc
```

## New in Version 0.8.2: Network Analysis

The KQML Parser backend now includes comprehensive graph analysis features through NetworkX integration. These features are available through the `/analysis/*` endpoints:

- **Graph Metrics Analysis**: Calculate density, connectivity, clustering, and other network metrics
- **Centrality Measures**: Identify important nodes using degree, betweenness, closeness, eigenvector centrality
- **Community Detection**: Find natural clusters of agents using algorithms like Louvain and Label Propagation
- **Layout Generation**: Generate optimal node positions for visualization
- **Temporal Analysis**: Track how network metrics change over time
- **Enhanced Visualization**: Combine layout, metrics, and community detection for rich visualizations

These endpoints are fully documented in Swagger UI and can be used to gain deeper insights into agent interaction patterns.

## Key Models Documentation

### AgentInteraction Model

This is the primary model used for sending and receiving agent interactions:

```json
{
  "interaction_id": "string (UUID, auto-generated if not provided)",
  "timestamp": "string (ISO datetime, auto-generated if not provided)",
  "sender_id": "string (required)",
  "receiver_id": "string (required)",
  "topic": "string (required)",
  "message": "string (required)",
  "run_id": "string (optional)",
  "interaction_type": "string (default: 'message')",
  "sentiment": "float (optional, range: -1 to 1)",
  "priority": "integer (optional, range: 1-5)",
  "duration_ms": "integer (optional)",
  "metadata": "object (optional)"
}
```

Valid `interaction_type` values:
- "message" - General message
- "query" - Question or request for information
- "response" - Reply to a query
- "notification" - Update or alert
- "request" - Action request
- "broadcast" - Message to multiple receivers
- "alert" - Important notification
- "command" - Directive to perform action
- "report" - Status or information report
- "update" - Status change notification

### GraphData Model

Used for graph visualization:

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

### Query Model

Used for natural language queries:

```json
{
  "query": "string (natural language query text)"
}
```

Example queries:
- "Find all interactions with priority greater than 3"
- "Show messages from agent1 to agent2"
- "Find all messages with topic temperature_reading"

### SyntheticDataParams Model

Used for generating synthetic data:

```json
{
  "numAgents": "integer (> 0)",
  "numInteractions": "integer (> 0)"
}
```

## Common API Patterns

### Success Responses

Most successful operations return:

```json
{
  "status": "success",
  "message": "Operation completed successfully",
  "data": { ... }
}
```

### Error Responses

Error responses follow this pattern:

```json
{
  "detail": "Error message explaining what went wrong"
}
```

Common HTTP status codes:
- 400: Bad Request - Invalid input
- 404: Not Found - Resource not found
- 422: Validation Error - Input validation failed
- 500: Internal Server Error - Server-side error

## Testing API Endpoints

You can test API endpoints directly from the Swagger UI by:

1. Navigate to http://localhost:8000/docs
2. Click on an endpoint to expand it
3. Click "Try it out"
4. Fill in required parameters
5. Click "Execute"

## Sample Requests

### Create Interaction

```bash
curl -X 'POST' \
  'http://localhost:8000/agents/interaction' \
  -H 'Content-Type: application/json' \
  -d '{
  "sender_id": "agent1",
  "receiver_id": "agent2",
  "topic": "temperature_reading",
  "message": "Current temperature is 25.5°C",
  "interaction_type": "report",
  "priority": 3
}'
```

### Generate Synthetic Data

```bash
curl -X 'POST' \
  'http://localhost:8000/generate/data' \
  -H 'Content-Type: application/json' \
  -d '{
  "numAgents": 5,
  "numInteractions": 20
}'
```

### Query Interactions

```bash
curl -X 'POST' \
  'http://localhost:8000/query' \
  -H 'Content-Type: application/json' \
  -d '{
  "query": "Find all interactions with priority greater than 3"
}'
```

### Get Graph Visualization Data

```bash
curl -X 'GET' \
  'http://localhost:8000/graph'
```

### Get Graph Metrics Analysis

```bash
curl -X 'GET' \
  'http://localhost:8000/analysis/metrics?directed=true'
```

### Get Node Centrality Measures

```bash
curl -X 'GET' \
  'http://localhost:8000/analysis/centrality?top_n=5'
```

### Detect Communities in Graph

```bash
curl -X 'GET' \
  'http://localhost:8000/analysis/communities?algorithm=louvain&directed=false'
```

### Get Graph Layout for Visualization

```bash
curl -X 'GET' \
  'http://localhost:8000/analysis/layout?layout=spring&dimensions=2'
```

### Get Enhanced Visualization Data

```bash
curl -X 'GET' \
  'http://localhost:8000/analysis/visualization?include_communities=true&include_metrics=true'
```

### Clear Database

```bash
curl -X 'DELETE' \
  'http://localhost:8000/admin/database/clear'
```

## API Reference

For a complete list of all API endpoints with detailed documentation, please see the [API_ENDPOINTS.md](./API_ENDPOINTS.md) file or use the Swagger UI at http://localhost:8000/docs when the backend is running.