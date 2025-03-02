# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.9.0] - 2025-03-01

### Added
- Web3 Integration - Phase 1: Blockchain Data Foundation
  - Ethereum blockchain connector for data ingestion with Web3.py integration
  - Complete blockchain entity data models (wallets, transactions, smart contracts, events)
  - Robust transaction ingestion pipeline with comprehensive filtering capabilities
  - Enhanced ArangoDB schema optimized for blockchain entity relationships
  - Graph relationship modeling for blockchain transactions and contract interactions
  - Multi-chain architecture with support for additional blockchain networks

- Risk Scoring & Security Analysis
  - Multi-factor risk scoring algorithms for wallets, transactions, and contracts
  - Behavioral pattern analysis for suspicious activity detection
  - Risk score normalization on a standardized 0-100 scale
  - Anomaly detection for unusual wallet and transaction patterns
  - Smart contract risk assessment with vulnerability categorization and tracking
  - Real-time alerts system for high-risk entities and activities
  - Advanced database operations for performance-optimized risk-based queries

- Network Analysis for Blockchain Data
  - Transaction flow analysis to identify value transfer patterns
  - Advanced community detection to discover related entity clusters
  - Centrality metrics to identify influential wallets and contracts
  - Temporal analysis for tracking entity behavior changes over time
  - Pattern recognition for common cryptocurrency scams and fraud
  - Visualization enhancements for complex blockchain relationships

- LLM-based Blockchain Query System
  - Ollama integration for efficient local LLM deployment
  - Specialized natural language to blockchain query translation
  - Custom prompt engineering for blockchain-specific data retrieval
  - Context-aware response formatting for blockchain data presentation
  - Query template system for common blockchain analysis patterns

- New API Endpoints
  - `/blockchain/transactions` - Comprehensive transaction retrieval and analysis
  - `/blockchain/wallets` - In-depth wallet activity and relationship analysis
  - `/blockchain/contracts` - Smart contract inspection and security analysis
  - `/blockchain/events` - Smart contract event monitoring and analysis
  - `/blockchain/risk` - Multi-factor risk assessment and alert management
  - `/blockchain/query/natural` - Natural language interface for blockchain data
  - `/blockchain/network` - Enhanced graph visualization for blockchain relationships

### Changed
- Complete migration from agent-based system to blockchain intelligence platform
- Enhanced graph data models to natively support blockchain entity relationships
- Upgraded NetworkX integration with specialized blockchain analysis algorithms
- Improved WebSocket handler for real-time blockchain event monitoring
- Updated Docker configuration with optimized Ollama LLM integration
- Refactored database operations for better performance with blockchain data
- Enhanced security with comprehensive validation and sanitization
- Extended synthetic data generation for realistic blockchain scenarios
- Optimized query performance for large blockchain dataset handling

### Removed
- Legacy agent-specific data models and database operations
- KQML message handling system (completely replaced with blockchain entities)
- Agent-focused scenario data generation (replaced with blockchain scenarios)
- Agent interaction tracking system (replaced with transaction tracking)
- Compatibility endpoints for legacy agent-based functionality

## [0.8.2] - 2025-03-01

### Added
- Advanced network analysis capabilities with NetworkX integration:
  - Graph metrics calculation (density, diameter, clustering, etc.)
  - Node centrality measures (degree, betweenness, closeness, eigenvector, PageRank)
  - Community detection algorithms (Louvain, Label Propagation, Girvan-Newman)
  - Temporal network analysis for evolution tracking
  - Custom force-directed layouts for visualizations (spring, spectral, circular, etc.)
- New `/analysis` endpoints for network analysis functionality:
  - `/analysis/metrics` for basic graph metrics
  - `/analysis/centrality` for node centrality measures
  - `/analysis/communities` for community detection
  - `/analysis/layout` for graph layout coordinates
  - `/analysis/temporal` for temporal analysis
  - `/analysis/visualization` for enhanced visualization data
- Comprehensive error handling with graceful fallbacks for graph algorithms

## [0.8.1] - 2025-03-01

### Fixed
- Fixed scenario generation endpoint that was returning 404 errors
- Added debug logging for scenario generation process
- Fixed CORS issues with API proxy configuration
- Improved stability of Docker deployment for development environment

## [0.8.0] - 2025-03-01

### Added
- Scenario-based synthetic data generation with four distinct simulation scenarios:
  - Prisoners' Dilemma (pd) for studying cooperation dynamics
  - Predator/Prey (predator_prey) for analyzing information propagation
  - Pursuer/Evader (pursuer_evader) for modeling crime dynamics
  - Search and Rescue (search_rescue) for knowledge transfer simulation
- New `/generate/scenario` endpoint for creating scenario-specific data
- Modular architecture for scenario generators with a common interface
- Comprehensive test suite for all scenario generators
- Updated API documentation with scenario generation examples

### Changed
- Enhanced `DataGenerator` class to support scenario-based generation
- Improved test infrastructure for new scenario generators
- Updated documentation to include scenario-based data generation

## [0.7.1] - 2025-02-27

### Added
- Comprehensive Docker deployment scripts for different environments:
  - `start.sh` for production deployment with full monitoring
  - `start_dev.sh` for lightweight development setup
  - `stop.sh` for graceful shutdown of all services
- Enhanced test infrastructure with full test suite covering all 57 tests
- Improved database connection handling with better retry logic
- Additional documentation and usage examples

