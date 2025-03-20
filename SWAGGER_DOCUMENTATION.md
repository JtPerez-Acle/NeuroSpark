# NeuroSpark Blockchain Intelligence API Swagger Documentation

This document provides information about the Swagger API documentation for the NeuroSpark Blockchain Intelligence System.

## Accessing Swagger Documentation

When the backend is running, you can access the Swagger UI documentation at:

```
http://localhost:8000/docs
```

And the ReDoc alternative documentation at:

```
http://localhost:8000/redoc
```

## New in Version 0.9.0: Blockchain Intelligence

The NeuroSpark backend now includes comprehensive blockchain analytics features:

- **Blockchain Data Ingestion**: Support for Ethereum blockchain data with expandable architecture
- **Smart Contract Analysis**: Risk assessment and monitoring for deployed contracts
- **Wallet Intelligence**: Address profiling, transaction history analysis, and risk scoring
- **Transaction Monitoring**: Analyze transaction patterns and identify suspicious activities
- **Graph Network Analysis**: Visualize and analyze relationships between blockchain entities
- **LLM-Powered Queries**: Natural language processing for blockchain data exploration
- **Risk Scoring System**: Multi-factor risk assessment for blockchain entities
- **Real-time Alerts**: Notification system for suspicious blockchain activities

These endpoints are fully documented in Swagger UI and can be used to gain deeper insights into blockchain entity relationships and activities.

## Key Models Documentation

### WalletModel

This model represents a blockchain wallet/address:

```json
{
  "address": "string (required, blockchain address)",
  "chain": "string (e.g., 'ethereum', 'solana')",
  "balance": "number (current balance)",
  "first_seen": "string (ISO datetime)",
  "last_active": "string (ISO datetime)",
  "type": "string (e.g., 'EOA', 'contract')",
  "tags": ["array of strings (optional)"],
  "risk_score": "number (0-100)",
  "metadata": "object (optional)"
}
```

### TransactionModel

Represents a blockchain transaction:

```json
{
  "hash": "string (transaction hash)",
  "block_number": "integer",
  "timestamp": "string (ISO datetime)",
  "from": "string (sender address)",
  "to": "string (recipient address)",
  "value": "string (transaction amount)",
  "gas_used": "integer",
  "gas_price": "string",
  "status": "boolean (success/failure)",
  "chain": "string (blockchain name)",
  "input_data": "string (transaction input data)",
  "risk_score": "number (0-100, optional)"
}
```

### ContractModel

Represents a smart contract:

```json
{
  "address": "string (contract address)",
  "chain": "string (blockchain name)",
  "creator": "string (creator address)",
  "creation_tx": "string (creation transaction hash)",
  "creation_timestamp": "string (ISO datetime)",
  "verified": "boolean (source code verification status)",
  "name": "string (contract name, if known)",
  "bytecode": "string (contract bytecode)",
  "abi": "array (contract ABI, if available)",
  "source_code": "string (verified source code, if available)",
  "risk_score": "number (0-100)",
  "vulnerabilities": ["array of vulnerability objects"]
}
```

### EventModel

Represents a smart contract event:

```json
{
  "contract": "string (contract address)",
  "tx_hash": "string (transaction hash)",
  "block_number": "integer",
  "timestamp": "string (ISO datetime)",
  "name": "string (event name)",
  "signature": "string (event signature)",
  "params": "object (event parameters)",
  "chain": "string (blockchain name)"
}
```

### AlertModel

Represents a security alert:

```json
{
  "timestamp": "string (ISO datetime)",
  "severity": "string (low, medium, high, critical)",
  "type": "string (alert type)",
  "entity": "string (related entity address or transaction hash)",
  "description": "string (alert description)",
  "context": "object (supporting evidence)",
  "status": "string (new, acknowledged, resolved)"
}
```

### GraphData Model

Used for blockchain graph visualization:

```json
{
  "nodes": [
    {
      "id": "string (address)",
      "label": "string (name or address)",
      "type": "string (wallet, contract, etc.)",
      "risk_score": "number (0-100)",
      "details": "string (optional)",
      "timestamp": "string (ISO datetime, optional)"
    }
  ],
  "links": [
    {
      "id": "string (transaction hash)",
      "source": "string (from address)",
      "target": "string (to address)",
      "value": "number (transaction value)",
      "timestamp": "string (ISO datetime)"
    }
  ]
}
```

### Query Model

Used for natural language blockchain queries:

```json
{
  "query": "string (natural language query text)"
}
```

Example queries:
- "Find all transactions with value greater than 10 ETH"
- "Show interactions between address 0x123... and 0x456..."
- "List high-risk contracts deployed in the last week"
- "Trace the flow of funds from address 0x789..."

### BlockchainDataParams Model

Used for generating synthetic blockchain data:

```json
{
  "numWallets": "integer (> 0)",
  "numTransactions": "integer (> 0)",
  "chainType": "string (ethereum, solana, etc.)"
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

### Get Wallet Details

```bash
curl -X 'GET' \
  'http://localhost:8000/blockchain/wallets/0x1234567890abcdef1234567890abcdef12345678' \
  -H 'accept: application/json'
```

### Get Transaction Details

```bash
curl -X 'GET' \
  'http://localhost:8000/blockchain/transactions/0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890' \
  -H 'accept: application/json'
```

### Get Contract Risk Assessment

```bash
curl -X 'GET' \
  'http://localhost:8000/blockchain/contracts/0x1234567890abcdef1234567890abcdef12345678/risk' \
  -H 'accept: application/json'
```

### Generate Synthetic Blockchain Data

```bash
curl -X 'POST' \
  'http://localhost:8000/generate/blockchain' \
  -H 'Content-Type: application/json' \
  -d '{
  "numWallets": 10,
  "numTransactions": 50,
  "chainType": "ethereum"
}'
```

### Analyze Transaction Flow

```bash
curl -X 'POST' \
  'http://localhost:8000/blockchain/query/trace' \
  -H 'Content-Type: application/json' \
  -d '{
  "address": "0x1234567890abcdef1234567890abcdef12345678",
  "depth": 3,
  "direction": "outgoing"
}'
```

### Natural Language Blockchain Query

```bash
curl -X 'POST' \
  'http://localhost:8000/blockchain/query/natural' \
  -H 'Content-Type: application/json' \
  -d '{
  "query": "Find high-risk transactions involving contract 0x1234567890abcdef1234567890abcdef12345678"
}'
```

### Get Graph Visualization Data

```bash
curl -X 'GET' \
  'http://localhost:8000/graph?address=0x1234567890abcdef1234567890abcdef12345678&depth=2'
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