# Emotika Start Script
Write-Host "Starting Emotika Application..." -ForegroundColor Green

# Check if Docker is running
try {
    $dockerStatus = docker info 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Docker is not running. Please start Docker Desktop and try again." -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "Docker is not installed or not in PATH. Please install Docker Desktop and try again." -ForegroundColor Red
    exit 1
}

# Check if npm is installed
try {
    $npmVersion = npm --version
    Write-Host "Using npm version $npmVersion" -ForegroundColor Cyan
} catch {
    Write-Host "npm is not installed or not in PATH. Please install Node.js and try again." -ForegroundColor Red
    exit 1
}

# Build and start the application
Write-Host "Building and starting the application..." -ForegroundColor Cyan
npm run dev 