#!/bin/bash

set -e

echo "==== Starting ArangoDB Testing Environment ===="

# Function to clean up containers
cleanup() {
  echo "==== Cleaning Up Containers ===="
  docker compose -f docker-compose.test.yml down -v
}

# Set up trap to ensure cleanup on exit
trap cleanup EXIT

# Clean up any existing test containers first
cleanup

# Build and run tests
# This uses the docker-compose.test.yml configuration which:
# 1. Starts an ArangoDB service (for database)
# 2. Uses a setup service that waits for ArangoDB to be fully ready
# 3. Runs the tests only after the setup service confirms ArangoDB is ready
# 4. Ensures proper communication between containers using a shared network
echo "==== Building and Running Tests ===="
docker compose -f docker-compose.test.yml up --build --abort-on-container-exit --exit-code-from test

echo "==== Tests Completed ===="
