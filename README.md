# Emotika

A multi-tiered application demonstrating the integration of Python, React, Redis, and ASP.NET REST services.

## Project Structure

```
emotika/
├── src/
│   ├── frontend/           # React frontend application
│   ├── python/             # Python backend service
│   └── dotnet/             # ASP.NET backend service
├── docker/
│   └── redis/              # Redis configuration
├── docker-compose.yml      # Docker composition file
├── package.json            # NPM package configuration
├── start.ps1               # Windows startup script
├── stop.ps1                # Windows stop script
├── start.sh                # Linux startup script
└── stop.sh                 # Linux stop script
```

## Prerequisites

- Docker Desktop
- Node.js and npm
- Python 3.x
- .NET SDK
- PowerShell 5.0 or later (Windows)
- Bash shell (Linux/macOS)

## Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/emotika.git
   cd emotika
   ```

2. Install dependencies and build the project:
   ```bash
   npm run setup
   ```

3. Start the application:

   **Windows:**
   ```bash
   npm run dev
   # or
   ./start.ps1
   ```

   **Linux/macOS:**
   ```bash
   npm run dev
   # or
   chmod +x start.sh
   ./start.sh
   ```

## Available Scripts

- `npm run setup` - Install dependencies and build the project
- `npm run build` - Build all components
- `npm run build:frontend` - Build the React frontend
- `npm run build:python` - Build the Python backend
- `npm run build:dotnet` - Build the .NET backend
- `npm run dev` - Build and start the application
- `npm run start` - Start the application
- `npm run start:build` - Start with rebuild
- `npm run stop` - Stop the application
- `npm run stop:volumes` - Stop and remove volumes

## Docker Commands

- `npm run logs` - View all container logs
- `npm run logs:frontend` - View frontend logs
- `npm run logs:python` - View Python backend logs
- `npm run logs:dotnet` - View .NET backend logs
- `npm run logs:redis` - View Redis logs
- `npm run restart:frontend` - Restart frontend container
- `npm run restart:python` - Restart Python backend container
- `npm run restart:dotnet` - Restart .NET backend container
- `npm run restart:redis` - Restart Redis container

## Development

The application uses Docker Compose for containerization. Each service runs in its own container:

- Frontend: React application
- Python Backend: Python REST service
- .NET Backend: ASP.NET REST service
- Redis: In-memory data store

## Linux/macOS Support

The project now includes shell scripts for Linux and macOS users:

- `start.sh` - Start the application (equivalent to start.ps1)
- `stop.sh` - Stop the application (equivalent to stop.ps1)

Make the scripts executable before running:
```bash
chmod +x start.sh stop.sh
```

## License

MIT 
