# Stop script for Emotika on Windows
# This script stops all Docker containers and services

Write-Host "Stopping Emotika application..." -ForegroundColor Cyan

# Check if Docker is running
try {
    $dockerInfo = docker info 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Docker is not running. Please start Docker and try again." -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "Docker is not installed or not in PATH. Please install Docker and try again." -ForegroundColor Red
    exit 1
}

# Stop Docker containers
Write-Host "Stopping Docker containers..." -ForegroundColor Cyan
docker-compose down

# Check if containers were stopped successfully
if ($LASTEXITCODE -eq 0) {
    Write-Host "Emotika application stopped successfully." -ForegroundColor Green
} else {
    Write-Host "Failed to stop some containers. Attempting to force stop..." -ForegroundColor Yellow
    
    # Try to stop containers forcefully
    docker-compose down --remove-orphans
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Emotika application stopped successfully after force stop." -ForegroundColor Green
    } else {
        Write-Host "Failed to stop Emotika application. Please check Docker status." -ForegroundColor Red
        exit 1
    }
}

# Clean up any remaining processes if needed
Write-Host "Cleaning up..." -ForegroundColor Cyan
Get-Process -Name "node" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

Write-Host "Cleanup complete." -ForegroundColor Green 