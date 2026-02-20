---
name: cosmosdb-nosql-best-practices
description: Azure Cosmos DB NoSQL performance optimization and best practices. Use this skill when writing, reviewing, or optimizing Cosmos DB queries, data models, partition key strategies, SDK usage, or database configurations.
license: MIT
metadata:
  author: Azure Cosmos DB
  version: "1.0.0"
  organization: Microsoft
  date: February 2026
  abstract: Comprehensive Azure Cosmos DB NoSQL best practices guide for developers. Covers data modeling, partition key selection, query optimization, SDK best practices, indexing strategies, throughput management, and consistency levels. Each section includes detailed explanations, incorrect vs. correct examples, and performance considerations.
---

# Azure Cosmos DB NoSQL Best Practices

Comprehensive performance optimization and best practices guide for Azure Cosmos DB NoSQL API, covering data modeling, query optimization, SDK usage, and operational excellence.

## When to Apply

Reference these guidelines when:
- Designing data models for Azure Cosmos DB NoSQL
- Choosing partition keys for containers
- Writing or optimizing SQL queries against Cosmos DB
- Configuring SDKs and connection settings
- Managing throughput (RU/s) and scaling strategies
- Implementing indexing policies
- Selecting consistency levels
- Working with change feed or stored procedures
- Reviewing Cosmos DB application performance

## Category Overview

| Priority | Category | Impact |
|----------|----------|--------|
| 1 | Partition Key Selection | CRITICAL |
| 2 | Data Modeling | CRITICAL |
| 3 | Query Optimization | CRITICAL |
| 4 | SDK Best Practices | HIGH |
| 5 | Indexing Strategies | HIGH |
| 6 | Throughput Management | HIGH |
| 7 | Consistency Levels | MEDIUM |
| 8 | Operational Excellence | MEDIUM |

---

## 1. Partition Key Selection (CRITICAL)

### Choose High-Cardinality Keys

Select a partition key with many distinct values to ensure even data distribution.

**Bad - Low cardinality key:**
```json
{
  "partitionKey": "/status"
}
```
Status only has a few values (active, inactive, pending) causing hot partitions.

**Good - High cardinality key:**
```json
{
  "partitionKey": "/userId"
}
```
userId has many unique values ensuring even distribution across logical partitions.

### Match Your Query Patterns

The partition key should align with your most frequent queries to avoid cross-partition fan-out.

**Bad - Querying by a field that is NOT the partition key causes cross-partition queries:**
```sql
SELECT * FROM c WHERE c.category = 'electronics'
-- If partitioned by /userId, this fans out to ALL partitions
```

**Good - Querying by partition key targets a single partition:**
```sql
SELECT * FROM c WHERE c.userId = 'user-123'
-- Single partition query, much cheaper in RU/s
```

### Use Hierarchical Partition Keys for Large Datasets

When a single partition value can exceed 20 GB, use hierarchical partition keys (up to 3 levels).

```json
{
  "partitionKey": {
    "paths": ["/tenantId", "/departmentId", "/userId"],
    "kind": "MultiHash",
    "version": 2
  }
}
```

Benefits:
- Overcomes the 20 GB single logical partition limit
- Queries can still target specific sub-partitions
- Supports multi-tenant architectures efficiently

### Avoid These as Partition Keys

- **Timestamps** — creates append-only hot partitions
- **Boolean fields** — only 2 values, extreme skew
- **Low-cardinality enums** — small set of values
- **Monotonically increasing IDs** — concentrates writes on a single partition

---

## 2. Data Modeling (CRITICAL)

### Embed Related Data When Accessed Together

If data is always read or written together, embed it in a single document.

**Bad - Separate documents with unnecessary lookups:**
```json
// Order document
{ "id": "order-1", "customerId": "cust-1", "total": 99.99 }

// Order items in separate collection
{ "id": "item-1", "orderId": "order-1", "product": "Widget", "qty": 2 }
{ "id": "item-2", "orderId": "order-1", "product": "Gadget", "qty": 1 }
```

**Good - Embedded model, single read:**
```json
{
  "id": "order-1",
  "customerId": "cust-1",
  "total": 99.99,
  "items": [
    { "product": "Widget", "qty": 2, "price": 49.99 },
    { "product": "Gadget", "qty": 1, "price": 50.00 }
  ]
}
```

### Use References for Unbounded or Independently Updated Data

