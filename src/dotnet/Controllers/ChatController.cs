using Microsoft.AspNetCore.Mvc;
using StackExchange.Redis;
using System.Text.Json;
using Emotika.Api.Models;

namespace Emotika.Api.Controllers;

[ApiController]
[Route("[controller]")]
[Produces("application/json")]
public class ChatController : ControllerBase
{
    private readonly IConnectionMultiplexer _redis;
    private const string CHAT_KEY_PREFIX = "chat:";
    private const string INPUT_QUEUE = "emotika_incoming";
    private const string RESPONSE_QUEUE = "emotika_response";
    private const int RESPONSE_TIMEOUT_SECONDS = 60;

    public ChatController(IConnectionMultiplexer redis)
    {
        _redis = redis;
    }

    /// <summary>
    /// Sends a message to the chat system and waits for a response
    /// </summary>
    /// <remarks>
    /// Sample request:
    /// 
    ///     POST /chat
    ///     {
    ///         "id": "123e4567-e89b-12d3-a456-426614174000",
    ///         "userMessage": "Hello, how are you?",
    ///         "timestamp": "2024-01-01T12:00:00Z"
    ///     }
    /// </remarks>
    /// <param name="chatMessage">The chat message containing id, userMessage, and timestamp</param>
    /// <returns>The chat message with the response</returns>
    /// <response code="200">Returns the chat message with response</response>
    /// <response code="408">Request timed out waiting for response</response>
    [HttpPost]
    [ProducesResponseType(typeof(ChatMessage), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status408RequestTimeout)]
    public async Task<ActionResult<ChatMessage>> SendMessage([FromBody] ChatMessage chatMessage)
    {
        if (string.IsNullOrEmpty(chatMessage.Id))
        {
            return BadRequest(new { error = "Message ID is required" });
        }

        if (string.IsNullOrEmpty(chatMessage.UserMessage))
        {
            return BadRequest(new { error = "User message is required" });
        }

        var db = _redis.GetDatabase();
        
        // Store in Redis
        await db.StringSetAsync(
            $"{CHAT_KEY_PREFIX}{chatMessage.Id}",
            JsonSerializer.Serialize(chatMessage)
        );

        // Add to input queue
        await db.ListRightPushAsync(INPUT_QUEUE, JsonSerializer.Serialize(new
        {
            id = chatMessage.Id,
            userMessage = chatMessage.UserMessage,
            timestamp = chatMessage.Timestamp
        }));

        // Wait for response with timeout
        var startTime = DateTime.UtcNow;
        while ((DateTime.UtcNow - startTime).TotalSeconds < RESPONSE_TIMEOUT_SECONDS)
        {
            // Check response queue
            var response = await db.ListLeftPopAsync(RESPONSE_QUEUE);
            if (response.HasValue)
            {
                var responseData = JsonSerializer.Deserialize<ChatMessage>(response!);
                if (responseData?.Id == chatMessage.Id)
                {
                    chatMessage.Response = responseData.Response;
                    return Ok(chatMessage);
                }
            }

            // Also check direct response key
            var directResponse = await db.StringGetAsync($"response:{chatMessage.Id}");
            if (directResponse.HasValue)
            {
                var responseData = JsonSerializer.Deserialize<ChatMessage>(directResponse!);
                chatMessage.Response = responseData?.Response ?? "Error: No response content";
                return Ok(chatMessage);
            }

            await Task.Delay(100); // Small delay to prevent CPU spinning
        }

        return StatusCode(408, new { error = "Response timeout" });
    }

    /// <summary>
    /// Retrieves a specific chat message by ID
    /// </summary>
    /// <remarks>
    /// Sample request:
    /// 
    ///     GET /chat/123e4567-e89b-12d3-a456-426614174000
    /// </remarks>
    /// <param name="id">The GUID of the message to retrieve</param>
    /// <returns>The chat message</returns>
    /// <response code="200">Returns the requested chat message</response>
    /// <response code="404">Message not found</response>
    [HttpGet("{id}")]
    [ProducesResponseType(typeof(ChatMessage), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public async Task<ActionResult<ChatMessage>> GetMessage(string id)
    {
        var db = _redis.GetDatabase();
        var message = await db.StringGetAsync($"{CHAT_KEY_PREFIX}{id}");

        if (!message.HasValue)
            return NotFound();

        return Ok(JsonSerializer.Deserialize<ChatMessage>(message!));
    }
} 