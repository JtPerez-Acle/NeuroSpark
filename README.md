# NeuroSpark v0.9.2

An AI-Powered Blockchain Intelligence System for analyzing smart contracts, monitoring blockchain activities, and providing real-time Web3 security insights with advanced graph analytics.

## 🌟 Introducing NeuroSpark 0.9.2: Comprehensive Blockchain Intelligence

The latest version completely transforms the platform into a powerful blockchain intelligence system:

- **Multi-Chain Web3 Data Integration**: Seamlessly ingest and model data from Ethereum and other blockchain networks with our high-performance connectors
- **Complete Blockchain Entity Modeling**: Comprehensive tracking and analysis of wallets, transactions, smart contracts, and events in a unified data model
- **Advanced Risk Intelligence**: Sophisticated multi-factor risk scoring for all blockchain entities using behavioral pattern analysis
- **Smart Contract Security Analysis**: Robust vulnerability detection and risk assessment for smart contract code with detailed reports
- **Real-time Blockchain Monitoring**: Instant detection and alerting for suspicious blockchain activities through our WebSocket-based alert system
- **LLM-Powered Natural Language Queries**: Intuitive natural language interface for complex blockchain data analysis powered by Ollama integration
- **Blockchain-Specific Graph Analytics**: Specialized algorithms designed specifically for blockchain transaction flow analysis and network visualization

## Core Features

- **Blockchain Integration & Analysis**:
  - **Multi-chain Support**: Connectors for Ethereum (primary) with extensible architecture for Solana and other chains
  - **Comprehensive Entity Models**: Complete data models for wallets, transactions, contracts, and events with rich metadata
  - **Graph-based Blockchain Analysis**: Advanced relationship modeling to uncover connections between blockchain entities
  - **Risk Intelligence Engine**: Sophisticated multi-factor risk scoring system with behavioral pattern analysis
  - **Real-time Monitoring System**: WebSocket-based alerting for immediate notification of suspicious blockchain activities
  - **Smart Contract Security**: Vulnerability detection and risk assessment for deployed smart contracts

- **Advanced Graph Analytics for Blockchain**:
  - **Transaction Flow Analysis**: Follow the money through complex transaction paths with NetworkX integration
  - **Entity Importance Measurement**: Multiple centrality algorithms to identify key wallets and contracts in the network
  - **Relationship Cluster Detection**: Advanced community detection to discover related entity groups
  - **Temporal Blockchain Analysis**: Track changes in network structure and entity behavior over time periods
  - **Anomaly Detection**: Identify unusual patterns and outliers in transaction networks
  - **Specialized Visualization**: Optimized layouts for complex blockchain relationship visualization

- **LLM-Powered Natural Language Interface**:
  - **Intuitive Query System**: Query complex blockchain data using simple natural language instructions
  - **Ollama Integration**: Efficient local LLM deployment with optimized performance
  - **Blockchain-Specific Prompt Engineering**: Custom templates designed for different types of blockchain analysis
  - **Context-Aware Response Generation**: Rich, informative responses with relevant blockchain context
  - **Query Translation**: Automatic conversion of natural language to optimized database queries
  - **Explainable Results**: Clear explanations of blockchain terminology and significance of findings

- **Synthetic Blockchain Data Generation**:
  - **Realistic Blockchain Patterns**: Generate statistically accurate transaction patterns based on real-world data
  - **DeFi Scenario Simulation**: Model specialized scenarios including DEX trades, lending protocols, and NFT markets
  - **Security Testing Environment**: Create test datasets with known vulnerabilities for security research
  - **Behavioral Pattern Modeling**: Simulate both normal and suspicious transaction patterns for risk testing
  - **Configurable Parameters**: Extensive customization options for all aspects of synthetic data generation

- **Enterprise-grade Infrastructure**:
  - **High-performance Backend**: FastAPI with async/await pattern for optimal throughput and responsiveness
  - **Real-time Event System**: WebSocket support for instant blockchain event notifications
  - **Optimized Graph Database**: ArangoDB with specialized indexes for efficient blockchain data querying
  - **Comprehensive Test Coverage**: Extensive test suite with 80+ tests and continuous integration
  - **Observability Stack**: Complete monitoring with Prometheus/Grafana dashboards
  - **Docker-based Deployment**: Simple deployment with containerized components including LLM integration

