# NeuroSpark Memory Bank

## Project Overview
NeuroSpark is an AI-Powered Blockchain Intelligence System for analyzing smart contracts, monitoring blockchain activities, and providing real-time Web3 security insights. The system is transitioning from version 0.9.0 to 1.0.0, migrating from an agent-based system to a blockchain-first approach.

## System Architecture

```mermaid
graph TD
    Client[Client Applications] --> API[FastAPI Backend]
    API --> BC[Blockchain Connectors]
    API --> DB[ArangoDB]
    API --> Analysis[Network Analysis]
    API --> Risk[Risk Intelligence]
    API --> LLM[LLM Integration]
    BC --> Ethereum[Ethereum]
    BC --> Solana[Solana]
    BC --> Other[Other Chains]
    DB --> Collections[Collections]
    Collections --> Wallets[Wallets]
    Collections --> Contracts[Contracts]
    Collections --> Transactions[Transactions]
    Collections --> Events[Events]
    Collections --> Alerts[Alerts]
    Risk --> Scoring[Scoring Engine]
    Risk --> Detectors[Anomaly Detectors]
    Risk --> AlertGen[Alert Generation]
    Analysis --> NetworkX[NetworkX]
    Analysis --> GraphAlgo[Graph Algorithms]
    LLM --> Ollama[Ollama]
    LLM --> QueryParser[Query Parser]
    Monitoring[Monitoring Stack] --> Prom[Prometheus]
    Monitoring --> Grafana[Grafana]
```

## Database Schema

```mermaid
erDiagram
    WALLET {
        string address PK
        string chain
        float balance
        datetime first_seen
        datetime last_active
        string type
        array tags
        float risk_score
        json metadata
    }
    CONTRACT {
        string address PK
        string chain
        string creator
        string creation_tx
        datetime creation_timestamp
        boolean verified
        string name
        string bytecode
        json abi
        string source_code
        float risk_score
        array vulnerabilities
    }
    TRANSACTION {
        string hash PK
        int block_number
        datetime timestamp
        string from
        string to
        float value
        int gas_used
        float gas_price
        string status
        string chain
        string input_data
        float risk_score
    }
    EVENT {
        string id PK
        string contract
        string tx_hash
        int block_number
        datetime timestamp
        string name
        string signature
        json params
        string chain
    }
    ALERT {
        string id PK
        datetime timestamp
        string severity
        string type
        string entity
        string description
        json context
        string status
    }
    
    WALLET ||--o{ TRANSACTION : sends
    WALLET ||--o{ TRANSACTION : receives
    WALLET ||--o{ CONTRACT : creates
    WALLET ||--o{ CONTRACT : interacts_with
    CONTRACT ||--o{ EVENT : emits
    CONTRACT ||--o{ CONTRACT : calls
    TRANSACTION ||--o{ EVENT : contains
    WALLET ||--o{ ALERT : triggers
    CONTRACT ||--o{ ALERT : triggers
    TRANSACTION ||--o{ ALERT : triggers
```

## Data Flow

```mermaid
flowchart LR
    Blockchain[Blockchain] --> Connectors[Blockchain Connectors]
    Connectors --> Parser[Data Parser]
    Parser --> Models[Blockchain Models]
    Models --> DB[ArangoDB]
    DB --> Query[Query Engine]
    DB --> Analysis[Analysis Engine]
    Analysis --> Risk[Risk Scoring]
    Risk --> Alerts[Alert System]
    Query --> API[REST API]
    Alerts --> WS[WebSocket]
    NLQuery[Natural Language Query] --> LLM[LLM]
    LLM --> Query
    API --> Client[Client]
    WS --> Client
```

## Migration Status

The project is currently migrating from an agent-based system to a blockchain-focused architecture:

-  Updated models.py with blockchain terminology
-  Renamed key classes (NetworkAgents � BlockchainNetwork, InteractionData � TransactionData)
-  Updated database operations to reflect blockchain focus
-  Changed WebSocket handler to use blockchain addresses
-  Updated database name from "agent_interactions" to "blockchain_intelligence"
-  Updated test suite with blockchain terminology and fixtures
-  Updated SWAGGER_DOCUMENTATION.md with blockchain API details
-  Updated CHANGELOG.md for version 0.9.1

Pending tasks:
-  Update routes.py and other API endpoint handlers to use the new models
-  Implement changes in data_generator.py
-  Add blockchain connector tests
-  Update API_ENDPOINTS.md to remove agent references
-  Add integration tests for complete blockchain data flow

## Key Components

### Blockchain Connectors
- Ethereum (web3.py)
- Solana (solana.py)
- Extensible architecture for additional chains

### Database (ArangoDB)
- Graph database for storing blockchain entities and relationships
- Collections: Wallets, Contracts, Transactions, Events, Alerts
- Graph relationships for tracing transaction flows

### Risk Intelligence
- Multi-factor scoring system
- Anomaly detection
- Alert generation and management

### LLM Integration
- Ollama for local LLM deployment
- Natural language query processing
- Blockchain data interpretation

### Monitoring
- Prometheus metrics
- Grafana dashboards
- Logging and alerting

## API Structure
- `/blockchain/wallets/*` - Wallet management and analysis
- `/blockchain/transactions/*` - Transaction queries and analysis
- `/blockchain/contracts/*` - Smart contract analysis and risk assessment
- `/blockchain/events/*` - Event filtering and decoding
- `/blockchain/risk/*` - Risk assessment and alerts
- `/blockchain/query/*` - Natural language and pattern queries
- `/analysis/*` - Network analysis endpoints
- `/graph/*` - Graph visualization data