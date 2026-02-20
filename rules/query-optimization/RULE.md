<!-- Auto-generated from skills/cosmosdb-best-practices/rules/query-*.md -->
<!-- Regenerate: run .cursor/prompts/generate-rules.md -->
---
description: "Azure Cosmos DB query optimization: avoid cross-partition queries, full scans, use projections and parameterization"
globs:
  - "**/*.{cs,ts,js,py,java}"
alwaysApply: false
---

# Query Optimization

Optimized queries minimize RU consumption and latency. Inefficient queries cause unnecessary cross-partition scans and index misses.

## Minimize cross-partition queries

Always include the partition key in queries to avoid cross-partition fan-out.

```csharp
// ❌ Bad - cross-partition fan-out, scans ALL partitions
var query = new QueryDefinition("SELECT * FROM c WHERE c.email = @email")
    .WithParameter("@email", email);
// High RU, high latency

// ✅ Good - single-partition query
var query = new QueryDefinition("SELECT * FROM c WHERE c.customerId = @id AND c.email = @email")
    .WithParameter("@id", customerId)
    .WithParameter("@email", email);
var options = new QueryRequestOptions { PartitionKey = new PartitionKey(customerId) };

// ✅ Best - point read when you have id + partition key
var response = await container.ReadItemAsync<Customer>(id, new PartitionKey(customerId));
// ~1 RU for point read vs 3-10+ RU for query
```

## Avoid full container scans

Never use queries that force scanning every document. Ensure queries hit indexes.

```csharp
// ❌ Bad - function on property prevents index usage
var query = "SELECT * FROM c WHERE LOWER(c.name) = 'john'";

// ❌ Bad - NOT operator often causes scans
var query = "SELECT * FROM c WHERE NOT c.isActive = true";

// ✅ Good - store lowercase version, direct equality
var query = "SELECT * FROM c WHERE c.nameLower = 'john'";

// ✅ Good - query for the positive case
var query = "SELECT * FROM c WHERE c.isActive = false";
```

## Project only needed fields

Select only the fields you need instead of `SELECT *` to reduce RU cost and network transfer.

```csharp
// ❌ Bad - returns entire document including large fields
var query = "SELECT * FROM c WHERE c.type = 'product'";

// ✅ Good - only what's needed
var query = "SELECT c.id, c.name, c.price, c.category FROM c WHERE c.type = 'product'";
// Can reduce RU by 50%+ for documents with many or large fields
```

## Use parameterized queries

Always use parameters instead of string concatenation to prevent injection and enable query plan caching.

```csharp
// ❌ Bad - string interpolation (injection risk + no plan caching)
var query = $"SELECT * FROM c WHERE c.name = '{userInput}'";

// ✅ Good - parameterized
var query = new QueryDefinition("SELECT * FROM c WHERE c.name = @name AND c.type = @type")
    .WithParameter("@name", userInput)
    .WithParameter("@type", "product");
```

## Use continuation tokens for pagination

Never use OFFSET/LIMIT for deep pagination. Use continuation tokens for efficient page-through.

```csharp
// ❌ Bad - OFFSET skips items by reading them (RU scales with offset)
var query = "SELECT * FROM c ORDER BY c.createdAt OFFSET 10000 LIMIT 50";

// ✅ Good - continuation tokens
string continuationToken = null;
var options = new QueryRequestOptions { MaxItemCount = 50 };

var iterator = container.GetItemQueryIterator<Product>(queryDef, continuationToken, options);
var response = await iterator.ReadNextAsync();

// Return token to client for next page
var nextToken = response.ContinuationToken;
// Client sends nextToken back for the next page
```

## Order filters by selectivity

Put the most selective (fewest matching documents) filter first in WHERE clauses.

```csharp
// ❌ Bad - broad filter first
var query = "SELECT * FROM c WHERE c.type = 'order' AND c.orderId = 'ORD-12345'";
// type matches millions, then narrows

// ✅ Good - most selective filter first
var query = "SELECT * FROM c WHERE c.orderId = 'ORD-12345' AND c.type = 'order'";
// orderId matches 1 document immediately
```

Reference: [Query best practices](https://learn.microsoft.com/azure/cosmos-db/nosql/query/best-practices) | [Pagination](https://learn.microsoft.com/azure/cosmos-db/nosql/query/pagination)