## System Architecture

```mermaid
graph TD
    subgraph "Application Components"
        FE[Frontend UI<br>React + TypeScript]
        BE[Backend API<br>FastAPI + Python]
        WS[WebSocket Server]
        DG[Data Generator]
        
        subgraph "Blockchain Components"
            BC[Blockchain Connectors]
            RI[Risk Intelligence]
            SC[Smart Contract Analysis]
            BA[Blockchain API]
        end
        
        subgraph "Analysis Components" 
            NX[NetworkX Integration]
            GM[Graph Metrics]
            CD[Community Detection]
            CN[Centrality Analysis]
            TF[Transaction Flow Analysis]
            AR[Anomaly Recognition]
        end
        
        subgraph "LLM Components"
            LM[LLM Integration]
            QP[Query Parser]
            PT[Prompt Templates]
        end
    end
    
    subgraph "Database"
        DB[(ArangoDB Graph Database)]
        subgraph "Entity Collections"
            WC[Wallets]
            TC[Transactions]
            CC[Contracts]
            EC[Events]
            AC[Alerts]
        end
    end
    
    subgraph "External Services"
        ETH[Ethereum API]
        SOL[Solana API]
        OL[Ollama LLM]
    end
    
    subgraph "Monitoring"
        PR[Prometheus]
        GR[Grafana Dashboards]
        LOG[Logging System]
    end
    
    US[Users] -->|Interact with| FE
    FE -->|Send Requests| BE
    BE -->|Real-time Updates| WS
    WS -->|Notifications| FE
    BE -->|Store/Query| DB
    BE -->|Generate Test Data| DG
    DG -->|Populate| DB
    
    %% Blockchain Integration
    BC -->|Ethereum Data| ETH
    BC -->|Solana Data| SOL
    BC -->|Process| BA
    BA -->|Store| DB
    BA -->|Analyze Risk| RI
    RI -->|Generate| AC
    SC -->|Analyze| CC
    
    %% NetworkX Integration
    BE <-->|Analyze| NX
    NX -->|Calculate| GM
    NX -->|Detect| CD
    NX -->|Measure| CN
    NX -->|Track| TF
    NX -->|Detect| AR
    
    %% LLM Integration
    BE <-->|Natural Language Query| LM
    LM -->|Query| OL
    LM -->|Parse| QP
    LM -->|Template| PT
    QP -->|Database Query| DB
    
    %% Monitoring
    BE -->|Metrics| PR
    PR -->|Visualize| GR
    BE -->|Log Events| LOG
    
    classDef frontend fill:#42a5f5,stroke:#1565c0,color:#fff
    classDef backend fill:#66bb6a,stroke:#2e7d32,color:#fff
    classDef database fill:#ff7043,stroke:#e64a19,color:#fff
    classDef monitoring fill:#ab47bc,stroke:#7b1fa2,color:#fff
    classDef analysis fill:#26c6da,stroke:#00838f,color:#fff
    classDef blockchain fill:#fdd835,stroke:#f57f17,color:#000
    classDef llm fill:#ec407a,stroke:#ad1457,color:#fff
    classDef external fill:#78909c,stroke:#37474f,color:#fff
    classDef user fill:#8d6e63,stroke:#4e342e,color:#fff
    
    class FE frontend
    class BE,WS,DG backend
    class DB,WC,TC,CC,EC,AC database
    class PR,GR,LOG monitoring
    class NX,GM,CD,CN,TF,AR analysis
    class BC,RI,SC,BA blockchain
    class LM,QP,PT llm
    class ETH,SOL,OL external
    class US user
```

## Domain Model

