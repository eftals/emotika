using Microsoft.AspNetCore.Mvc;
using StackExchange.Redis;
using System.Text.Json;
using Emotika.Api.Models;

namespace Emotika.Api.Controllers;

[ApiController]
[Route("[controller]")]
public class ChatController : ControllerBase
{
    private readonly IConnectionMultiplexer _redis;
    private const string CHAT_KEY_PREFIX = "chat:";

    public ChatController(IConnectionMultiplexer redis)
    {
        _redis = redis;
    }

    [HttpPost]
    public async Task<ActionResult<ChatMessage>> SendMessage([FromBody] string message)
    {
        var db = _redis.GetDatabase();
        
        // Create a new chat message
        var chatMessage = new ChatMessage
        {
            UserMessage = message
        };

        // Store in Redis
        await db.StringSetAsync(
            $"{CHAT_KEY_PREFIX}{chatMessage.Id}",
            JsonSerializer.Serialize(chatMessage)
        );

        // TODO: In the future, we'll add AI processing here
        chatMessage.Response = "Message received and stored with ID: " + chatMessage.Id;

        return Ok(chatMessage);
    }

    [HttpGet("{id}")]
    public async Task<ActionResult<ChatMessage>> GetMessage(string id)
    {
        var db = _redis.GetDatabase();
        var message = await db.StringGetAsync($"{CHAT_KEY_PREFIX}{id}");

        if (!message.HasValue)
            return NotFound();

        return Ok(JsonSerializer.Deserialize<ChatMessage>(message!));
    }
} 