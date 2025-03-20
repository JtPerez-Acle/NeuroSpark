#!/bin/bash

# Agent Interaction Backend - Development Start Script
# This script starts the backend services for development with minimal components

set -e

BOLD="\033[1m"
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
NC="\033[0m" # No Color

echo -e "${BOLD}Starting Agent Interaction Backend (Development Mode)${NC}"

# Check if docker and docker-compose are installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check for docker compose command
if ! docker compose version &> /dev/null; then
    echo -e "${RED}Docker Compose is not installed or not in PATH. Please install Docker Compose first.${NC}"
    exit 1
fi

# Create log directory if it doesn't exist
mkdir -p ./logs

# Start the services using the simple configuration
echo -e "\n${BOLD}Starting services in development mode...${NC}"
docker compose -f docker-compose.simple.yml up -d

# Wait for ArangoDB to be healthy
echo -e "\n${BOLD}Waiting for ArangoDB to be ready...${NC}"
attempts=0
max_attempts=30

until [ $attempts -ge $max_attempts ]; do
    if docker compose -f docker-compose.simple.yml ps | grep "arangodb" | grep -q "Up"; then
        # Check if healthcheck is passing
        if docker compose -f docker-compose.simple.yml ps | grep "arangodb" | grep -q "(healthy)"; then
            echo -e "${GREEN}ArangoDB is ready!${NC}"
            break
        fi
    fi
    
    echo "Waiting for ArangoDB to be healthy... (attempt $((attempts+1))/$max_attempts)"
    attempts=$((attempts+1))
    sleep 3
done

if [ $attempts -ge $max_attempts ]; then
    echo -e "${YELLOW}ArangoDB may not be fully initialized yet. Check status with 'docker-compose -f docker-compose.simple.yml ps'${NC}"
fi

# Display URLs and helpful information
echo -e "\n${GREEN}${BOLD}Development Services Started!${NC}"
echo -e "Development environment is now running with minimal components."
echo -e "API available at: ${BOLD}http://localhost:8000${NC}"
echo -e "API Documentation: ${BOLD}http://localhost:8000/docs${NC}"
echo -e "ArangoDB UI available at: ${BOLD}http://localhost:8529${NC} (user: root, password: password)"

echo -e "\n${YELLOW}${BOLD}Note:${NC} This is a simplified development setup without monitoring services."
echo -e "For a full deployment with Prometheus, Grafana, etc., use ${BOLD}./start.sh${NC} instead."

echo -e "\n${BOLD}Useful Development Commands:${NC}"
echo "  docker compose -f docker-compose.simple.yml ps               - View running services"
echo "  docker compose -f docker-compose.simple.yml logs -f app      - Follow app logs"
echo "  docker compose -f docker-compose.simple.yml logs -f arangodb - Follow database logs"
echo "  docker compose -f docker-compose.simple.yml restart app      - Restart the API"
echo "  docker compose -f docker-compose.simple.yml down             - Stop services"
echo "  docker compose -f docker-compose.simple.yml down -v          - Stop services and remove volumes"
echo "  docker compose -f docker-compose.simple.yml exec app /bin/bash - Access app container shell"