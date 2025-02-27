#!/bin/bash

# Agent Interaction Backend Setup Script
# This script helps set up the Agent Interaction Backend with ArangoDB

set -e

BOLD="\033[1m"
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
NC="\033[0m" # No Color

echo -e "${BOLD}Welcome to Agent Interaction Backend Setup${NC}"
echo "This script will help you configure the backend with ArangoDB"

# Check if docker and docker-compose are installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

echo -e "\n${BOLD}Database Configuration${NC}"

# Ask if user wants to customize ArangoDB password
read -p "Do you want to customize the ArangoDB database password? (y/n) [n]: " customize_password
customize_password=${customize_password:-n}

if [[ $customize_password == "y" || $customize_password == "Y" ]]; then
    read -p "Enter new ArangoDB password: " arango_password
    
    # Update password in docker-compose.yml
    sed -i "s/ARANGO_ROOT_PASSWORD=password/ARANGO_ROOT_PASSWORD=${arango_password}/" docker-compose.yml
    sed -i "s/ARANGO_PASSWORD=password/ARANGO_PASSWORD=${arango_password}/" docker-compose.yml
    
    echo -e "${GREEN}Password updated in docker-compose.yml${NC}"
else
    echo -e "${YELLOW}Using default password 'password'${NC}"
    arango_password="password"
fi

echo -e "\n${BOLD}Starting Services${NC}"

# If there are existing volumes, clean them up
echo "Cleaning up any existing volumes..."
docker-compose down -v &> /dev/null || true

# Create directories for ArangoDB data
mkdir -p ./arangodb/data
mkdir -p ./arangodb/apps

# Start the services
echo "Starting services with docker-compose..."
docker-compose up -d

# Wait for services to initialize
echo "Waiting for services to initialize..."
sleep 20

# Test connection to ArangoDB
echo "Testing connection to ArangoDB..."
max_attempts=10
attempt=1
connected=false

while [ $attempt -le $max_attempts ]; do
    echo "Connection attempt $attempt/$max_attempts..."
    
    # Use curl to check if ArangoDB is responding
    if curl -s -u root:${arango_password} http://localhost:8529/_api/version | grep -q "server"; then
        connected=true
        break
    fi
    
    attempt=$((attempt+1))
    sleep 5
done

if [ "$connected" = true ]; then
    echo -e "${GREEN}Successfully connected to ArangoDB!${NC}"
else
    echo -e "${RED}Failed to connect to ArangoDB after $max_attempts attempts.${NC}"
    echo "Please check the logs with 'docker-compose logs arangodb'"
fi

# Setup complete
echo -e "\n${GREEN}${BOLD}Setup Complete!${NC}"
echo -e "The Agent Interaction Backend is now running."
echo -e "API available at: ${BOLD}http://localhost:8000${NC}"
echo -e "API Documentation: ${BOLD}http://localhost:8000/docs${NC}"
echo -e "ArangoDB UI available at: ${BOLD}http://localhost:8529${NC} (user: root, password: ${arango_password})"
echo -e "Grafana Dashboard available at: ${BOLD}http://localhost:3000${NC} (user: admin, password: admin)"

echo -e "\n${BOLD}Useful Commands:${NC}"
echo "  docker-compose ps                   - View running services"
echo "  docker-compose logs -f app          - Follow app logs"
echo "  docker-compose logs -f arangodb     - Follow database logs"
echo "  docker-compose restart app          - Restart the API"
echo "  docker-compose down                 - Stop services"
echo "  docker-compose down -v              - Stop services and remove volumes"