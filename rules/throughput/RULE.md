<!-- Auto-generated from skills/cosmosdb-best-practices/rules/throughput-*.md -->
<!-- Regenerate: run .cursor/prompts/generate-rules.md -->
---
description: "Azure Cosmos DB throughput and scaling: autoscale, serverless, burst capacity, and right-sizing"
globs:
  - "**/*.{cs,ts,js,py,java,json}"
alwaysApply: false
---

# Throughput & Scaling

Right-sizing throughput balances cost and performance. Over-provisioning wastes money; under-provisioning causes throttling.

## Use autoscale for variable workloads

Autoscale adjusts RU/s between 10% and 100% of a configured maximum based on demand.

```csharp
// ✅ Good - autoscale for production workloads with variable traffic
await database.CreateContainerAsync(new ContainerProperties("orders", "/customerId"),
    throughput: ThroughputProperties.CreateAutoscaleThroughput(maxThroughput: 10000));
// Scales between 1,000–10,000 RU/s based on demand
// Pay for actual usage, not peak

// ❌ Bad - fixed throughput for unpredictable workloads
await database.CreateContainerAsync(properties, throughput: 10000);
// Paying for 10,000 RU/s even at 2am when traffic is near zero
```

Use autoscale when:
- Traffic patterns are variable or unpredictable
- You want automatic cost optimization
- Peak-to-baseline ratio > 2x

## Consider serverless for dev/test

Serverless charges per-RU consumed with no minimum. Ideal for development, testing, and low-traffic workloads.

```csharp
// ✅ Good - serverless for dev/test
await client.CreateDatabaseAsync("dev-db");
await database.CreateContainerAsync(
    new ContainerProperties("test-data", "/id"));
// No throughput provisioning needed — pay per request
// Max burst: 5,000 RU/s
```

Serverless limitations:
- Max 5,000 RU/s burst
- Max 1TB storage per container
- Single-region only
- No dedicated throughput guarantees

## Choose container vs database throughput

- **Container throughput**: Dedicated RU/s per container. Best for predictable, high-throughput containers.
- **Database throughput**: Shared RU/s across containers. Best when you have many containers with variable traffic.

```csharp
// Container-level: each container gets guaranteed throughput
await database.CreateContainerAsync(properties,
    ThroughputProperties.CreateAutoscaleThroughput(10000));

// Database-level: shared across all containers
await client.CreateDatabaseAsync("mydb",
    ThroughputProperties.CreateAutoscaleThroughput(20000));
// Each container can burst up to the full 20,000 RU/s
// Hot containers may starve cold ones
```

## Right-size provisioned throughput

Monitor actual RU consumption and adjust. Track `Normalized RU Consumption` in Azure Monitor.

- **< 30% normalized RU**: You're over-provisioned — reduce to save cost
- **60–80%**: Healthy range
- **> 90%**: Risk of throttling — scale up or enable autoscale

```csharp
// Check RU consumption on every response
var response = await container.ReadItemAsync<Order>(id, pk);
_logger.LogDebug("Operation consumed {RU} RU", response.RequestCharge);

// Track RU budgets
if (response.RequestCharge > 50)
    _logger.LogWarning("High RU operation: {RU} RU", response.RequestCharge);
```

## Understand burst capacity

Cosmos DB allows short bursts above provisioned throughput using accumulated unused RU/s. Burst capacity is limited and not guaranteed.

- Unused RU/s accumulate for up to 5 minutes
- Maximum burst: 3,000 RU/s above provisioned
- Don't rely on burst for sustained traffic — use autoscale instead

Reference: [Throughput overview](https://learn.microsoft.com/azure/cosmos-db/set-throughput) | [Autoscale](https://learn.microsoft.com/azure/cosmos-db/provision-throughput-autoscale) | [Serverless](https://learn.microsoft.com/azure/cosmos-db/serverless)
