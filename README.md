# KQML Parser Backend 0.2.3

A Multi-Agent Graph Intelligence System for processing and storing KQML messages and agent interactions.

## Features

- FastAPI-based REST API with WebSocket support for real-time updates
- Neo4j graph database for persistent storage of agent interactions
- KQML message parsing and validation
- Synthetic data generation for testing and demonstration
- Interactive API documentation with Swagger UI
- Real-time agent interaction monitoring via WebSocket
- Comprehensive test suite with Neo4j integration testing
- Extensive logging and monitoring capabilities

## Prerequisites

- Python 3.11+
- Neo4j 5.x
- Docker and Docker Compose

## Installation

1. Clone the repository:
```bash
git clone https://github.com/JtPerez-Acle/kqml-parser-backend
cd kqml-parser-backend
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -e ".[test]"
```

4. Start Neo4j and the application:
```bash
docker-compose up -d
```

This will start both Neo4j and the FastAPI application in containers.

## Environment Variables

The application uses the following environment variables for Neo4j configuration:
- `NEO4J_URI`: Neo4j connection URI (default: `bolt://localhost:7687`)
- `NEO4J_USER`: Neo4j username (default: `neo4j`)
- `NEO4J_PASSWORD`: Neo4j password (default: `kqml_dev_2025`)

These variables are automatically set in the `docker-compose.yml` file. For local development without Docker:
```bash
export NEO4J_URI=bolt://localhost:7687
export NEO4J_USER=neo4j
export NEO4J_PASSWORD=kqml_dev_2025
```

## Running Tests

The test suite uses a containerized Neo4j instance for all database operations. This ensures that tests run in an environment that matches production.

### Using run_tests.sh (Recommended)

We provide a convenient script that handles the entire test setup and execution:

```bash
./run_tests.sh
```

This script will:
1. Clean up any existing test containers and volumes
2. Build a fresh test environment using Docker Compose
3. Start a Neo4j container configured specifically for testing
4. Run the test suite with coverage reporting
5. Clean up all test containers and volumes after completion

The script uses `docker-compose.test.yml` which:
- Runs Neo4j in a temporary filesystem (tmpfs) for fast testing
- Ensures proper isolation between test runs
- Matches the production environment configuration
- Provides health checks to ensure Neo4j is ready before tests start

### Manual Testing

If you need more control over the test environment, you can run the components manually:

1. Start the test Neo4j container:
```bash
docker-compose -f docker-compose.test.yml up -d neo4j
```

2. Run the tests:
```bash
pytest -v --cov=app --cov-report=term-missing
```

This will:
- Run all tests against the Neo4j database
- Generate a coverage report
- Validate all database operations
- Test error handling and edge cases
- Verify logging and monitoring

### Test Flow Visualization

```mermaid
flowchart TD
    Start([Start run_tests.sh]) --> Cleanup[Clean up existing containers]
    Cleanup --> Build[Build test environment]
    Build -->|Success| StartNeo4j[Start Neo4j container]
    Build -->|Failure| BuildError[Build Error:<br/>- Invalid Dockerfile<br/>- Missing dependencies<br/>- Permission issues]
    BuildError -->|Auto| Cleanup
    
    StartNeo4j -->|Success| WaitHealth{Wait for<br/>Neo4j health}
    StartNeo4j -->|Failure| Neo4jError[Neo4j Error:<br/>- Port conflicts<br/>- Volume issues<br/>- Memory limits]
    Neo4jError -->|Auto| Cleanup
    
    WaitHealth -->|Healthy| StartTests[Start test container]
    WaitHealth -->|Timeout| HealthError[Health Check Error:<br/>- Neo4j not responding<br/>- Network issues]
    HealthError -->|Auto| Cleanup
    
    StartTests -->|Success| RunTests[Run pytest suite]
    StartTests -->|Failure| TestContainerError[Test Container Error:<br/>- Volume mount issues<br/>- Permission problems]
    TestContainerError -->|Auto| Cleanup
    
    RunTests -->|Pass| FinalCleanup[Clean up all resources]
    RunTests -->|Fail| TestFailure[Test Failures:<br/>- Failed assertions<br/>- Connection errors<br/>- Timeout issues]
    TestFailure -->|Auto| FinalCleanup
    
    FinalCleanup --> End([End])
    
    classDef success fill:#a3e635,stroke:#166534,color:#166534
    classDef error fill:#fca5a5,stroke:#991b1b,color:#991b1b
    classDef process fill:#93c5fd,stroke:#1e40af,color:#1e40af
    classDef decision fill:#fde047,stroke:#854d0e,color:#854d0e
    
    class Start,End success
    class BuildError,Neo4jError,HealthError,TestContainerError,TestFailure error
    class Cleanup,Build,StartNeo4j,StartTests,RunTests,FinalCleanup process
    class WaitHealth decision
```

