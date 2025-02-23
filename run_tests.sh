#!/bin/bash

# Clean up any existing test containers
docker-compose -f docker-compose.test.yml down -v

# Build and run tests
docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit --exit-code-from test

# Clean up after tests
docker-compose -f docker-compose.test.yml down -v
