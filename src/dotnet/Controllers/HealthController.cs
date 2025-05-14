using Microsoft.AspNetCore.Mvc;
using StackExchange.Redis;

namespace Emotika.Api.Controllers;

[ApiController]
[Route("[controller]")]
public class HealthController : ControllerBase
{
    private readonly IConnectionMultiplexer _redis;

    public HealthController(IConnectionMultiplexer redis)
    {
        _redis = redis;
    }

    [HttpGet]
    public IActionResult Get()
    {
        try
        {
            var db = _redis.GetDatabase();
            db.Ping();
            return Ok(new { status = "healthy", redis = "connected" });
        }
        catch (RedisConnectionException)
        {
            return StatusCode(503, new { status = "unhealthy", redis = "disconnected" });
        }
    }
} 