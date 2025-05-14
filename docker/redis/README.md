# Redis Development Setup

This directory contains the Redis configuration for the development environment.

## Configuration

The `redis.conf` file contains a simplified Redis configuration suitable for development:

- No password protection
- Data persistence enabled
- Memory limit set to 256MB
- LRU eviction policy

## Usage

Redis is automatically started as part of the Docker Compose setup. It's accessible to all services in the Docker network at `redis:6379`.

## Connecting to Redis

### From Python Backend

```python
import redis

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True
)
```

### From .NET Backend

```csharp
var redis = ConnectionMultiplexer.Connect("redis:6379");
var db = redis.GetDatabase();
```

### From Frontend

The frontend doesn't connect directly to Redis. It communicates with the backend services, which then interact with Redis.

## Data Persistence

Redis data is persisted in a Docker volume named `redis-data`. This ensures that your data is preserved between container restarts. 