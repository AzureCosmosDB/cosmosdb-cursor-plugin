# Generate Cursor Rules from Agent Kit

This prompt regenerates the `rules/` folder (Cursor IDE format) from the source of truth in the [cosmosdb-agent-kit](https://github.com/Azure-Samples/cosmosdb-agent-kit) repo at `skills/cosmosdb-best-practices/rules/`.

Run this prompt in Cursor whenever the agent kit rules are updated.

---

## Instructions

Fetch all markdown files from `https://github.com/Azure-Samples/cosmosdb-agent-kit/tree/main/skills/cosmosdb-best-practices/rules/` (excluding files starting with `_`). Group them by their filename prefix using the mapping below. For each group, generate a `rules/<folder>/RULE.md` file following the Supabase convention.

### Category mapping (filename prefix → folder)

| Prefix | Folder | Description |
|--------|--------|-------------|
| `model-` | `data-modeling` | Document design, embedding, referencing, size limits, schema evolution |
| `partition-` | `partition-key` | Cardinality, hot partitions, hierarchical keys, query alignment |
| `query-` | `query-optimization` | Cross-partition queries, scans, projections, pagination, parameterization |
| `sdk-` | `sdk-patterns` | Singleton client, connection mode, retries, diagnostics, async, concurrency |
| `index-` | `indexing` | Composite indexes, excluded paths, index types, spatial indexes |
| `throughput-` | `throughput` | Autoscale, serverless, burst capacity, right-sizing |
| `global-` | `global-distribution` | Multi-region, consistency levels, failover, conflict resolution |
| `monitoring-` | `monitoring` | RU consumption, latency, throttling, diagnostic logs, Azure Monitor |
| `pattern-` | `design-patterns` | Change feed, materialized views, ranking, multi-tenant patterns |
| `vector-` | `vector-search` | Feature enablement, embedding policies, vector indexes, VectorDistance |

### RULE.md format

Each generated `RULE.md` must follow this exact structure:

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
7. **For `sdk-patterns`**, separate .NET/Java/Python-specific rules into a "Language-specific patterns" section at the end
8. **Add `globs`** appropriate to the content:
   - Rules with code examples: `"**/*.{cs,ts,js,py,java}"`
   - Rules with JSON config (indexing, data-modeling): add `json` to the glob

### Index RULE.md

Also regenerate `rules/RULE.md` as an index that points to all sub-rules:

```markdown
---
description: "Azure Cosmos DB: index rule for data modeling, SDK patterns, query optimization, and operational best practices"
globs:
  - "**/*.{cs,ts,js,py,java,json}"
alwaysApply: false
---

# Azure Cosmos DB Best Practices

Use the nested rules in this folder for focused guidance while working with Azure Cosmos DB.

## <Section name>

- `<folder-name>`

(repeat for each category)
```

### After generation

1. Delete any `rules/*/RULE.md` files for categories that no longer have source files
2. Add auto-generated markers to top of each RULE.md: `<!-- Auto-generated from cosmosdb-agent-kit — run .cursor/prompts/generate-rules.md to regenerate -->`
3. List what changed (new rules added, rules updated, rules removed)
