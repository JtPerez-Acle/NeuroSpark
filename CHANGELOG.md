# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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