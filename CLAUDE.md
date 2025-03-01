# NeuroSpark Development Guide

## Project Overview
NeuroSpark is an AI-Powered Blockchain Intelligence System for analyzing smart contracts, monitoring blockchain activities, and providing real-time Web3 security insights. Building on our existing Multi-Agent Graph Intelligence platform, the system now provides:

- Blockchain data ingestion and modeling (multiple chains support)
- Smart contract and wallet risk analysis
- LLM-based natural language querying of blockchain data
- Advanced graph analytics for DeFi flow analysis
- Real-time monitoring and alerts for suspicious activities
- Synthetic data generation for Web3 and agent simulation

## Key Commands

### Development
```bash
# Start development environment (without monitoring stack)
./start_dev.sh

# Start full environment (with monitoring)
./start.sh

# Stop all containers
./stop.sh

# Run tests
./run_tests.sh
```

### Testing
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_database.py

# Run tests with coverage
pytest --cov=app tests/
```

### Docker
```bash
# Build and start all services
docker-compose up -d

# Development mode (minimal setup)
docker-compose -f docker-compose.simple.yml up -d

# Testing environment
docker-compose -f docker-compose.test.yml up -d
```

## Coding Standards

### Python Style
- Follow PEP 8 guidelines
- Use type hints for function parameters and return values
- Document functions with docstrings (Google style)
- Maximum line length: 100 characters
- Use black for code formatting
- Use isort for import sorting (import order: standard library, third-party, local)

### Project Structure
- Keep modules focused and single-purpose
- Place database models in `app/database/models/`
- Place database operations in `app/database/operations/`
- Add routes in appropriate route files (e.g., `app/blockchain_routes.py`)
- Add new analysis algorithms in `app/analysis/`

### Web3 Project Structure
- Organize blockchain functionality in the `app/blockchain/` directory:
  - `app/blockchain/connectors/` - Chain-specific API clients
  - `app/blockchain/models/` - Blockchain entity models
  - `app/blockchain/parsers/` - Transaction and event parsers
  - `app/blockchain/indexer/` - Blockchain data indexing service
- Place risk intelligence code in `app/risk/` directory:
  - `app/risk/scoring/` - Risk assessment algorithms
  - `app/risk/detectors/` - Pattern detection for suspicious activities
  - `app/risk/alerts/` - Alert generation and management
- Organize LLM functionality in `app/llm/` directory:
  - `app/llm/query_parser/` - Natural language to query translation
  - `app/llm/ollama/` - Ollama integration
  - `app/llm/prompts/` - Prompt templates for different query types

### Naming Conventions
- Class names: PascalCase (e.g., `WalletRiskAnalyzer`)
- Functions and methods: snake_case (e.g., `calculate_risk_score`)
- Variables: snake_case (e.g., `transaction_hash`)
- Constants: UPPER_SNAKE_CASE (e.g., `MAX_TRANSACTION_BATCH`)
- Private methods/attributes: leading underscore (e.g., `_validate_transaction`)
- Type aliases: PascalCase with postfix "Type" (e.g., `TransactionType`)
- Blockchain-specific classes: Prefix with chain name (e.g., `EthereumConnector`, `SolanaParser`)

### Testing
- Write unit tests for all new functionality
- Use pytest fixtures for test setup
- Mock external dependencies
- Aim for high test coverage
- Test both success and error cases

### Web3 Testing
- Use Ganache (or anvil from Foundry) for local Ethereum testing
- Create test fixtures for blockchain data and events
- Mock blockchain API responses for deterministic tests
- Use VCR.py to record and replay blockchain API interactions
- Create separate test modules for each blockchain connector
- Implement test helpers for common blockchain operations
- Use parameterized tests for multi-chain compatibility checks
- Apply snapshot testing for complex blockchain data structures

### Git Workflow
- Create feature branches from `main`
- Use descriptive commit messages with prefixes:
  - `[core]` - Core functionality
  - `[feat]` - New features
  - `[fix]` - Bug fixes
  - `[docs]` - Documentation
  - `[test]` - Tests
  - `[refactor]` - Code refactoring
  - `[perf]` - Performance improvements
  - `[scenarios]` - Synthetic scenario generation

## Architecture Notes

### Key Components
1. **FastAPI Backend**: REST API and WebSocket support
2. **ArangoDB**: Graph database for blockchain entities and relationships
3. **Web3.py/Web3-Solana**: Blockchain API connectors
4. **NetworkX**: Graph analysis algorithms
5. **Ollama**: Local LLM deployment for NL queries
6. **Prometheus/Grafana**: Monitoring and metrics
7. **Docker**: Containerized deployment

### Web3 Dependencies
- **Core Dependencies**:
  - web3.py (^6.0.0): Ethereum blockchain interaction
  - solana.py (^0.30.0): Solana blockchain interaction
  - ollama-python (^0.1.0): Ollama LLM client
  - aiohttp (^3.8.5): Async HTTP client for blockchain APIs
  - pydantic (^2.0.0): Data validation and settings management

- **Analytics Dependencies**:
  - etherscan-python (^2.2.0): Etherscan API client for contract verification
  - py-solana-parser (^0.1.0): Solana program parser
  - slither-analyzer (^0.9.0): Solidity static analyzer
  - networkx (^3.0): Graph analysis library

- **Processing Dependencies**:
  - redis (^4.5.0): Caching and message broker
  - asyncio (stdlib): Asynchronous I/O and event loop
  - backoff (^2.2.0): Retry functionality for API calls

### Docker Configuration
- **Base Image**: Python 3.10 Alpine for lightweight containers
- **Container Setup**:
  - Main API container with FastAPI
  - ArangoDB container for graph storage
  - Ollama container for LLM integration
  - Redis container for caching and message queue
  - Monitoring stack (Prometheus, Grafana)

- **Network Configuration**:
  - Isolated network for container communication
  - Exposed ports for API, monitoring dashboards

- **Volume Mounts**:
  - Persistent storage for ArangoDB data
  - Ollama models directory for LLM persistence

### Database Structure
- **Agents**: Nodes representing entities
- **Interactions**: Edges between agents with timestamps and content
- **Runs**: Grouping of interactions for specific sessions
- **Participations**: Connections between agents and runs

### Blockchain Database Schema
- **Collections**:
  - **Wallets**: Blockchain addresses and metadata
    - `_key`: Address hash
    - `address`: Wallet address (format depends on chain)
    - `chain`: Blockchain identifier
    - `balance`: Current balance
    - `first_seen`: Timestamp of first activity
    - `last_active`: Timestamp of latest activity
    - `type`: Wallet type (EOA, contract, etc.)
    - `tags`: Array of labels/categories
    - `risk_score`: Calculated risk assessment
    - `metadata`: Additional chain-specific data

  - **Transactions**: Blockchain transactions
    - `_key`: Transaction hash
    - `hash`: Transaction identifier
    - `block_number`: Block containing the transaction
    - `timestamp`: Transaction timestamp
    - `from`: Sender address
    - `to`: Recipient address
    - `value`: Transaction amount
    - `gas_used`: Gas consumed
    - `gas_price`: Gas price
    - `status`: Transaction status
    - `chain`: Blockchain identifier
    - `input_data`: Transaction input data
    - `risk_score`: Calculated risk assessment

  - **Contracts**: Smart contract information
    - `_key`: Contract address hash
    - `address`: Contract address
    - `chain`: Blockchain identifier
    - `creator`: Creator address
    - `creation_tx`: Creation transaction hash
    - `creation_timestamp`: Creation time
    - `verified`: Whether source code is verified
    - `name`: Contract name (if known)
    - `bytecode`: Contract bytecode
    - `abi`: Contract ABI (if available)
    - `source_code`: Verified source code (if available)
    - `risk_score`: Calculated risk assessment
    - `vulnerabilities`: Array of detected vulnerabilities

  - **Events**: Smart contract events
    - `_key`: Event identifier (tx_hash + log_index)
    - `contract`: Contract address
    - `tx_hash`: Transaction hash
    - `block_number`: Block containing the event
    - `timestamp`: Event timestamp
    - `name`: Event name
    - `signature`: Event signature
    - `params`: Event parameters
    - `chain`: Blockchain identifier

  - **Alerts**: Security alerts and notifications
    - `_key`: Alert UUID
    - `timestamp`: Alert generation time
    - `severity`: Alert severity (low, medium, high, critical)
    - `type`: Alert type
    - `entity`: Related entity (address, tx hash, etc.)
    - `description`: Alert description
    - `context`: Supporting evidence
    - `status`: Alert status (new, acknowledged, resolved, etc.)

- **Graph Relationships**:
  - **WalletToWallet**: Transaction relationships between wallets
  - **WalletToContract**: Interactions between wallets and contracts
  - **ContractToContract**: Contract calls and interactions
  - **EntityToAlert**: Connections between entities and security alerts

### API Structure
- `/agents` - Agent management
- `/interactions` - Interaction management
- `/network` - Network data and filters
- `/graph` - Graph visualization data
- `/analysis/*` - Network analysis endpoints
- `/generate/*` - Synthetic data endpoints
- `/query` - Natural language queries

### Blockchain API Endpoints
- `/blockchain/wallets`
  - `GET /blockchain/wallets/{address}` - Get wallet details
  - `GET /blockchain/wallets/{address}/transactions` - Get wallet transactions
  - `GET /blockchain/wallets/{address}/interactions` - Get wallet contract interactions
  - `GET /blockchain/wallets/{address}/risk` - Get wallet risk assessment
  - `POST /blockchain/wallets/batch` - Retrieve multiple wallets

- `/blockchain/transactions`
  - `GET /blockchain/transactions/{hash}` - Get transaction details
  - `GET /blockchain/transactions/filter` - Filter transactions by criteria
  - `GET /blockchain/transactions/risk` - Get high-risk transactions
  - `POST /blockchain/transactions/batch` - Retrieve multiple transactions

- `/blockchain/contracts`
  - `GET /blockchain/contracts/{address}` - Get contract details
  - `GET /blockchain/contracts/{address}/events` - Get contract events
  - `GET /blockchain/contracts/{address}/audit` - Get contract security audit
  - `GET /blockchain/contracts/{address}/interactions` - Get contract interactions
  - `GET /blockchain/contracts/{address}/risk` - Get contract risk assessment
  - `POST /blockchain/contracts/batch` - Retrieve multiple contracts

- `/blockchain/events`
  - `GET /blockchain/events/filter` - Filter events by criteria
  - `GET /blockchain/events/recent` - Get recent events
  - `POST /blockchain/events/decode` - Decode event data

- `/blockchain/risk`
  - `GET /blockchain/risk/overview` - Get overall risk metrics
  - `GET /blockchain/risk/alerts` - Get active risk alerts
  - `GET /blockchain/risk/suspicious` - Get suspicious activities
  - `POST /blockchain/risk/analyze` - Analyze entity for risks

- `/blockchain/query`
  - `POST /blockchain/query/natural` - Natural language blockchain query
  - `POST /blockchain/query/trace` - Trace transaction flow
  - `POST /blockchain/query/pattern` - Find transaction patterns

## Web3 Architecture & Technical Decisions

### Blockchain Data Ingestion
- **Technology Choice**: Web3.py for Ethereum, web3-solana for Solana
- **Approach**: Event-based streaming with backfilling capability
- **Indexing Strategy**: Hybrid approach with on-demand and pre-computed indexes
- **Data Models**: 
  - Transactions (hash, from, to, value, timestamp, gas, status)
  - Wallets (address, balance, first_seen, last_active, risk_score)
  - Smart Contracts (address, creator, creation_timestamp, bytecode, verified_source, abi, risk_score)
  - Events (contract, name, params, block, transaction)

### Risk Scoring System
- **Algorithm**: Composite scoring using multiple risk factors with weighted influence
- **Risk Categories**:
  - Transaction patterns (unusual amounts, frequency, gas)
  - Code vulnerabilities (reentrancy, overflow, etc.)
  - Network behavior (centrality, interaction patterns)
  - Historical associations (with known risky entities)
- **Score Normalization**: 0-100 scale with categorization (Low: 0-25, Medium: 26-50, High: 51-75, Critical: 76-100)
- **Implementation**: Modular pipeline with pluggable detection algorithms

### LLM Integration
- **Framework**: Ollama for local deployment
- **Models**: Llama 3 8B/70B (based on hardware capability)
- **Prompt Design**: Two-stage approach:
  1. Query understanding and translation to graph/blockchain query format
  2. Result processing and natural language response generation
- **Deployment**: Docker container with GPU acceleration if available
- **Caching Strategy**: LRU cache for frequent queries with TTL-based invalidation

### Database Schema Extensions
- **Wallet Collection**: Stores wallet addresses and metadata
- **Transaction Collection**: Stores blockchain transactions
- **Contract Collection**: Stores smart contract data and analysis
- **Risk Collection**: Stores risk assessments and scores
- **Alert Collection**: Stores generated security alerts
- **Edge Definitions**:
  - WalletToWallet (transaction relationship)
  - WalletToContract (interaction relationship)
  - ContractToContract (call relationship)

### Real-time Processing
- **Technology**: Kafka or Redis Streams for event processing
- **WebSocket Enhancement**: Extended subscription capabilities for blockchain events
- **Alert Pipeline**: Multi-stage processing with filtering, correlation, and notification

### Performance Considerations
- **Chunked Processing**: Process blockchain data in time-bounded chunks
- **Selective Indexing**: Index only frequently queried data patterns
- **Query Optimization**: Use AQL query optimization for complex traversals
- **Caching Layer**: Redis for high-frequency data access patterns
- **Background Processing**: Asynchronous risk analysis and pattern detection

## Enhancement Areas
- Implement blockchain-specific graph algorithms
- Add cross-chain entity resolution
- Develop smart contract vulnerability scanning
- Enhance LLM-based query capabilities
- Implement DeFi protocol-specific analytics
- Add advanced visualization for transaction flows
- Build alert management system
- Create risk scoring customization