When embedded arrays can grow without limit or sub-documents are updated independently, use references.

**Bad - Unbounded array that grows indefinitely:**
```json
{
  "id": "user-1",
  "name": "Alice",
  "activityLog": [
    { "action": "login", "ts": "2026-01-01T00:00:00Z" },
    // ... thousands of entries, document exceeds 2 MB limit
  ]
}
```

**Good - Separate documents with a reference:**
```json
// User document
{ "id": "user-1", "name": "Alice", "type": "user" }

// Activity log entries (same container, partitioned by userId)
{ "id": "activity-1", "userId": "user-1", "action": "login", "ts": "2026-01-01T00:00:00Z", "type": "activity" }
```

### Respect the 2 MB Item Size Limit

Azure Cosmos DB enforces a maximum item size of 2 MB. Design documents to stay well under this limit.

### Use a Type Discriminator for Heterogeneous Containers

Store multiple entity types in the same container and distinguish them with a `type` field.

```json
{ "id": "user-1", "type": "user", "name": "Alice", "userId": "user-1" }
{ "id": "order-1", "type": "order", "userId": "user-1", "total": 99.99 }
```

This enables single-partition reads for all data related to one user.

---

## 3. Query Optimization (CRITICAL)

### Always Include the Partition Key in Queries

```sql
-- Bad: Cross-partition query (high RU cost)
SELECT * FROM c WHERE c.email = 'alice@example.com'

-- Good: Single-partition query
SELECT * FROM c WHERE c.userId = 'user-1' AND c.email = 'alice@example.com'
```

### Project Only Required Fields

```sql
-- Bad: Returns entire document
SELECT * FROM c WHERE c.userId = 'user-1'

-- Good: Returns only needed fields, reduces RU and bandwidth
SELECT c.id, c.name, c.email FROM c WHERE c.userId = 'user-1'
```

### Avoid High-Cost Operators

- **Avoid** `LIKE '%text%'` (leading wildcard) — causes full scan
- **Avoid** cross-partition `ORDER BY` without partition key filter
- **Avoid** user-defined functions (UDFs) in queries — they bypass the index
- **Prefer** `ARRAY_CONTAINS` over `JOIN` for simple array membership checks

### Use Pagination with Continuation Tokens

```csharp
// C# SDK example
var query = container.GetItemQueryIterator<dynamic>(
    "SELECT * FROM c WHERE c.type = 'order'",
    requestOptions: new QueryRequestOptions { MaxItemCount = 50 }
);

while (query.HasMoreResults)
{
    var response = await query.ReadNextAsync();
    // Process response.Resource
    // response.ContinuationToken for next page
}
```

---

## 4. SDK Best Practices (HIGH)

### Use a Singleton CosmosClient

**Bad - Creating new clients per request wastes resources:**
```csharp
// Anti-pattern: new client per request
public async Task GetItem()
{
    using var client = new CosmosClient(endpoint, key);
    // ...
}
```

**Good - Singleton client reused across the application:**
```csharp
// Register as singleton in DI
services.AddSingleton(sp =>
{
    return new CosmosClient(endpoint, key, new CosmosClientOptions
    {
        ApplicationRegion = Regions.WestUS2,
        ConnectionMode = ConnectionMode.Direct,
        MaxRetryAttemptsOnRateLimitedRequests = 9,
        MaxRetryWaitTimeOnRateLimitedRequests = TimeSpan.FromSeconds(30)
    });
});
```

### Use Direct Connection Mode

Direct mode provides lower latency than Gateway mode for most workloads.

```csharp
new CosmosClientOptions
{
    ConnectionMode = ConnectionMode.Direct
}
```

### Handle 429 (Rate Limited) Responses

```csharp
try
{
    var response = await container.ReadItemAsync<dynamic>(id, partitionKey);
}
catch (CosmosException ex) when (ex.StatusCode == HttpStatusCode.TooManyRequests)
{
    // Retry after the duration specified in the response
    await Task.Delay(ex.RetryAfter ?? TimeSpan.FromSeconds(1));
    // Retry the operation
}
```

### Use Async APIs and Bulk Execution for High Throughput

```csharp
// Enable bulk execution
new CosmosClientOptions { AllowBulkExecution = true };

// Then use Task.WhenAll for concurrent operations
var tasks = items.Select(item =>
    container.CreateItemAsync(item, new PartitionKey(item.UserId))
);
await Task.WhenAll(tasks);
```

