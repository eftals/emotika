using System.Text.Json;
using Emotika.Api.Models;
using Emotika.Api.Services;
using Microsoft.Extensions.DependencyInjection;

namespace Emotika.Api.Middleware;

public class SessionMiddleware
{
    private readonly RequestDelegate _next;

    public SessionMiddleware(RequestDelegate next)
    {
        _next = next;
    }

    public async Task InvokeAsync(HttpContext context)
    {
        // Get the session service from the service provider
        var sessionService = context.RequestServices.GetRequiredService<ISessionService>();
        
        // Skip session validation for OPTIONS requests (CORS preflight)
        if (context.Request.Method == "OPTIONS")
        {
            await _next(context);
            return;
        }

        // Get session token from header
        var sessionToken = context.Request.Headers["X-Session-Token"].ToString();

        // If no session token is provided, create a new session
        if (string.IsNullOrEmpty(sessionToken))
        {
            var newSession = await sessionService.CreateSessionAsync();
            context.Response.Headers.Add("X-Session-Token", newSession.Token);
            await _next(context);
            return;
        }

        // Validate existing session
        var isValid = await sessionService.IsValidSessionAsync(sessionToken);
        if (!isValid)
        {
            context.Response.StatusCode = 401;
            var error = new { error = "Invalid or expired session" };
            await context.Response.WriteAsJsonAsync(error);
            return;
        }

        // Update session activity
        await sessionService.UpdateSessionAsync(sessionToken);

        // Continue with the request
        await _next(context);
    }
} 