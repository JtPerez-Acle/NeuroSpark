# NeuroSpark Web3 Migration Plan

## Cleanup & Refactoring Checklist

### Components to Remove/Replace
- [x] Replace agent-based models with blockchain entities
  - [x] Remove `app/database/models/agent.py`
  - [x] Remove `app/database/models/interaction.py`
  - [x] Remove `app/database/models/run.py`
  - [x] Remove `app/database/models/message.py`

- [x] Remove agent-specific database operations
  - [x] Remove `app/database/operations/agents.py`
  - [x] Remove `app/database/operations/interactions.py`
  - [x] Remove `app/database/operations/messages.py`
  - [x] Remove `app/database/operations/runs.py`

- [ ] Update or replace route handlers
  - [ ] Refactor `app/graph_routes.py` for blockchain visualization
  - [ ] Update `app/query_routes.py` for blockchain queries
  - [x] Remove `app/kqml_handler.py` (not needed for blockchain)
  - [ ] Refactor `app/websocket_handler.py` for blockchain events

### Blockchain Components to Implement

1. **New Directory Structure**
   - [x] Create `app/blockchain/` directory
     - [x] `connectors/` - API clients for different blockchains
     - [x] `models/` - Data models for blockchain entities
     - [x] `parsers/` - Transaction and event parsers
     - [x] `indexer/` - Blockchain data indexing service

   - [x] Create `app/risk/` directory 
     - [x] `scoring/` - Risk assessment algorithms
     - [x] `detectors/` - Pattern detection
     - [x] `alerts/` - Alert generation

   - [x] Create `app/llm/` directory
     - [x] `query_parser/` - Natural language to query translation
     - [x] `ollama/` - Ollama integration
     - [x] `prompts/` - Prompt templates

2. **Database Schema Updates**
   - [x] Implement wallet collection in ArangoDB
   - [x] Implement transaction collection in ArangoDB
   - [x] Implement contract collection in ArangoDB
   - [x] Implement event collection in ArangoDB
   - [ ] Create blockchain-specific edge definitions

3. **API Implementation**
   - [x] Implement `/blockchain/wallets` endpoints
   - [x] Implement `/blockchain/transactions` endpoints
   - [x] Implement `/blockchain/contracts` endpoints
   - [x] Implement `/blockchain/events` endpoints
   - [x] Implement `/blockchain/risk` endpoints
   - [ ] Implement `/blockchain/query` endpoints

4. **Core Components**
   - [x] Implement Ethereum blockchain connector (Web3.py)
   - [ ] Implement transaction ingestion pipeline
   - [ ] Implement smart contract analysis
   - [ ] Implement LLM-based natural language query system
   - [ ] Create risk scoring algorithms

## Implementation Phases

### Phase 1: Blockchain Foundation
- Remove obsolete agent-based code
- Implement core blockchain data models
- Set up Ethereum blockchain connector
- Create blockchain database schema

### Phase 2: Risk Intelligence & Analytics
- Implement transaction pattern analysis
- Develop smart contract vulnerability detection
- Create wallet behavior analysis
- Build risk scoring algorithms

### Phase 3: LLM Integration & UI
- Set up Ollama integration
- Implement natural language query processing
- Create interactive visualization for blockchain data
- Build dashboards for risk metrics and alerts