# NeuroSpark - API Documentation

This document provides detailed information about all available API endpoints in the NeuroSpark Blockchain Intelligence System.

## Version

Current Version: **0.9.0** (Unreleased)

Latest changes:
- Comprehensive Web3/Blockchain integration
- Wallet, Transaction, Contract, and Event data models
- Risk scoring for blockchain entities
- Real-time blockchain monitoring
- Natural language querying for blockchain data
- Enhanced network visualization for blockchain entities

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
    "message": "NeuroSpark Blockchain Intelligence API"
  }
  ```

### Blockchain Endpoints

#### Wallet Operations

##### Get Wallet
- **Endpoint**: `GET /blockchain/wallets/{address}`
- **Description**: Get wallet information from the database
- **Parameters**:
  - `address`: string (path parameter) - Wallet address
  - `chain`: string (query parameter, default: "ethereum") - Blockchain identifier
- **Response**:
  ```json
  {
    "address": "0x1234567890abcdef1234567890abcdef12345678",
    "chain": "ethereum",
    "balance": 1500000000000000000,
    "wallet_type": "EOA",
    "first_seen": "2023-01-15T08:30:45Z",
    "last_active": "2023-02-28T14:22:10Z",
    "risk_score": 35.5,
    "tags": ["exchange", "high-volume"]
  }
  ```
- **Error Codes**:
  - `404`: Wallet not found
  - `500`: Server error

##### Get Wallet Transactions
- **Endpoint**: `GET /blockchain/wallets/{address}/transactions`
- **Description**: Get transactions for a wallet
- **Parameters**:
  - `address`: string (path parameter) - Wallet address
  - `chain`: string (query parameter, default: "ethereum") - Blockchain identifier
  - `limit`: integer (query parameter, default: 20) - Maximum number of transactions to return
  - `offset`: integer (query parameter, default: 0) - Number of transactions to skip
  - `sort_field`: string (query parameter, default: "timestamp") - Field to sort by
  - `sort_direction`: string (query parameter, default: "desc") - Sort direction (asc or desc)
- **Response**:
  ```json
  {
    "items": [
      {
        "hash": "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
        "chain": "ethereum",
        "block_number": 16459873,
        "timestamp": "2023-02-28T14:22:10Z",
        "from_address": "0x1234567890abcdef1234567890abcdef12345678",
        "to_address": "0xabcdef1234567890abcdef1234567890abcdef1234",
        "value": 500000000000000000,
        "status": "success",
        "gas_used": 21000,
        "gas_price": 20000000000,
        "risk_score": 12.3
      }
    ],
    "count": 1
  }
  ```
- **Error Codes**:
  - `404`: Wallet not found
  - `500`: Server error

##### Get Wallet Contracts
- **Endpoint**: `GET /blockchain/wallets/{address}/contracts`
- **Description**: Get contracts deployed or interacted with by a wallet
- **Parameters**:
  - `address`: string (path parameter) - Wallet address
  - `chain`: string (query parameter, default: "ethereum") - Blockchain identifier
  - `limit`: integer (query parameter, default: 20) - Maximum number of contracts to return
  - `offset`: integer (query parameter, default: 0) - Number of contracts to skip
- **Response**:
  ```json
  {
    "items": [
      {
        "address": "0xabcdef1234567890abcdef1234567890abcdef1234",
        "chain": "ethereum",
        "creator": "0x1234567890abcdef1234567890abcdef12345678",
        "creation_timestamp": "2023-01-20T10:15:33Z",
        "verified": true,
        "name": "TokenSwap",
        "risk_score": 25.8,
        "vulnerabilities": []
      }
    ],
    "count": 1
  }
  ```
- **Error Codes**:
  - `404`: Wallet not found
  - `500`: Server error

#### Transaction Operations

##### Get Transaction
- **Endpoint**: `GET /blockchain/transactions/{tx_hash}`
- **Description**: Get transaction information from the database
- **Parameters**:
  - `tx_hash`: string (path parameter) - Transaction hash
  - `chain`: string (query parameter, default: "ethereum") - Blockchain identifier
- **Response**:
  ```json
  {
    "hash": "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
    "chain": "ethereum",
    "block_number": 16459873,
    "timestamp": "2023-02-28T14:22:10Z",
    "from_address": "0x1234567890abcdef1234567890abcdef12345678",
    "to_address": "0xabcdef1234567890abcdef1234567890abcdef1234",
    "value": 500000000000000000,
    "status": "success",
    "gas_used": 21000,
    "gas_price": 20000000000,
    "risk_score": 12.3
  }
  ```
- **Error Codes**:
  - `404`: Transaction not found
  - `500`: Server error

#### Contract Operations

##### Get Contract
- **Endpoint**: `GET /blockchain/contracts/{address}`
- **Description**: Get contract information from the database
- **Parameters**:
  - `address`: string (path parameter) - Contract address
  - `chain`: string (query parameter, default: "ethereum") - Blockchain identifier
- **Response**:
  ```json
  {
    "address": "0xabcdef1234567890abcdef1234567890abcdef1234",
    "chain": "ethereum",
    "creator": "0x1234567890abcdef1234567890abcdef12345678",
    "creation_timestamp": "2023-01-20T10:15:33Z",
    "verified": true,
    "name": "TokenSwap",
    "risk_score": 25.8,
    "vulnerabilities": []
  }
  ```
- **Error Codes**:
  - `404`: Contract not found
  - `500`: Server error

##### Get Contract Events
- **Endpoint**: `GET /blockchain/contracts/{address}/events`
- **Description**: Get events for a contract
- **Parameters**:
  - `address`: string (path parameter) - Contract address
  - `chain`: string (query parameter, default: "ethereum") - Blockchain identifier
  - `event_name`: string (query parameter, optional) - Optional event name filter
  - `from_block`: integer (query parameter, optional) - Optional starting block number
  - `to_block`: integer (query parameter, optional) - Optional ending block number
  - `limit`: integer (query parameter, default: 20) - Maximum number of events to return
  - `offset`: integer (query parameter, default: 0) - Number of events to skip
- **Response**:
  ```json
  {
    "items": [
      {
        "contract_address": "0xabcdef1234567890abcdef1234567890abcdef1234",
        "tx_hash": "0xfedcba0987654321fedcba0987654321fedcba0987654321fedcba0987654321",
        "block_number": 16459900,
        "log_index": 2,
        "timestamp": "2023-02-28T15:30:22Z",
        "name": "Transfer",
        "signature": "Transfer(address,address,uint256)",
        "params": {
          "from": "0x1234567890abcdef1234567890abcdef12345678",
          "to": "0xfedcba0987654321fedcba0987654321fedcba09",
          "value": "1000000000000000000"
        }
      }
    ],
    "count": 1
  }
  ```
- **Error Codes**:
  - `404`: Contract not found
  - `500`: Server error

#### Risk Operations

##### Get High-Risk Entities
- **Endpoint**: `GET /blockchain/risk/{entity_type}`
- **Description**: Get high-risk entities from the database
- **Parameters**:
  - `entity_type`: string (path parameter) - Entity type (wallets, contracts, transactions)
  - `min_risk_score`: float (query parameter, default: 75.0) - Minimum risk score
  - `limit`: integer (query parameter, default: 20) - Maximum number of entities to return
- **Response**:
  ```json
  {
    "entity_type": "wallets",
    "min_risk_score": 75.0,
    "count": 2,
    "items": [
      {
        "address": "0x9876543210abcdef9876543210abcdef98765432",
        "chain": "ethereum",
        "wallet_type": "EOA",
        "risk_score": 85.2,
        "tags": ["suspicious"]
      },
      {
        "address": "0x5432109876abcdef5432109876abcdef54321098",
        "chain": "ethereum",
        "wallet_type": "contract",
        "risk_score": 78.4,
        "tags": ["high-risk"]
      }
    ]
  }
  ```
- **Error Codes**:
  - `400`: Invalid entity type
  - `500`: Server error

##### Get Active Alerts
- **Endpoint**: `GET /blockchain/risk/alerts`
- **Description**: Get active security alerts from the database
- **Parameters**:
  - `severity`: string (query parameter, optional) - Filter by severity level (low, medium, high, critical)
  - `entity_type`: string (query parameter, optional) - Filter by entity type (wallet, contract, transaction)
  - `alert_type`: string (query parameter, optional) - Filter by alert type
  - `limit`: integer (query parameter, default: 50) - Maximum number of alerts to return
- **Response**:
  ```json
  {
    "items": [
      {
        "id": "alert123456",
        "timestamp": "2023-03-01T08:15:30Z",
        "severity": "high",
        "type": "suspicious_transaction",
        "entity": "0xabcdef1234567890abcdef1234567890abcdef1234",
        "entity_type": "transaction",
        "description": "Large transfer to a newly created wallet",
        "status": "new"
      },
      {
        "id": "alert123457",
        "timestamp": "2023-03-01T09:22:15Z",
        "severity": "critical",
        "type": "reentrancy",
        "entity": "0x5432109876abcdef5432109876abcdef54321098",
        "entity_type": "contract",
        "description": "Potential reentrancy vulnerability detected",
        "status": "acknowledged"
      }
    ],
    "count": 2
  }
  ```
- **Error Codes**:
  - `500`: Server error

### Network Graph Endpoints

#### Get Blockchain Network
- **Endpoint**: `GET /blockchain/network`
- **Description**: Get blockchain network visualization data with optional filters
- **Query Parameters**:
  - `node_type`: string (optional) - Filter by node type (wallet, contract)
  - `time_range`: string (optional) - Time range filter (24h, 7d, 30d, all)
- **Response**:
  ```json
  {
    "nodes": [
      {
        "id": "0x1234567890abcdef1234567890abcdef12345678",
        "type": "wallet",
        "subtype": "EOA",
        "risk_score": 35.5,
        "chain": "ethereum",
        "properties": {}
      },
      {
        "id": "0xabcdef1234567890abcdef1234567890abcdef1234",
        "type": "contract",
        "subtype": "token",
        "risk_score": 25.8,
        "chain": "ethereum",
        "properties": {}
      }
    ],
    "edges": [
      {
        "source": "0x1234567890abcdef1234567890abcdef12345678",
        "target": "0xabcdef1234567890abcdef1234567890abcdef1234",
        "type": "transaction",
        "tx_hash": "0xfedcba0987654321fedcba0987654321fedcba0987654321fedcba0987654321",
        "value": 1000000000000000000,
        "timestamp": "2023-03-01T09:22:15Z",
        "properties": {}
      }
    ]
  }
  ```
- **Error Codes**:
  - `500`: Server error

#### Query Blockchain Network
- **Endpoint**: `POST /blockchain/network/query`
- **Description**: Query blockchain network with complex filters
- **Request Body**:
  ```json
  {
    "node_type": "wallet",
    "relationship_type": "transaction",
    "start_time": "2023-01-01T00:00:00Z",
    "end_time": "2023-03-01T00:00:00Z",
    "addresses": ["0x1234567890abcdef1234567890abcdef12345678"],
    "min_value": 1000000000000000000,
    "chain": "ethereum",
    "include_properties": true
  }
  ```
- **Response**: Same as GET /blockchain/network
- **Error Codes**:
  - `422`: Invalid query parameters
  - `500`: Server error

### Natural Language Query Endpoints

#### Query Blockchain Data
- **Endpoint**: `POST /blockchain/query/natural`
- **Description**: Query blockchain data using natural language
- **Request Body**:
  ```json
  {
    "query": "Find all high-value transactions from this wallet in the last week"
  }
  ```
- **Response**:
  ```json
  {
    "result": {
      "transactions": [
        {
          "hash": "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
          "chain": "ethereum",
          "block_number": 16459873,
          "timestamp": "2023-02-28T14:22:10Z",
          "from_address": "0x1234567890abcdef1234567890abcdef12345678",
          "to_address": "0xabcdef1234567890abcdef1234567890abcdef1234",
          "value": 500000000000000000,
          "status": "success"
        }
      ],
      "count": 1,
      "total_value": 500000000000000000
    },
    "query_metadata": {
      "translated_query": "SELECT * FROM transactions WHERE from_address = '0x1234567890abcdef1234567890abcdef12345678' AND timestamp > '2023-02-21' AND value > 100000000000000000 ORDER BY timestamp DESC",
      "execution_time_ms": 325
    }
  }
  ```
- **Error Codes**:
  - `422`: Invalid query
  - `500`: Server error

#### Trace Transaction Flow
- **Endpoint**: `POST /blockchain/query/trace`
- **Description**: Trace transaction flow through multiple entities
- **Request Body**:
  ```json
  {
    "start_address": "0x1234567890abcdef1234567890abcdef12345678",
    "max_depth": 3,
    "min_value": 1000000000000000000,
    "start_time": "2023-01-01T00:00:00Z",
    "end_time": "2023-03-01T00:00:00Z"
  }
  ```
- **Response**:
  ```json
  {
    "paths": [
      {
        "path": [
          {
            "address": "0x1234567890abcdef1234567890abcdef12345678",
            "type": "wallet"
          },
          {
            "tx_hash": "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
            "value": 500000000000000000
          },
          {
            "address": "0xabcdef1234567890abcdef1234567890abcdef1234",
            "type": "contract"
          },
          {
            "tx_hash": "0x9876543210fedcba9876543210fedcba9876543210fedcba9876543210fedcba",
            "value": 450000000000000000
          },
          {
            "address": "0xfedcba0987654321fedcba0987654321fedcba09",
            "type": "wallet"
          }
        ],
        "total_value": 450000000000000000,
        "hop_count": 2
      }
    ],
    "total_paths": 1
  }
  ```
- **Error Codes**:
  - `422`: Invalid parameters
  - `500`: Server error

### Data Generation Endpoints

#### Generate Blockchain Data
- **Endpoint**: `POST /generate/data`
- **Description**: Generate synthetic blockchain data
- **Request Body**:
  ```json
  {
    "numWallets": 10,
    "numContracts": 3,
    "numTransactions": 50,
    "startBalance": 5000000000000000000,
    "chain": "ethereum"
  }
  ```
- **Response**:
  ```json
  {
    "status": "success",
    "data": {
      "wallets": [
        {
          "address": "0x1234567890abcdef1234567890abcdef12345678",
          "chain": "ethereum",
          "wallet_type": "EOA",
          "balance": 4500000000000000000
        }
      ],
      "contracts": [
        {
          "address": "0xabcdef1234567890abcdef1234567890abcdef1234",
          "chain": "ethereum",
          "contract_type": "token",
          "creator": "0x1234567890abcdef1234567890abcdef12345678"
        }
      ],
      "transactions": [
        {
          "hash": "0xfedcba0987654321fedcba0987654321fedcba0987654321fedcba0987654321",
          "from_address": "0x1234567890abcdef1234567890abcdef12345678",
          "to_address": "0xabcdef1234567890abcdef1234567890abcdef1234",
          "value": 500000000000000000,
          "chain": "ethereum"
        }
      ]
    }
  }
  ```
- **Error Codes**:
  - `422`: Invalid parameters
  - `500`: Server error

#### Generate Blockchain Scenario
- **Endpoint**: `POST /generate/scenario`
- **Description**: Generate blockchain scenario-based data
- **Request Body**:
  ```json
  {
    "scenario": "dex",
    "numWallets": 15,
    "numTransactions": 100,
    "timespan": 604800,
    "chain": "ethereum",
    "params": {
      "tradePairs": ["ETH/USDC", "ETH/DAI"],
      "swapVolume": 100000000000000000000
    }
  }
  ```
- **Response**:
  ```json
  {
    "status": "success",
    "scenario": "dex",
    "data": {
      "contracts": [
        {
          "address": "0xabcdef1234567890abcdef1234567890abcdef1234",
          "name": "DEXRouter",
          "contract_type": "dex",
          "chain": "ethereum"
        },
        {
          "address": "0x9876543210abcdef9876543210abcdef98765432",
          "name": "USDC",
          "contract_type": "token",
          "chain": "ethereum"
        }
      ],
      "wallets": [
        {
          "address": "0x1234567890abcdef1234567890abcdef12345678",
          "wallet_type": "trader",
          "chain": "ethereum"
        }
      ],
      "transactions": [
        {
          "hash": "0xfedcba0987654321fedcba0987654321fedcba0987654321fedcba0987654321",
          "type": "swap",
          "from_token": "ETH",
          "to_token": "USDC",
          "value": 2000000000000000000,
          "from_address": "0x1234567890abcdef1234567890abcdef12345678",
          "to_address": "0xabcdef1234567890abcdef1234567890abcdef1234",
          "chain": "ethereum"
        }
      ],
      "events": [
        {
          "name": "Swap",
          "contract": "0xabcdef1234567890abcdef1234567890abcdef1234",
          "tx_hash": "0xfedcba0987654321fedcba0987654321fedcba0987654321fedcba0987654321",
          "params": {
            "sender": "0x1234567890abcdef1234567890abcdef12345678",
            "amount0In": 2000000000000000000,
            "amount1Out": 4000000000
          }
        }
      ]
    }
  }
  ```
- **Error Codes**:
  - `422`: Invalid parameters
  - `500`: Server error

### Database Operations

#### Clear Database
- **Endpoint**: `DELETE /admin/database/clear`
- **Description**: Clear all data from the database
- **Response**:
  ```json
  {
    "success": true,
    "message": "Database cleared successfully",
    "details": {
      "blockchain_nodes_deleted": 156,
      "blockchain_edges_deleted": 238,
      "collections_affected": ["wallets", "transactions", "contracts", "events", "alerts"]
    }
  }
  ```
- **Error Codes**:
  - `500`: Server error

## Models

### Wallet
```json
{
  "address": "string (hex address)",
  "chain": "string (blockchain identifier)",
  "balance": "integer (wei/atom amount)",
  "wallet_type": "string (EOA, contract, multisig)",
  "first_seen": "string (ISO datetime)",
  "last_active": "string (ISO datetime)",
  "risk_score": "float (0-100)",
  "tags": ["string (tags/categories)"],
  "metadata": "object (optional additional data)"
}
```

### Transaction
```json
{
  "hash": "string (transaction hash)",
  "chain": "string (blockchain identifier)",
  "block_number": "integer",
  "timestamp": "string (ISO datetime)",
  "from_address": "string (sender address)",
  "to_address": "string (recipient address)",
  "value": "integer (wei/atom amount)",
  "status": "string (success, failed)",
  "gas_used": "integer",
  "gas_price": "integer",
  "input_data": "string (hex encoded)",
  "risk_score": "float (0-100)"
}
```

### Contract
```json
{
  "address": "string (contract address)",
  "chain": "string (blockchain identifier)",
  "creator": "string (creator address)",
  "creation_tx": "string (creation transaction hash)",
  "creation_timestamp": "string (ISO datetime)",
  "verified": "boolean",
  "name": "string (contract name)",
  "contract_type": "string (token, dex, lending, etc.)",
  "bytecode": "string (optional, hex encoded)",
  "abi": "array (optional, contract ABI)",
  "source_code": "string (optional, source code)",
  "risk_score": "float (0-100)",
  "vulnerabilities": [
    {
      "type": "string (vulnerability type)",
      "severity": "string (low, medium, high, critical)",
      "description": "string"
    }
  ]
}
```

### Event
```json
{
  "contract_address": "string (contract address)",
  "tx_hash": "string (transaction hash)",
  "block_number": "integer",
  "log_index": "integer",
  "timestamp": "string (ISO datetime)",
  "name": "string (event name)",
  "signature": "string (event signature)",
  "params": "object (event parameters)"
}
```

### Alert
```json
{
  "id": "string (UUID)",
  "timestamp": "string (ISO datetime)",
  "severity": "string (low, medium, high, critical)",
  "type": "string (alert type)",
  "entity": "string (address, tx hash)",
  "entity_type": "string (wallet, contract, transaction)",
  "description": "string (alert description)",
  "status": "string (new, acknowledged, resolved)"
}
```

### BlockchainNetworkQuery
```json
{
  "node_type": "string (wallet, contract)",
  "relationship_type": "string (transaction, interaction)",
  "start_time": "string (ISO datetime)",
  "end_time": "string (ISO datetime)",
  "addresses": ["string (blockchain address)"],
  "min_value": "integer (wei/atom amount)",
  "chain": "string (blockchain identifier)",
  "include_properties": "boolean"
}
```

### NaturalLanguageQuery
```json
{
  "query": "string (natural language query)"
}
```

### TransactionTrace
```json
{
  "start_address": "string (blockchain address)",
  "max_depth": "integer",
  "min_value": "integer (wei/atom amount)",
  "start_time": "string (ISO datetime)",
  "end_time": "string (ISO datetime)"
}
```

### BlockchainScenarioParams
```json
{
  "scenario": "string (dex, lending, nft, token_transfer)",
  "numWallets": "integer",
  "numTransactions": "integer",
  "timespan": "integer (seconds)",
  "chain": "string (blockchain identifier)",
  "params": "object (scenario-specific parameters)"
}
```