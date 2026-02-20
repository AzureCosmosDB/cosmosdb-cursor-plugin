---
name: cosmosdb-data-modeling
description: Azure Cosmos DB data modeling patterns and anti-patterns. Use this skill when designing schemas, choosing between embedding vs. referencing, modeling multi-tenant data, or structuring containers for Azure Cosmos DB NoSQL.
license: MIT
metadata:
  author: Azure Cosmos DB
  version: "1.0.0"
  organization: Microsoft
  date: February 2026
  abstract: Data modeling guidance for Azure Cosmos DB NoSQL API. Covers embedding vs. referencing patterns, multi-tenant design, single vs. multiple container strategies, change feed patterns, and common anti-patterns to avoid.
---

# Azure Cosmos DB Data Modeling

Practical data modeling patterns for Azure Cosmos DB NoSQL API, helping you design efficient schemas that minimize cost and maximize performance.

## When to Apply

Reference these guidelines when:
- Designing a new data model for Cosmos DB
- Migrating from relational database to Cosmos DB
- Deciding between embedding and referencing
- Designing multi-tenant architectures
- Structuring containers and partition strategies
- Evaluating whether to use single or multiple containers

---

## Pattern 1: Embedding (Denormalization)

### When to Embed

- Data is **read together** in most queries
- Related data has a **1:1** or **1:few** relationship
- Embedded data changes **infrequently**
- Embedded data is **bounded** (won't grow without limit)

### Example: User Profile with Address

```json
{
  "id": "user-001",
  "type": "user",
  "name": "Alice Johnson",
  "email": "alice@example.com",
  "address": {
    "street": "123 Main St",
    "city": "Seattle",
    "state": "WA",
    "zip": "98101"
  },
  "preferences": {
    "theme": "dark",
    "language": "en"
  }
}
```

Single read operation, 1 RU for a 1 KB document.

---

## Pattern 2: Referencing (Normalization)

### When to Reference

- Related data is **unbounded** (e.g., activity logs, comments)
- Related data is **updated independently** and frequently
- Related data is **accessed separately** from the parent
- Embedding would push the document over **2 MB**

### Example: Blog Post with Comments

```json
// Post document
{
  "id": "post-001",
  "type": "post",
  "authorId": "user-001",
  "title": "Getting Started with Cosmos DB",
  "body": "...",
  "commentCount": 142
}

// Comment documents (same container, same partition key)
{
  "id": "comment-001",
  "type": "comment",
  "postId": "post-001",
  "authorId": "user-002",
  "body": "Great article!",
  "createdAt": "2026-02-15T10:30:00Z"
}
```

---

## Pattern 3: Single Container with Type Discriminator

Store multiple entity types in one container to enable single-partition queries across related data.

```json
// All partitioned by /tenantId
{ "id": "tenant-001", "type": "tenant", "tenantId": "tenant-001", "name": "Acme Corp" }
{ "id": "user-001",   "type": "user",   "tenantId": "tenant-001", "name": "Alice" }
{ "id": "order-001",  "type": "order",  "tenantId": "tenant-001", "total": 250.00 }
{ "id": "invoice-001","type": "invoice","tenantId": "tenant-001", "amount": 250.00 }
```

Query all data for a tenant in a single partition:
```sql
SELECT * FROM c WHERE c.tenantId = 'tenant-001'
```

Filter by type:
```sql
SELECT * FROM c WHERE c.tenantId = 'tenant-001' AND c.type = 'order'
```

---

## Pattern 4: Multi-Tenant Design

### Option A: Container-per-Tenant (Small Scale)
- Dedicated container per tenant
- Full isolation, simple to reason about
- **Limit**: Does not scale past ~25 tenants (container limit per database)

### Option B: Shared Container with Tenant Partition Key (Recommended)
- Single container partitioned by `/tenantId`
- Scales to thousands of tenants
- Use hierarchical partition keys for very large tenants

```json
{
  "partitionKey": {
    "paths": ["/tenantId", "/entityType"],
    "kind": "MultiHash",
    "version": 2
  }
}
```

### Option C: Database-per-Tenant (Full Isolation)
- Separate database per tenant
- Maximum isolation and separate throughput
- Higher management overhead

---

## Pattern 5: Materialized Views via Change Feed

Use change feed to maintain pre-computed views for read-heavy access patterns.

```
┌─────────────┐    Change Feed    ┌──────────────────┐
│  Source      │ ───────────────>  │  Materialized    │
│  Container  │                   │  View Container  │
└─────────────┘                   └──────────────────┘
```

Example: An e-commerce app writes orders to a main container but maintains a "top products by category" view in a separate container, updated in real-time via change feed.

---

## Common Anti-Patterns to Avoid

| Anti-Pattern | Why It's Bad | Fix |
|---|---|---|
| Normalizing everything like a relational DB | Multiple round-trips, high RU cost | Embed related data when read together |
| Using large unbounded arrays | Documents exceed 2 MB, slow writes | Reference with separate documents |
| Using low-cardinality partition key | Hot partitions, throttling | Choose high-cardinality key |
| Storing all entity types without a discriminator | Cannot filter efficiently | Add a `type` field |
| Over-indexing every property | Higher write RU cost | Customize indexing policy |
| Single-document transactions across partitions | Not supported | Design data within partitions |
| Ignoring item size growth | Hits 2 MB limit over time | Monitor and split documents |

---

## Decision Framework

```
Is the related data always read together?
├── YES: Is it bounded (won't grow past ~100 items)?
│   ├── YES: EMBED
│   └── NO: REFERENCE (separate documents, same partition)
└── NO: Is it updated independently?
    ├── YES: REFERENCE
    └── NO: Consider EMBEDDING with review
```

---

## References

- https://learn.microsoft.com/azure/cosmos-db/nosql/model-document-data
- https://learn.microsoft.com/azure/cosmos-db/nosql/model-partition-example
- https://learn.microsoft.com/azure/cosmos-db/hierarchical-partition-keys
- https://learn.microsoft.com/azure/cosmos-db/nosql/change-feed-design-patterns
