using System.Text.Json.Serialization;

namespace Emotika.Api.Models;

public class Session
{
    [JsonPropertyName("token")]
    public string Token { get; set; } = string.Empty;

    [JsonPropertyName("lastActivity")]
    public DateTime LastActivity { get; set; }

    [JsonPropertyName("userId")]
    public string? UserId { get; set; }

    [JsonPropertyName("metadata")]
    public Dictionary<string, object> Metadata { get; set; } = new();
} 