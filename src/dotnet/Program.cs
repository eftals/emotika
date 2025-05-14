using StackExchange.Redis;
using Microsoft.OpenApi.Models;
using Emotika.Api.Services;
using Emotika.Api.Middleware;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(c =>
{
    c.SwaggerDoc("v1", new OpenApiInfo 
    { 
        Title = "Emotika API", 
        Version = "v1",
        Description = "API for the Emotika chat application"
    });
});

// Configure Redis
builder.Services.AddSingleton<IConnectionMultiplexer>(sp =>
{
    var configuration = sp.GetRequiredService<IConfiguration>();
    var redisHost = configuration["REDIS_HOST"] ?? "localhost";
    var redisPort = configuration.GetValue<int>("REDIS_PORT", 6379);
    var config = new ConfigurationOptions
    {
        EndPoints = { $"{redisHost}:{redisPort}" },
        AbortOnConnectFail = false,
        ConnectRetry = 3,
        ConnectTimeout = 5000
    };
    return ConnectionMultiplexer.Connect(config);
});

// Register Session Service
builder.Services.AddScoped<ISessionService, SessionService>();

// Configure CORS
builder.Services.AddCors(options =>
{
    options.AddDefaultPolicy(policy =>
    {
        policy.AllowAnyOrigin()
              .AllowAnyMethod()
              .AllowAnyHeader()
              .WithExposedHeaders("X-Session-Token"); // Allow the session token header
    });
});

var app = builder.Build();

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

// Only use HTTPS redirection in production
if (!app.Environment.IsDevelopment())
{
    app.UseHttpsRedirection();
}

app.UseCors();
app.UseMiddleware<SessionMiddleware>(); // Add session middleware
app.UseAuthorization();
app.MapControllers();

app.Run(); 