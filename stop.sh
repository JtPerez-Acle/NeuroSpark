#!/bin/bash

# Agent Interaction Backend - Stop Script
# This script stops the running backend services

set -e

BOLD="\033[1m"
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
NC="\033[0m" # No Color

echo -e "${BOLD}Stopping Agent Interaction Backend${NC}"

# Check if services are running with the full configuration
if docker-compose ps | grep -q "Up"; then
    echo "Stopping services using full configuration..."
    docker-compose down
    echo -e "${GREEN}Services stopped successfully!${NC}"
# Check if services are running with the simple configuration
elif docker-compose -f docker-compose.simple.yml ps | grep -q "Up"; then
    echo "Stopping services using development configuration..."
    docker-compose -f docker-compose.simple.yml down
    echo -e "${GREEN}Development services stopped successfully!${NC}"
else
    echo -e "${YELLOW}No services appear to be running.${NC}"
fi

echo -e "\n${YELLOW}Note:${NC} This command does not remove volumes. If you want to remove all data, use:"
echo "  docker-compose down -v           # For full environment"
echo "  docker-compose -f docker-compose.simple.yml down -v  # For development environment"