The diagram shows:
- 🟦 Blue boxes: Main process steps
- 🟨 Yellow diamonds: Decision points
- 🟩 Green boxes: Start/End points
- 🟥 Red boxes: Potential failure points and their causes

Key features of our test orchestration:
1. **Automatic Cleanup**: Every failure triggers automatic cleanup to prevent resource leaks
2. **Health Checks**: Neo4j container must be healthy before tests begin
3. **Failure Isolation**: Each component (build, Neo4j, tests) fails independently
4. **Resource Management**: All resources are cleaned up, regardless of success or failure

## Running the Application

Start the FastAPI server:
```bash
uvicorn app.main:app --reload
```

The API will be available at:
- API: http://localhost:8000
- Interactive Documentation (Swagger UI): http://localhost:8000/docs
- Alternative Documentation (ReDoc): http://localhost:8000/redoc
- WebSocket: ws://localhost:8000/ws

## API Endpoints

### Root Endpoint
- `GET /` - Get API information

### Agent Interactions
- `POST /agents/message` - Process a KQML message
- `GET /agents/{agent_id}/runs` - Get all runs for a specific agent
- `GET /agents/{agent_id}/interactions` - Get all interactions for a specific agent

### Network Operations
- `POST /network/query` - Process natural language queries about agent interactions
- `POST /synthetic/data` - Generate synthetic interaction data
- `GET /synthetic/kqml` - Generate a synthetic KQML message

### WebSocket
- `WebSocket /ws` - Real-time agent interaction updates

## System Architecture

```mermaid
graph TB
    subgraph Client Applications
        C1[Web Client]
        C2[Agent Client]
    end

    subgraph FastAPI Backend
        API[FastAPI App]
        WS[WebSocket Manager]
        KH[KQML Handler]
        DG[Data Generator]
        
        subgraph Database Layer
            DBI[Database Interface]
            NDB[Neo4j DB]
        end
    end

    subgraph Storage
        Neo4j[(Neo4j Database)]
    end

    C1 --> |HTTP/WS| API
    C2 --> |HTTP| API
    API --> |Real-time Updates| WS
    WS --> |Notifications| C1
    API --> |Parse Messages| KH
    API --> |Generate Data| DG
    
    KH --> DBI
    DG --> DBI
    DBI --> NDB
    NDB --> Neo4j
```

## Data Flow

```mermaid
sequenceDiagram
    participant Agent as Agent Client
    participant API as FastAPI Backend
    participant WS as WebSocket
    participant DB as Neo4j Database
    participant Client as Web Client

    Agent->>API: Send KQML Message
    API->>API: Parse & Validate
    API->>DB: Store Interaction
    API->>WS: Broadcast Update
    WS->>Client: Real-time Notification
    
    Client->>API: Query Interactions
    API->>DB: Execute Query
    DB->>API: Return Results
    API->>Client: Send Response
```

## Database Schema

```mermaid
erDiagram
    AGENT ||--o{ INTERACTION : "SENT"
    AGENT ||--o{ INTERACTION : "RECEIVED_BY"
    INTERACTION ||--|| RUN : "PART_OF"
    
    AGENT {
        string id
        string type
        string description
    }
    
    INTERACTION {
        string id
        string message_id
        string content
        string performative
        datetime timestamp
    }
    
    RUN {
        string id
        datetime timestamp
        string description
        json metrics
    }
```

## Component Interaction

```mermaid
flowchart LR
    subgraph Input
        KQML[KQML Message]
        Query[Query Request]
        Gen[Generate Data]
    end

    subgraph Processing
        Parser[KQML Parser]
        Handler[Message Handler]
        Generator[Data Generator]
    end

    subgraph Storage
        Neo4j[(Neo4j)]
    end

    subgraph Output
        WS[WebSocket]
        API[REST API]
    end

    KQML --> Parser
    Query --> Handler
    Gen --> Generator

    Parser --> Handler
    Handler --> Neo4j
    Generator --> Neo4j

    Neo4j --> API
    Neo4j --> WS
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests to ensure they pass
5. Submit a pull request

## License

MIT License. See LICENSE file for details.