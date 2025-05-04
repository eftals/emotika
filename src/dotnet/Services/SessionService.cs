using System.Text.Json;
using StackExchange.Redis;
using Emotika.Api.Models;

namespace Emotika.Api.Services;

public interface ISessionService
{
    Task<Session?> GetSessionAsync(string token);
    Task<Session> CreateSessionAsync(string? userId = null, Dictionary<string, object>? metadata = null);
    Task<Session?> UpdateSessionAsync(string token, Dictionary<string, object>? metadata = null);
    Task<bool> DeleteSessionAsync(string token);
    Task<bool> IsValidSessionAsync(string token);
}

public class SessionService : ISessionService
{
    private readonly IConnectionMultiplexer _redis;
    private readonly TimeSpan _sessionExpiry = TimeSpan.FromMinutes(30);
    private const string SessionPrefix = "session:";

    public SessionService(IConnectionMultiplexer redis)
    {
        _redis = redis;
    }

    private string GetSessionKey(string token) => $"{SessionPrefix}{token}";

    public async Task<Session?> GetSessionAsync(string token)
    {
        var db = _redis.GetDatabase();
        var sessionKey = GetSessionKey(token);
        var sessionData = await db.StringGetAsync(sessionKey);

        if (sessionData.IsNull)
            return null;

        try
        {
            var session = JsonSerializer.Deserialize<Session>(sessionData!);
            if (session != null)
            {
                // Refresh the session expiry
                await db.KeyExpireAsync(sessionKey, _sessionExpiry);
            }
            return session;
        }
        catch (JsonException)
        {
            return null;
        }
    }

    public async Task<Session> CreateSessionAsync(string? userId = null, Dictionary<string, object>? metadata = null)
    {
        var session = new Session
        {
            Token = Guid.NewGuid().ToString(),
            LastActivity = DateTime.UtcNow,
            UserId = userId,
            Metadata = metadata ?? new Dictionary<string, object>()
        };

        var db = _redis.GetDatabase();
        var sessionKey = GetSessionKey(session.Token);
        var sessionJson = JsonSerializer.Serialize(session);

        await db.StringSetAsync(sessionKey, sessionJson, _sessionExpiry);
        return session;
    }

    public async Task<Session?> UpdateSessionAsync(string token, Dictionary<string, object>? metadata = null)
    {
        var session = await GetSessionAsync(token);
        if (session == null)
            return null;

        session.LastActivity = DateTime.UtcNow;
        if (metadata != null)
        {
            foreach (var (key, value) in metadata)
            {
                session.Metadata[key] = value;
            }
        }

        var db = _redis.GetDatabase();
        var sessionKey = GetSessionKey(token);
        var sessionJson = JsonSerializer.Serialize(session);

        await db.StringSetAsync(sessionKey, sessionJson, _sessionExpiry);
        return session;
    }

    public async Task<bool> DeleteSessionAsync(string token)
    {
        var db = _redis.GetDatabase();
        var sessionKey = GetSessionKey(token);
        return await db.KeyDeleteAsync(sessionKey);
    }

    public async Task<bool> IsValidSessionAsync(string token)
    {
        var session = await GetSessionAsync(token);
        return session != null;
    }
} 