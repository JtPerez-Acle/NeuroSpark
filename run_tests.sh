#!/bin/bash

# Set Neo4j environment variables
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="testpassword"

# Run tests with coverage
pytest --cov=app --cov-report=html --cov-report=term-missing:skip-covered