```mermaid
classDiagram
    %% Blockchain Entities
    class Wallet {
        +string address
        +string chain
        +float balance
        +string wallet_type
        +datetime first_seen
        +datetime last_active
        +float risk_score
        +List tags
        +dict metadata
        +store()
        +update()
        +get_transactions()
        +get_contracts()
        +calculate_risk()
    }
    
    class Transaction {
        +string hash
        +string chain
        +int block_number
        +datetime timestamp
        +string from_address
        +string to_address
        +float value
        +string status
        +int gas_used
        +int gas_price
        +string input_data
        +float risk_score
        +store()
        +get_receipt()
        +calculate_risk()
    }
    
    class Contract {
        +string address
        +string chain
        +string creator
        +string creation_tx
        +datetime creation_timestamp
        +bool verified
        +string name
        +string bytecode
        +string abi
        +string source_code
        +float risk_score
        +List vulnerabilities
        +store()
        +get_events()
        +analyze_security()
        +calculate_risk()
    }
    
    class Event {
        +string contract_address
        +string tx_hash
        +int block_number
        +int log_index
        +datetime timestamp
        +string name
        +string signature
        +dict params
        +store()
        +decode()
    }
    
    class Alert {
        +string id
        +datetime timestamp
        +string severity
        +string type
        +string entity
        +string entity_type
        +string description
        +string status
        +store()
        +acknowledge()
        +resolve()
    }
    
    %% Analysis Components
    class NetworkAnalysis {
        +List~Dict~ nodes
        +List~Dict~ links
        +bool directed
        +get_metrics()
        +get_centrality()
        +detect_communities()
        +get_layout()
        +get_temporal_metrics()
        +get_visualization()
    }
    
    class RiskScoring {
        +calculate_wallet_risk()
        +calculate_transaction_risk()
        +calculate_contract_risk()
        +get_high_risk_entities()
        +generate_alerts()
    }
    
    class LLMQueryEngine {
        +parse_natural_query()
        +generate_database_query()
        +format_response()
        +get_context()
    }
    
    %% Relationships
    Wallet "1" -- "many" Transaction : sends
    Wallet "1" -- "many" Transaction : receives
    Wallet "1" -- "many" Contract : deploys
    Contract "1" -- "many" Event : emits
    Transaction "1" -- "many" Event : contains
    Wallet "many" -- "many" Alert : related_to
    Contract "many" -- "many" Alert : related_to
    Transaction "many" -- "many" Alert : related_to
    
    NetworkAnalysis -- Wallet : analyzes
    NetworkAnalysis -- Transaction : analyzes
    NetworkAnalysis -- Contract : analyzes
    
    RiskScoring -- Wallet : scores
    RiskScoring -- Transaction : scores
    RiskScoring -- Contract : scores
    RiskScoring -- Alert : generates
    
    LLMQueryEngine -- Wallet : queries
    LLMQueryEngine -- Transaction : queries
    LLMQueryEngine -- Contract : queries
    LLMQueryEngine -- Event : queries
```

## Data Flow and Analytics Processes

### Blockchain Transaction Flow

```mermaid
sequenceDiagram
    participant Client as Client Application
    participant API as FastAPI Backend
    participant BlockchainAPI as Blockchain API
    participant RiskSystem as Risk Scoring System
    participant DB as ArangoDB Database
    participant WS as WebSocket Server
    
    Client->>API: GET /blockchain/wallets/{address}
    API->>BlockchainAPI: Process wallet request
    BlockchainAPI->>DB: Query wallet data
    DB-->>BlockchainAPI: Return wallet data
    BlockchainAPI->>RiskSystem: Calculate risk score
    RiskSystem-->>BlockchainAPI: Return risk assessment
    BlockchainAPI-->>API: Return wallet with risk data
    API-->>Client: Return wallet information
    
    Client->>API: GET /blockchain/transactions/{hash}
    API->>BlockchainAPI: Process transaction request
    BlockchainAPI->>DB: Query transaction
    DB-->>BlockchainAPI: Return transaction data
    BlockchainAPI->>RiskSystem: Calculate transaction risk
    RiskSystem-->>BlockchainAPI: Return risk assessment
    BlockchainAPI-->>API: Return enriched transaction
    API-->>Client: Return transaction information
    
    Note over Client,WS: For real-time monitoring
    Client->>WS: Subscribe to blockchain events
    WS-->>Client: Confirm subscription
    BlockchainAPI->>RiskSystem: New high-risk transaction detected
    RiskSystem->>DB: Store security alert
    DB->>WS: Broadcast security alert
    WS-->>Client: Push notification
```

### Risk Analysis Flow

