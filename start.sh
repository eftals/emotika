#!/bin/bash

# Emotika Start Script
echo -e "\033[0;32mStarting Emotika Application...\033[0m"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "\033[0;31mDocker is not running. Please start Docker and try again.\033[0m"
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo -e "\033[0;31mnpm is not installed or not in PATH. Please install Node.js and try again.\033[0m"
    exit 1
fi

# Display npm version
npm_version=$(npm --version)
echo -e "\033[0;36mUsing npm version $npm_version\033[0m"

# Build and start the application
echo -e "\033[0;36mBuilding and starting the application...\033[0m"
npm run dev 