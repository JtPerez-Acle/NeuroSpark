#!/bin/bash

# Agent Interaction Backend - Production Start Script
# This script starts the backend services for production use

set -e

BOLD="\033[1m"
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
NC="\033[0m" # No Color

echo -e "${BOLD}Starting Agent Interaction Backend${NC}"

# Check if docker and docker-compose are installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

# Create directories for ArangoDB data if they don't exist
mkdir -p ./arangodb/data
mkdir -p ./arangodb/apps
mkdir -p ./logs

# Start the services
echo -e "\n${BOLD}Starting services...${NC}"
docker-compose up -d

# Wait for ArangoDB to be healthy
echo -e "\n${BOLD}Waiting for ArangoDB to be ready...${NC}"
attempts=0
max_attempts=30

until [ $attempts -ge $max_attempts ]; do
    if docker-compose ps | grep "arangodb" | grep -q "Up"; then
        # Check if healthcheck is passing
        if docker-compose ps | grep "arangodb" | grep -q "(healthy)"; then
            echo -e "${GREEN}ArangoDB is ready!${NC}"
            break
        fi
    fi
    
    echo "Waiting for ArangoDB to be healthy... (attempt $((attempts+1))/$max_attempts)"
    attempts=$((attempts+1))
    sleep 3
done

if [ $attempts -ge $max_attempts ]; then
    echo -e "${YELLOW}ArangoDB may not be fully initialized yet. Check status with 'docker-compose ps'${NC}"
fi

# Display URLs and helpful information
echo -e "\n${GREEN}${BOLD}Services Started!${NC}"
echo -e "The Agent Interaction Backend is now running."
echo -e "API available at: ${BOLD}http://localhost:8000${NC}"
echo -e "API Documentation: ${BOLD}http://localhost:8000/docs${NC}"
echo -e "ArangoDB UI available at: ${BOLD}http://localhost:8529${NC} (user: root, password: password)"
echo -e "Grafana Dashboard available at: ${BOLD}http://localhost:3000${NC} (user: admin, password: admin)"

echo -e "\n${BOLD}Useful Commands:${NC}"
echo "  docker-compose ps                   - View running services"
echo "  docker-compose logs -f app          - Follow app logs"
echo "  docker-compose logs -f arangodb     - Follow database logs"
echo "  docker-compose restart app          - Restart the API"
echo "  docker-compose down                 - Stop services"
echo "  docker-compose down -v              - Stop services and remove volumes"