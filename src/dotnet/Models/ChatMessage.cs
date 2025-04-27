namespace Emotika.Api.Models;

public enum MessageStatus
{
    Pending,
    Processing,
    Completed,
    Failed
}

public class ChatMessage
{
    public string Id { get; set; } = Guid.NewGuid().ToString();
    public string UserMessage { get; set; } = string.Empty;
    public DateTime Timestamp { get; set; } = DateTime.UtcNow;
    public string? Response { get; set; }
    public MessageStatus Status { get; set; } = MessageStatus.Pending;
    public string? ErrorMessage { get; set; }
} 