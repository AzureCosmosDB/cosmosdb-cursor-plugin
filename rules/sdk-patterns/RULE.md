<!-- Auto-generated from skills/cosmosdb-best-practices/rules/sdk-*.md -->
<!-- Regenerate: run .cursor/prompts/generate-rules.md -->
---
description: "Azure Cosmos DB SDK best practices: singleton client, connection mode, retries, diagnostics, async patterns, concurrency, and resilience"
globs:
  - "**/*.{cs,ts,js,py,java}"
alwaysApply: false
---

# SDK Best Practices

Proper SDK usage ensures connection efficiency, retry handling, and optimal throughput. Common mistakes include creating multiple clients and ignoring throttling.

## Reuse CosmosClient as singleton

Never create a new client per request. CosmosClient manages connections, caches, and routing — creating multiples causes resource exhaustion.

```csharp
// ❌ Bad - new client per request
public async Task<Order> GetOrder(string id)
{
    using var client = new CosmosClient(connectionString);  // Expensive!
    var container = client.GetContainer("db", "orders");
    return (await container.ReadItemAsync<Order>(id, pk)).Resource;
}

// ✅ Good - singleton via DI
builder.Services.AddSingleton(sp =>
{
    return new CosmosClient(connectionString, new CosmosClientOptions
    {
        ApplicationName = "my-app",
        ConnectionMode = ConnectionMode.Direct,
        MaxRetryAttemptsOnRateLimitedRequests = 9,
        MaxRetryWaitTimeOnRateLimitedRequests = TimeSpan.FromSeconds(30)
    });
});
```

## Use Direct connection mode for production

Direct mode provides lower latency than Gateway mode. It is the default in .NET SDK v3+.

```csharp
// ✅ Good - explicit Direct mode
var options = new CosmosClientOptions
{
    ConnectionMode = ConnectionMode.Direct  // Default, but be explicit
};

// Use Gateway only when behind restrictive firewalls
// that block the port range 10000-20000
```

## Handle 429 errors with Retry-After

The SDK has built-in retry logic for 429 (Too Many Requests). Configure it appropriately.

```csharp
// ✅ Good - configure retry settings
var options = new CosmosClientOptions
{
    MaxRetryAttemptsOnRateLimitedRequests = 9,
    MaxRetryWaitTimeOnRateLimitedRequests = TimeSpan.FromSeconds(30)
};

// For custom retry logic
try
{
    await container.CreateItemAsync(item, pk);
}
catch (CosmosException ex) when (ex.StatusCode == HttpStatusCode.TooManyRequests)
{
    _logger.LogWarning("Throttled. RetryAfter: {RetryAfter}", ex.RetryAfter);
    await Task.Delay(ex.RetryAfter ?? TimeSpan.FromSeconds(1));
    // Retry the operation
}
```

## Configure preferred regions

List regions closest to your application first for lowest latency and automatic failover.

```csharp
var options = new CosmosClientOptions
{
    ApplicationPreferredRegions = new List<string>
    {
        Regions.EastUS,      // Closest region first
        Regions.WestUS2,     // Failover region
        Regions.WestEurope   // Tertiary
    }
};
// Include at least 2 regions for redundancy
```

## Log diagnostics for troubleshooting

Capture diagnostics on slow or failed operations. They contain regions contacted, retry info, and timing.

```csharp
var response = await container.ReadItemAsync<Order>(id, pk);

// Log diagnostics for slow operations
if (response.Diagnostics.GetClientElapsedTime() > TimeSpan.FromMilliseconds(100))
{
    _logger.LogWarning(
        "Slow read: {Ms}ms, RU: {RU}, Diagnostics: {Diag}",
        response.Diagnostics.GetClientElapsedTime().TotalMilliseconds,
        response.RequestCharge,
        response.Diagnostics.ToString());
}

// CRITICAL: Always log diagnostics on failure
catch (CosmosException ex)
{
    _logger.LogError(ex,
        "Failed: Status={Status}, RU={RU}, Diagnostics={Diag}",
        ex.StatusCode, ex.RequestCharge, ex.Diagnostics?.ToString());
    throw;
}
```

## Use async APIs — never block

Synchronous calls block threads and cause pool exhaustion under load.

```csharp
// ❌ Bad - blocks thread
var response = container.ReadItemAsync<Order>(id, pk).Result;

// ✅ Good - async all the way
var response = await container.ReadItemAsync<Order>(id, pk);

// ✅ Concurrent operations
var orderTask = container.ReadItemAsync<Order>(id, pk);
var itemsTask = container.GetItemQueryIterator<OrderItem>(query).ReadNextAsync();
await Task.WhenAll(orderTask, itemsTask);
```

## Use ETags for optimistic concurrency

Prevent lost updates in read-modify-write patterns with ETag checks.

```csharp
// ✅ Good - ETag-based optimistic concurrency
var response = await container.ReadItemAsync<Player>(id, pk);
var player = response.Resource;
var etag = response.ETag;

player.BestScore = Math.Max(player.BestScore, newScore);

await container.ReplaceItemAsync(player, id, pk,
    new ItemRequestOptions { IfMatchEtag = etag });
// Throws CosmosException (412 PreconditionFailed) if document changed
```

## Configure availability strategy (hedging)

For latency-sensitive reads, configure threshold-based availability strategy to hedge requests to secondary regions.

```csharp
// ✅ Good - hedge reads to secondary region after 500ms
var options = new CosmosClientOptions
{
    AvailabilityStrategy = new ThresholdBasedAvailabilityStrategy(
        threshold: TimeSpan.FromMilliseconds(500),
        thresholdStep: TimeSpan.FromMilliseconds(100))
};
// If primary region doesn't respond in 500ms, sends parallel request to next region
```

## Configure partition-level circuit breaker

Isolate unhealthy partitions to prevent cascading failures.

```csharp
// ✅ Good - enable circuit breaker
var options = new CosmosClientOptions
{
    PartitionLevelCircuitBreakerConfig = new PartitionLevelCircuitBreakerConfig
    {
        IsEnabled = true
    }
};
// Automatically routes around unhealthy partitions
// Requires preferred regions configured
```

## Configure excluded regions for dynamic failover

Programmatically exclude regions at runtime during regional outages.

```csharp
// ✅ Good - exclude region during outage
var requestOptions = new ItemRequestOptions
{
    ExcludedRegions = new List<string> { Regions.EastUS }
};
await container.ReadItemAsync<Order>(id, pk, requestOptions);
```

## Language-specific patterns

### .NET
- Use `AllowBulkExecution = true` for batch ingestion
- Explicitly reference `Newtonsoft.Json` if using the serializer
- Use stream APIs when you don't need deserialization

### Java
- Enable `contentResponseOnWriteEnabled(false)` to reduce response payload on writes
- Use `@Bean` methods with dependent injection for Cosmos DB initialization in Spring Boot
- Match Spring Boot and Java SDK versions for compatibility

### Local development
- Use Cosmos DB Emulator with `CosmosClientOptions.HttpClientFactory` for custom SSL handling
- Set `COSMOS_ENDPOINT` and `COSMOS_KEY` environment variables
- Use `ConnectionMode.Gateway` with emulator

Reference: [.NET SDK best practices](https://learn.microsoft.com/azure/cosmos-db/nosql/best-practice-dotnet) | [Java SDK best practices](https://learn.microsoft.com/azure/cosmos-db/nosql/best-practice-java)