```mermaid
sequenceDiagram
    participant Client as Client Application
    participant API as FastAPI Backend
    participant DB as ArangoDB Database
    participant RiskEngine as Risk Scoring Engine
    participant NetworkX as NetworkX Analyzer
    
    Client->>API: GET /blockchain/risk/{entity_type}
    API->>DB: Fetch high-risk entities
    DB-->>API: Return entity data
    API-->>Client: Return high-risk entities
    
    Client->>API: GET /blockchain/contracts/{address}/audit
    API->>DB: Fetch contract data
    DB-->>API: Return contract details
    API->>RiskEngine: Analyze contract security
    Note over RiskEngine: Security analysis:<br>- Reentrancy<br>- Overflow<br>- Authorization<br>- Logic flaws<br>- etc.
    RiskEngine-->>API: Return vulnerabilities
    API-->>Client: Return security audit
    
    Client->>API: POST /blockchain/risk/analyze
    Note over Client,API: Request includes address to analyze
    API->>DB: Fetch entity and related data
    DB-->>API: Return blockchain data
    API->>RiskEngine: Perform comprehensive analysis
    RiskEngine->>NetworkX: Analyze transaction patterns
    NetworkX-->>RiskEngine: Return network metrics
    Note over RiskEngine: Risk assessment:<br>- Transaction patterns<br>- Network position<br>- Historical behavior<br>- Security issues
    RiskEngine-->>API: Return risk profile
    API-->>Client: Return detailed risk analysis
    
    Client->>API: GET /blockchain/risk/alerts
    API->>DB: Fetch active alerts
    DB-->>API: Return alert data
    API->>RiskEngine: Enrich alerts with context
    RiskEngine-->>API: Return enriched alerts
    API-->>Client: Return security alerts
```

## API Endpoints

### Blockchain Data Endpoints

- `GET /blockchain/wallets/{address}` - Get detailed wallet information including balance, transaction history, and risk assessment
- `GET /blockchain/wallets/{address}/transactions` - Get all transactions involving a specific wallet with pagination and filtering
- `GET /blockchain/wallets/{address}/contracts` - Get all contracts deployed by or interacted with by a specific wallet
- `GET /blockchain/transactions/{tx_hash}` - Get comprehensive transaction details including receipt and event logs
- `GET /blockchain/contracts/{address}` - Get contract information with metadata and security assessment
- `GET /blockchain/contracts/{address}/events` - Get all events emitted by a specific contract with filtering options
- `GET /blockchain/contracts/{address}/audit` - Get detailed security audit report for a smart contract
- `POST /blockchain/wallets/batch` - Retrieve detailed information for multiple wallets in a single request
- `POST /blockchain/transactions/batch` - Retrieve detailed information for multiple transactions in a single request

### Risk Intelligence Endpoints

- `GET /blockchain/risk/{entity_type}` - Get high-risk entities by type (wallets, transactions, contracts) with customizable risk thresholds
- `GET /blockchain/risk/alerts` - Get active security alerts with severity classification and context
- `POST /blockchain/risk/analyze` - Perform comprehensive risk analysis on any blockchain entity with detailed reports
- `GET /blockchain/risk/suspicious` - Get suspicious activities detected in recent blockchain transactions
- `GET /blockchain/risk/overview` - Get aggregated risk metrics across the monitored blockchain ecosystem

### Network Graph Endpoints

- `GET /blockchain/network` - Get blockchain network visualization data with configurable depth and entity types
- `POST /blockchain/network/query` - Query blockchain network with complex filters and relationship criteria
- `GET /blockchain/network/clusters` - Get pre-identified relationship clusters among blockchain entities

### Natural Language Query Endpoints

- `POST /blockchain/query/natural` - Execute LLM-powered natural language blockchain queries with context awareness
- `POST /blockchain/query/trace` - Trace transaction paths between blockchain entities with customizable depth
- `POST /blockchain/query/pattern` - Identify specific transaction patterns among blockchain entities

### Analytics Endpoints

- `GET /analysis/metrics` - Get comprehensive blockchain network metrics with statistical analysis
- `GET /analysis/centrality` - Calculate key influential entities in the blockchain network using multiple centrality algorithms
- `GET /analysis/communities` - Detect and analyze relationship clusters within the blockchain network
- `GET /analysis/flow` - Analyze value flow and circulation patterns through the network
- `GET /analysis/temporal` - Analyze blockchain network metrics across different time periods
- `GET /analysis/visualization` - Get enhanced network visualization with integrated metrics and highlights