### Capture Diagnostics for Troubleshooting

```csharp
var response = await container.ReadItemAsync<dynamic>(id, partitionKey);
if (response.Diagnostics.GetClientElapsedTime() > TimeSpan.FromMilliseconds(100))
{
    logger.LogWarning("High latency detected: {Diagnostics}", response.Diagnostics);
}
```

---

## 5. Indexing Strategies (HIGH)

### Customize Indexing Policy

The default policy indexes all properties. Exclude paths you never query on to save RU/s on writes.

```json
{
  "indexingMode": "consistent",
  "includedPaths": [
    { "path": "/userId/?" },
    { "path": "/createdAt/?" },
    { "path": "/category/?" }
  ],
  "excludedPaths": [
    { "path": "/largePayload/*" },
    { "path": "/_etag/?" }
  ]
}
```

### Add Composite Indexes for Multi-Property ORDER BY

```json
{
  "compositeIndexes": [
    [
      { "path": "/category", "order": "ascending" },
      { "path": "/createdAt", "order": "descending" }
    ]
  ]
}
```

Required when your query uses `ORDER BY` on multiple properties:
```sql
SELECT * FROM c ORDER BY c.category ASC, c.createdAt DESC
```

### Use Vector Indexes for AI/Similarity Search

```json
{
  "vectorIndexes": [
    {
      "path": "/embedding",
      "type": "quantizedFlat"
    }
  ]
}
```

---

## 6. Throughput Management (HIGH)

### Use Autoscale for Variable Workloads

```csharp
await database.CreateContainerAsync(new ContainerProperties
{
    Id = "my-container",
    PartitionKeyPath = "/userId"
},
ThroughputProperties.CreateAutoscaleThroughput(maxThroughput: 4000));
```

Autoscale provisions between 10% and 100% of max RU/s, adapting to demand.

### Use Serverless for Dev/Test and Low-Traffic

For sporadic workloads or development, serverless eliminates provisioning decisions and charges per-operation only.

### Monitor and Optimize RU Consumption

- Check `x-ms-request-charge` response header for actual RU cost per operation
- Use Azure Monitor metrics: `TotalRequestUnits`, `NormalizedRUConsumption`
- Target `NormalizedRUConsumption` below 70% to avoid throttling

---

## 7. Consistency Levels (MEDIUM)

| Level | Guarantee | RU Cost | Use Case |
|-------|-----------|---------|----------|
| Strong | Linearizable reads | 2x | Financial transactions |
| Bounded Staleness | Reads lag by at most K versions or T time | 2x | Leaderboards |
| Session (default) | Read-your-writes within a session | 1x | Most applications |
| Consistent Prefix | Ordered, no gaps | 1x | Social feeds |
| Eventual | Highest availability, lowest latency | 1x | Telemetry, non-critical reads |

**Recommendation**: Start with **Session** consistency (default). Only use Strong when strictly necessary — it doubles RU cost and increases latency.

---

## 8. Operational Excellence (MEDIUM)

### Enable Multi-Region Writes for Global Apps

Configure preferred regions closest to your users:
```csharp
new CosmosClientOptions
{
    ApplicationPreferredRegions = new List<string> { "West US 2", "East US" }
}
```

### Use Change Feed for Event-Driven Architectures

Change feed captures inserts and updates, ideal for:
- Materializing views
- Triggering downstream processing
- Syncing to search indexes or caches

### Use Point Reads Over Queries When Possible

```csharp
// Point read: 1 RU for a 1 KB document
var response = await container.ReadItemAsync<MyItem>(id, new PartitionKey(userId));

// vs. Query: Higher RU cost
var query = container.GetItemQueryIterator<MyItem>("SELECT * FROM c WHERE c.id = @id");
```

### Use TTL for Automatic Data Expiration

```json
{
  "defaultTtl": 2592000
}
```
Set TTL (in seconds) to automatically delete old documents without manual cleanup.

---

## References

- https://learn.microsoft.com/azure/cosmos-db/nosql/
- https://learn.microsoft.com/azure/cosmos-db/nosql/best-practice-dotnet
- https://learn.microsoft.com/azure/cosmos-db/nosql/how-to-query
- https://learn.microsoft.com/azure/cosmos-db/nosql/index-policy
- https://learn.microsoft.com/azure/cosmos-db/hierarchical-partition-keys
- https://learn.microsoft.com/azure/well-architected/service-guides/cosmos-db
