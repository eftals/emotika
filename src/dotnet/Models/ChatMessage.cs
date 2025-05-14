using System.Text.Json.Serialization;

namespace Emotika.Api.Models;

public class ChatMessage
{
    [JsonPropertyName("id")]
    public string Id { get; set; } = string.Empty;

    [JsonPropertyName("userMessage")]
    public string UserMessage { get; set; } = string.Empty;

    [JsonPropertyName("timestamp")]
    public DateTime Timestamp { get; set; }

    [JsonPropertyName("response")]
    public string? Response { get; set; }
} 