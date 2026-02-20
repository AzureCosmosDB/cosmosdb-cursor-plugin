<!-- Auto-generated from skills/cosmosdb-best-practices/rules/pattern-*.md -->
<!-- Regenerate: run .cursor/prompts/generate-rules.md -->
---
description: "Azure Cosmos DB design patterns: change feed materialized views, efficient ranking, and cross-partition optimization"
globs:
  - "**/*.{cs,ts,js,py,java}"
alwaysApply: false
---

# Design Patterns

Architecture patterns for common scenarios like cross-partition query optimization, event sourcing, and multi-tenant designs.

## Use Change Feed for materialized views

Use Change Feed to maintain denormalized views optimized for specific query patterns, avoiding expensive cross-partition queries.

```csharp
// Problem: "Get top products across all categories" requires cross-partition scan
// Solution: Change Feed processor creates materialized view in a separate container

// Source container: partitioned by /categoryId
public class Product
{
    public string Id { get; set; }
    public string CategoryId { get; set; }  // Partition key
    public string Name { get; set; }
    public decimal Price { get; set; }
    public double Rating { get; set; }
}

// Materialized view container: partitioned by /viewType
public class TopProductView
{
    public string Id { get; set; }            // "top-rated"
    public string ViewType { get; set; }      // Partition key: "top-rated"
    public List<ProductSummary> Products { get; set; }
    public DateTime LastUpdated { get; set; }
}

// Change Feed processor keeps the view in sync
var processor = container.GetChangeFeedProcessorBuilder<Product>(
    "top-products-view",
    async (IReadOnlyCollection<Product> changes, CancellationToken ct) =>
    {
        // Rebuild the materialized view with updated data
        var topProducts = await GetTopRatedProducts();
        await viewContainer.UpsertItemAsync(new TopProductView
        {
            Id = "top-rated",
            ViewType = "top-rated",
            Products = topProducts,
            LastUpdated = DateTime.UtcNow
        });
    })
    .WithInstanceName("instance-1")
    .WithLeaseContainer(leaseContainer)
    .Build();

await processor.StartAsync();
```

Benefits:
- Query the materialized view with a single-partition point read (~1 RU)
- Source data stays partitioned for write efficiency
- Change Feed keeps views eventually consistent
- Scale processors independently

## Use count-based or cached rank approaches for ranking

Avoid scanning entire partitions for ranking queries. Use pre-computed ranks.

```csharp
// ❌ Bad - full partition scan for rank
var query = "SELECT VALUE COUNT(1) FROM c WHERE c.score > @score";
// Scans all documents to count those with higher scores

// ✅ Good - cached leaderboard with Change Feed
public class LeaderboardEntry
{
    public string Id { get; set; }           // "leaderboard"
    public string PartitionKey { get; set; } // "global"
    public List<RankedPlayer> TopPlayers { get; set; }  // Top N cached
    public DateTime LastUpdated { get; set; }
}

// Change Feed updates the leaderboard when scores change
// Point read to get leaderboard: ~1 RU instead of full scan
```

## Multi-tenant patterns

### Tenant-per-partition (recommended for most cases)

```csharp
public class TenantDocument
{
    public string Id { get; set; }
    public string TenantId { get; set; }  // Partition key
    public string Type { get; set; }
}
// Natural isolation, efficient per-tenant queries
// Use hierarchical partition keys if tenants exceed 20GB
```

### Container-per-tenant (for strict isolation)

```csharp
// Only when regulatory requirements demand physical isolation
// Higher operational overhead, harder to manage at scale
var container = database.GetContainer($"tenant-{tenantId}");
```

## Event sourcing with Change Feed

```csharp
// Store events as immutable documents
public class DomainEvent
{
    public string Id { get; set; }
    public string AggregateId { get; set; }  // Partition key
    public string EventType { get; set; }
    public int Version { get; set; }
    public JsonElement Data { get; set; }
    public DateTime Timestamp { get; set; }
}

// Change Feed projects events into read models
// Each event is processed exactly once (at-least-once with idempotency)
```

Reference: [Change feed](https://learn.microsoft.com/azure/cosmos-db/change-feed) | [Design patterns](https://learn.microsoft.com/azure/cosmos-db/nosql/model-partition-example)
