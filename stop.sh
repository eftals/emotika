#!/bin/bash

# Stop script for Emotika on Linux/macOS
# This script stops all Docker containers and services

echo -e "\033[36mStopping Emotika application...\033[0m"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "\033[31mDocker is not running. Please start Docker and try again.\033[0m"
    exit 1
fi

# Stop Docker containers
echo -e "\033[36mStopping Docker containers...\033[0m"
docker-compose down

# Check if containers were stopped successfully
if [ $? -eq 0 ]; then
    echo -e "\033[32mEmotika application stopped successfully.\033[0m"
else
    echo -e "\033[33mFailed to stop some containers. Attempting to force stop...\033[0m"
    
    # Try to stop containers forcefully
    docker-compose down --remove-orphans
    
    if [ $? -eq 0 ]; then
        echo -e "\033[32mEmotika application stopped successfully after force stop.\033[0m"
    else
        echo -e "\033[31mFailed to stop Emotika application. Please check Docker status.\033[0m"
        exit 1
    fi
fi

# Clean up any remaining processes if needed
echo -e "\033[36mCleaning up...\033[0m"
pkill -f "node" || true

echo -e "\033[32mCleanup complete.\033[0m" 