### Data Generation Endpoints

- `POST /generate/data` - Generate realistic synthetic blockchain data with configurable parameters
- `POST /generate/scenario` - Generate scenario-based blockchain data for specific use cases (DEX, lending, NFT, etc.)
- `POST /generate/transaction` - Generate a single synthetic blockchain transaction

For detailed information about all available endpoints, request/response formats, and examples, please refer to the [API_ENDPOINTS.md](./API_ENDPOINTS.md) file or visit the interactive API documentation at [`http://localhost:8000/docs`](http://localhost:8000/docs) when the server is running.

## Prerequisites

- Python 3.11+
- ArangoDB 3.11+
- Docker and Docker Compose
- Node.js 18+ (for frontend development)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/JtPerez-Acle/neurospark
cd neurospark
```

2. Choose one of the following startup methods:

### Initial Setup (First-time Users)
```bash
./setup.sh
```
This interactive script guides you through the first-time setup with:
- Customizable ArangoDB password configuration
- Complete services startup with a clean environment
- Database connectivity verification and troubleshooting
- Summary of available commands

### Production Deployment
```bash
./start.sh
```
Starts the full stack with:
- ArangoDB database
- Backend FastAPI service
- Prometheus and Grafana for monitoring
- Perfect for production or demonstration

### Development Environment
```bash
./start_dev.sh
```
Starts a lightweight environment with:
- ArangoDB database
- Backend FastAPI service
- Optimized for development without monitoring overhead

### Shutdown
```bash
./stop.sh
```
Gracefully stops all running services.

### Manual Local Development
```bash
# Start ArangoDB with Docker
docker-compose up -d arangodb

# Backend development setup
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
poetry install

# Run backend server
poetry run uvicorn app.main:app --reload

# Frontend development setup
cd ../kqml-parser-frontend
npm install
npm run dev
```

## Environment Variables

The application uses these environment variables:

### ArangoDB Settings
- `ARANGO_HOST`: ArangoDB host (default: `localhost`)
- `ARANGO_PORT`: ArangoDB port (default: `8529`)
- `ARANGO_DB`: ArangoDB database name (default: `blockchain_intelligence`)
- `ARANGO_USER`: ArangoDB username (default: `root`)
- `ARANGO_PASSWORD`: ArangoDB password (default: `password`)

These are set in the `docker-compose.yml` file. For local development:
```bash
export ARANGO_HOST=localhost
export ARANGO_PORT=8529
export ARANGO_DB=blockchain_intelligence
export ARANGO_USER=root
export ARANGO_PASSWORD=password
```

> **Note About ArangoDB**: 
> ArangoDB is a multi-model database that supports document, graph, and key-value storage, making it perfect for our blockchain intelligence system. The web interface (accessible at http://localhost:8529 after starting the containers) provides intuitive tools for visualizing and managing your data.
>
> Use the provided `setup.sh` script for an automated, guided setup experience.

## Running Tests

### Using run_tests.sh (Recommended)

We provide a script that handles the test setup and execution:

```bash
./run_tests.sh
```

This script will:
1. Clean up any existing test containers and volumes
2. Build a fresh test environment using Docker Compose
3. Start an ArangoDB container for testing
4. Run the test suite with coverage reporting
5. Clean up all test containers and volumes after completion

### Manual Testing

For more control over the test environment:

1. Start the test ArangoDB container:
```bash
docker-compose -f docker-compose.test.yml up -d arangodb
```

2. Run the tests:
```bash
pytest -v --cov=app --cov-report=term-missing
```
- Our test suite currently has over 80% coverage, focusing on all critical files.
- 81/81 tests passing with full blockchain terminology consistency

## Running the Application

### Using Start Scripts (Recommended)

We provide several scripts to manage the application:

1. **Production Mode:**
```bash
./start.sh
```
This script will start the complete stack including:
- ArangoDB database
- Backend API service
- Prometheus for metrics
- Grafana for dashboards
- Log aggregator

2. **Development Mode:**
```bash
./start_dev.sh
```
This starts a minimal environment with:
- ArangoDB database
- Backend API service
Perfect for development when you don't need the full monitoring stack.

3. **Stop Services:**
```bash
./stop.sh
```
This gracefully stops all running services.

### Manual Startup

For local development without Docker:
```bash
# Activate your virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Start the FastAPI server
uvicorn app.main:app --reload
```

The API will be available at:
- API: http://localhost:8000
- Interactive Documentation (Swagger UI): http://localhost:8000/docs
- Alternative Documentation (ReDoc): http://localhost:8000/redoc
- WebSocket: ws://localhost:8000/ws

The Frontend will be available at:
- http://localhost:3000 (when running the frontend separately)

## API Endpoints

### Root Endpoint
- `GET /` - Get API information and capabilities

### Blockchain Data Endpoints
- `GET /blockchain/wallets/{address}` - Get detailed wallet information
- `GET /blockchain/wallets/{address}/transactions` - Get wallet transactions
- `GET /blockchain/wallets/{address}/contracts` - Get contracts deployed or interacted with
- `GET /blockchain/wallets/batch` - Retrieve multiple wallets in a single request
- `GET /blockchain/transactions/{hash}` - Get transaction details
- `GET /blockchain/transactions/filter` - Filter transactions by criteria
- `POST /blockchain/transactions/batch` - Retrieve multiple transactions
- `GET /blockchain/contracts/{address}` - Get contract information
- `GET /blockchain/contracts/{address}/events` - Get contract events
- `GET /blockchain/contracts/{address}/audit` - Get contract security audit
- `GET /blockchain/events/filter` - Filter events by criteria
- `POST /blockchain/events/decode` - Decode event data

### Risk Intelligence Endpoints
- `GET /blockchain/risk/{entity_type}` - Get high-risk entities by type
- `GET /blockchain/risk/alerts` - Get active security alerts
- `POST /blockchain/risk/analyze` - Perform comprehensive risk analysis
- `GET /blockchain/risk/suspicious` - Get suspicious activities
- `GET /blockchain/risk/overview` - Get risk metrics and statistics

### Blockchain Network Analysis
- `GET /blockchain/network` - Get blockchain network visualization data
- `POST /blockchain/network/query` - Query blockchain network with filters
- `GET /blockchain/network/clusters` - Get entity relationship clusters

### Natural Language Query Endpoints
- `POST /blockchain/query/natural` - Execute natural language blockchain queries
- `POST /blockchain/query/trace` - Trace transaction paths
- `POST /blockchain/query/pattern` - Identify transaction patterns

### Graph Analytics Endpoints
- `GET /analysis/metrics` - Get blockchain network metrics
- `GET /analysis/centrality` - Calculate key entity influence metrics
- `GET /analysis/communities` - Detect entity communities
- `GET /analysis/flow` - Analyze value flow through the network
- `GET /analysis/temporal` - Track metrics over time
- `GET /analysis/visualization` - Get enhanced visualization data

### Data Generation Endpoints
- `POST /generate/data` - Generate synthetic blockchain data
- `POST /generate/scenario` - Generate blockchain scenario data
- `POST /generate/transaction` - Generate a single synthetic transaction

### Database Administration
- `DELETE /admin/database/clear` - Clear all data from the database
- `POST /admin/database/setup` - Initialize database collections and indexes

### WebSocket Endpoints
- `WebSocket /ws` - Real-time blockchain event notifications

For detailed API documentation with request/response examples, please refer to the [API_ENDPOINTS.md](./API_ENDPOINTS.md) file or visit the Swagger UI at http://localhost:8000/docs when the backend is running.

## Docker Deployment

The full stack can be deployed using Docker Compose:

```mermaid
graph TD
    subgraph "Docker Environment"
        FE[Frontend Container<br>Node.js + Vite]
        BE[Backend Container<br>FastAPI + Python]
        DB[ArangoDB Container]
        NET[Docker Network]
    end
    
    FE -->|port 3000| USER[User Browser]
    USER -->|port 8000| BE
    BE -->|http:// port 8529| DB
    
    FE --- NET
    BE --- NET
    DB --- NET
    
    classDef container fill:#2196f3,stroke:#0d47a1,color:#fff
    classDef network fill:#4caf50,stroke:#1b5e20,color:#fff
    classDef external fill:#ff9800,stroke:#e65100,color:#fff
    
    class FE,BE,DB container
    class NET network
    class USER external
```

## Database Schema

### Blockchain Graph Database

The system uses ArangoDB as a specialized graph database for blockchain data, providing excellent performance for complex relationship queries:

```mermaid
erDiagram
    WALLET ||--o{ TRANSACTION : "SENDS"
    WALLET ||--o{ TRANSACTION : "RECEIVES"
    WALLET ||--o{ CONTRACT : "DEPLOYS"
    CONTRACT ||--o{ EVENT : "EMITS"
    TRANSACTION ||--o{ EVENT : "CONTAINS"
    WALLET }|--o{ ALERT : "RELATED_TO"
    CONTRACT }|--o{ ALERT : "RELATED_TO"
    TRANSACTION }|--o{ ALERT : "RELATED_TO"
    
    WALLET {
        string _key "Wallet ID"
        string address "Blockchain address"
        string chain "Blockchain network"
        float balance "Current balance"
        string type "Wallet type (EOA, contract)"
        datetime first_seen "First activity time"
        datetime last_active "Latest activity time"
        float risk_score "Risk assessment (0-100)"
        array tags "Wallet tags/labels"
        json metadata "Chain-specific data"
    }
    
    TRANSACTION {
        string _key "Transaction hash"
        string hash "Transaction identifier"
        string chain "Blockchain network"
        int block_number "Block containing transaction"
        datetime timestamp "Transaction time"
        string from_address "Sender address"
        string to_address "Recipient address"
        float value "Transaction amount"
        string status "Transaction status"
        int gas_used "Gas consumed"
        int gas_price "Gas price"
        string input_data "Transaction input data"
        float risk_score "Risk assessment (0-100)"
        json metadata "Additional transaction data"
    }
    
    CONTRACT {
        string _key "Contract address"
        string address "Contract address"
        string chain "Blockchain network"
        string creator "Creator address"
        string creation_tx "Creation transaction hash"
        datetime creation_timestamp "Creation time"
        boolean verified "Source code verification"
        string name "Contract name"
        string bytecode "Contract bytecode"
        json abi "Contract ABI"
        string source_code "Verified source code"
        float risk_score "Risk assessment (0-100)"
        array vulnerabilities "Detected security issues"
    }
    
    EVENT {
        string _key "Event identifier"
        string contract_address "Contract address"
        string tx_hash "Transaction hash"
        int block_number "Block number"
        int log_index "Index in transaction logs"
        datetime timestamp "Event time"
        string name "Event name"
        string signature "Event signature"
        json params "Event parameters"
    }
    
    ALERT {
        string _key "Alert ID"
        datetime timestamp "Alert generation time"
        string severity "Alert severity level"
        string type "Alert classification"
        string entity "Related entity address/hash"
        string entity_type "Entity type"
        string description "Alert description"
        string status "Alert status"
    }
```

## Monitoring Dashboard

```mermaid
graph LR
    subgraph "Metrics Collection"
        APP[Application Metrics]
        SYS[System Metrics]
        DB[Database Metrics]
    end
    
    subgraph "Monitoring Stack"
        PROM[Prometheus]
        GRAF[Grafana]
        LOGS[Log Aggregator]
    end
    
    subgraph "Visualization"
        PERF[Performance Dashboard]
        ERR[Error Tracking]
        USAGE[Usage Statistics]
    end
    
    APP --> PROM
    SYS --> PROM
    DB --> PROM
    
    APP --> LOGS
    
    PROM --> GRAF
    LOGS --> GRAF
    
    GRAF --> PERF
    GRAF --> ERR
    GRAF --> USAGE
    
    classDef source fill:#4caf50,stroke:#1b5e20,color:#fff
    classDef processing fill:#ff9800,stroke:#e65100,color:#fff
    classDef output fill:#2196f3,stroke:#0d47a1,color:#fff
    
    class APP,SYS,DB source
    class PROM,GRAF,LOGS processing
    class PERF,ERR,USAGE output
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests to ensure they pass
5. Submit a pull request

## License

MIT License. See LICENSE file for details.
