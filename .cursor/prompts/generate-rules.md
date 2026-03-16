# Generate Cursor Rules from Agent Kit

This prompt regenerates the `rules/` folder (Cursor IDE `.mdc` format) from the source of truth in the [cosmosdb-agent-kit](https://github.com/Azure-Samples/cosmosdb-agent-kit) repo at `skills/cosmosdb-best-practices/rules/`.

Run this prompt in Cursor whenever the agent kit rules are updated.

---

## Instructions

Fetch all markdown files from `https://github.com/Azure-Samples/cosmosdb-agent-kit/tree/main/skills/cosmosdb-best-practices/rules/` (excluding files starting with `_`). Group them by their filename prefix using the mapping below. For each group, generate a `rules/<name>.mdc` file following the Cursor plugin rules format.

### Category mapping (filename prefix → folder)

| Prefix | File | Description |
|--------|------|-------------|
| `model-` | `data-modeling.mdc` | Document design, embedding, referencing, size limits, schema evolution |
| `partition-` | `partition-key.mdc` | Cardinality, hot partitions, hierarchical keys, query alignment |
| `query-` | `query-optimization.mdc` | Cross-partition queries, scans, projections, pagination, parameterization |
| `sdk-` | `sdk-patterns.mdc` | Singleton client, connection mode, retries, diagnostics, async, concurrency |
| `index-` | `indexing.mdc` | Composite indexes, excluded paths, index types, spatial indexes |
| `throughput-` | `throughput.mdc` | Autoscale, serverless, burst capacity, right-sizing |
| `global-` | `global-distribution.mdc` | Multi-region, consistency levels, failover, conflict resolution |
| `monitoring-` | `monitoring.mdc` | RU consumption, latency, throttling, diagnostic logs, Azure Monitor |
| `pattern-` | `design-patterns.mdc` | Change feed, materialized views, ranking, multi-tenant patterns |
| `vector-` | `vector-search.mdc` | Feature enablement, embedding policies, vector indexes, VectorDistance |

### .mdc rule format

Each generated `.mdc` file must follow this exact structure:

```markdown
---
description: "Azure Cosmos DB <topic>: <comma-separated key concepts>"
globs:
  - "**/*.{cs,ts,js,py,java,json}"
alwaysApply: false
---

# <Section Title>

<Section description from _sections.md>

## <Rule title from source file>

<Brief explanation of the rule>

\```<language>
// ❌ Bad - <what's wrong>
<incorrect code from source>

// ✅ Good - <what's right>
<correct code from source>
\```

<Additional guidance, key points, or tables if present in source>

Reference: [<link text>](<url>)
```

### Rules for generation

1. **Read `_sections.md`** for section titles and descriptions
2. **For each source `.md` file**, extract:
   - Title from YAML frontmatter `title:` field
   - Impact from `impact:` field
   - Code examples (both incorrect and correct)
   - Key points, tables, or bullet lists
   - Reference links
3. **Consolidate** all rules in a category into a single `RULE.md`
4. **Keep code examples concise** — use the most impactful example from each source file, not all of them. Prefer the C# example with one other language if available.
5. **Preserve all reference links** from source files
6. **Order rules within each file** by impact: CRITICAL → HIGH → MEDIUM → LOW
7. **For `sdk-patterns.mdc`**, separate .NET/Java/Python-specific rules into a "Language-specific patterns" section at the end
8. **Add `globs`** appropriate to the content:
   - Rules with code examples: `"**/*.{cs,ts,js,py,java}"`
   - Rules with JSON config (indexing, data-modeling): add `json` to the glob

### Overview rule

Also regenerate `rules/cosmosdb-overview.mdc` as an overview that references all category rules:

```markdown
---
description: "Azure Cosmos DB: overview rule for data modeling, SDK patterns, query optimization, and operational best practices"
globs:
  - "**/*.{cs,ts,js,py,java,json}"
alwaysApply: false
---

# Azure Cosmos DB Best Practices

Use the rules in this folder for focused guidance while working with Azure Cosmos DB.

## <Section name>

- `<name>.mdc`

(repeat for each category)
```

### After generation

1. Delete any `rules/*/RULE.md` files for categories that no longer have source files
2. Add auto-generated markers to top of each RULE.md: `<!-- Auto-generated from cosmosdb-agent-kit — run .cursor/prompts/generate-rules.md to regenerate -->`
3. List what changed (new rules added, rules updated, rules removed)