### Changed
- Improved ArangoDB health check mechanism for better reliability
- Enhanced test fixtures with proper isolation and teardown
- Updated README with latest features and deployment options
- Updated Docker Compose files for better service coordination

### Fixed
- Fixed ArangoDB health check issues in Docker containers
- Fixed connection retry handling in database layer
- Fixed test reliability issues with better synchronization
- Fixed Docker testing environment for consistent results

## [0.7.0] - 2025-02-27

### Added
- ArangoDB optimized queries for network visualization
- Simplified Docker deployment with working docker-compose.yml
- New testing utilities with simple_test.py and complex_test.py

### Changed
- Streamlined root directory by removing obsolete Neo4j files
- Updated README to focus on ArangoDB integration
- Made Docker setup more robust with proper startup and shutdown

### Fixed
- Fixed key handling in ArangoDB integrations
- Fixed Docker-based test environment issues
- Fixed interaction_id and run_id handling in database and API

## [0.6.0] - 2025-02-27

### Changed
- Completed migration from Neo4j to ArangoDB
- Removed all Neo4j dependencies and imports
- Updated test infrastructure to use ArangoDB
- Updated docker-compose.test.yml for ArangoDB tests

### Fixed
- Fixed remaining Neo4j dependencies in test suite
- Updated database cleanup process in test fixtures

## [0.5.0] - 2025-02-26

### Added
- Migrated from Neo4j to ArangoDB for better reliability and simplicity
- Added new ArangoDB implementation with full feature parity
- Implemented `clear_database` method for easier database management
- Created new setup script for automated environment configuration
- Added comprehensive ArangoDB database tests

### Changed
- Updated environment variable configuration for ArangoDB
- Enhanced database interface for better abstraction
- Improved error handling and connection reliability
- Updated documentation with ArangoDB schema details
- Simplified password and authentication management

### Fixed
- Resolved database authentication issues
- Fixed inconsistent database state after restarts
- Improved database connection handling
- Enhanced error recovery for database operations

## [0.4.0] - 2025-02-26

### Added
- New `/interactions` endpoints for dedicated interaction management
- New `/generate` endpoints for synthetic data generation
- Individual interaction retrieval by ID
- Improved API documentation with updated examples
- Enhanced test coverage for new endpoints

### Changed
- Reorganized API structure for better resource isolation
- Deprecated old endpoints with warnings while maintaining backward compatibility
- Consolidated test suite with dedicated tests for new endpoints
- Updated database operations to support the new API structure

### Fixed
- Database connection handling in tests
- Interaction ID handling consistency
- API response structure for better client compatibility

## [0.3.0] - 2025-02-24

### Added
- New `AgentInteraction` model with improved fields:
  - Added topic categorization
  - Added priority levels (1-5)
  - Added sentiment tracking (-1 to 1)
  - Added duration tracking for performance monitoring
  - Added extensible metadata field
- Test suite for new interaction handling
- Improved synthetic data generation with realistic agent interactions

### Changed
- Replaced KQML message format with simpler, more focused agent interaction model
- Renamed project from "KQML Parser" to "Agent Interaction Backend"
- Updated API endpoints from `/agents/message` to `/agents/interaction`
- Refactored data generator to use new interaction format
- Improved documentation and API descriptions

### Removed
- Complex KQML parsing and validation logic
- Performative-based message structure
- KQML-specific ontology handling

## [0.2.3] - 2025-02-23

### Added
- Neo4j database integration with proper connection handling and error management
- New database abstraction layer with `base.py` interface
- Implemented `get_agent_runs` and `get_agent_interactions` methods in Neo4j
- Environment variables configuration for Neo4j connection
- `run_tests.sh` script for running tests with proper environment setup

### Changed
- Refactored database implementation into modular structure:
  - Split into `memory_db.py` and `neo4j_db.py`
  - Created abstract base class in `base.py`
  - Improved separation of concerns
- Updated test suite to handle both in-memory and Neo4j databases
- Enhanced error handling in database operations
- Improved test coverage and reporting
- Updated README with current project structure and features

### Fixed
- Neo4j connection and authentication issues
- Test failures related to database operations
- Environment variable handling in test suite
- Transaction handling in `store_run` with proper commit/rollback/close
- Metrics storage in Neo4j by converting complex objects to JSON strings

## [0.2.2] - 2025-02-21

### Added
- Comprehensive API documentation with Swagger UI
- Enhanced error handling and validation
- Synthetic data generation endpoints
- Query parameter validation and defaults
- Path parameter validation
- Async operation support across all endpoints

### Changed
- Improved FastAPI route definitions
- Enhanced input validation using Pydantic models
- Better error messages and status codes
- Updated README with comprehensive documentation
- Reorganized project structure for better maintainability

### Fixed
- Path parameter handling in FastAPI routes
- Query parameter validation
- Error handling in database operations
- Async operation issues
- Documentation inconsistencies

## [0.2.1] - 2025-02-20

### Added
- Neo4j database integration
- Basic KQML message processing
- Agent interaction tracking
- Initial test suite setup

### Changed
- Switched to FastAPI from Flask
- Improved project structure
- Enhanced documentation

## [0.2.0] - 2025-02-19

### Added
- Initial FastAPI implementation
- Basic endpoint structure
- Project documentation
- Development plan
- Basic test framework

## [0.1.0] - 2025-02-18

### Added
- Project initialization
- Basic project structure
- Initial documentation