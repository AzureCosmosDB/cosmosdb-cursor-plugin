# Azure Cosmos DB Plugin for Cursor

The Azure Cosmos DB plugin for [Cursor](https://cursor.com/) gives Cursor the tools and skills needed to work effectively with Azure Cosmos DB projects.

## What's Included

- **MCP Server** — Connection to the [Azure Cosmos DB MCP Toolkit](https://github.com/AzureCosmosDB/MCPToolKit) for database operations, queries, vector search, and schema discovery
- **Skills** — Agent skills for Cosmos DB best practices:
  - `cosmosdb-nosql-best-practices` — Query optimization, SDK usage, indexing, throughput management
  - `cosmosdb-data-modeling` — Embedding vs. referencing, multi-tenant patterns, container design
- **Rules** — Coding rules for Cosmos DB SDK patterns and data modeling conventions

## MCP Tools Available

Once connected to the MCP Toolkit, the following tools are available:

| Tool | Description |
|------|-------------|
| `list_databases` | List all databases in the Cosmos DB account |
| `list_collections` | List all containers in a database |
| `get_approximate_schema` | Sample documents to infer schema (top-level properties) |
| `get_recent_documents` | Get N most recent documents ordered by timestamp |
| `find_document_by_id` | Find a document by its id |
| `text_search` | Search for documents where a property contains a search phrase |
| `vector_search` | Perform vector search using Azure OpenAI embeddings |

## Prerequisites

To use the MCP server features, you need:

1. **Azure Cosmos DB account** — [Create one](https://learn.microsoft.com/azure/cosmos-db/nosql/quickstart-portal)
2. **Deployed MCP Toolkit** — Follow the [MCPToolKit deployment guide](https://github.com/AzureCosmosDB/MCPToolKit#quick-start)
3. **JWT Bearer Token** — For authentication (see setup below)

The **skills and rules work without any setup** — they provide best practices guidance regardless of MCP server configuration.

## Setup

### Step 1: Deploy the MCP Toolkit

Follow the [Azure Cosmos DB MCP Toolkit Quick Start](https://github.com/AzureCosmosDB/MCPToolKit#quick-start):

```bash
git clone https://github.com/AzureCosmosDB/MCPToolKit.git
cd MCPToolKit

# Deploy infrastructure (choose one method)
# Option A: Deploy to Azure button in the MCPToolKit README
# Option B: Azure Developer CLI
azd up

# Deploy the MCP server application
.\scripts\Deploy-Cosmos-MCP-Toolkit.ps1 -ResourceGroup "YOUR-RESOURCE-GROUP"
```

### Step 2: Configure Environment Variables

After the plugin is installed, set these environment variables so the MCP server can connect:

```bash
# Your deployed MCP Toolkit URL (from deployment-info.json)
COSMOSDB_MCP_SERVER_URL=https://YOUR-CONTAINER-APP.azurecontainerapps.io

# JWT token for authentication
COSMOSDB_MCP_JWT_TOKEN=<your-bearer-token>
```

#### Getting Your JWT Token

```bash
# Login to Azure
az login

# Get the Entra App Client ID (from deployment-info.json)
az account get-access-token --resource YOUR-ENTRA-APP-CLIENT-ID --query accessToken -o tsv
```

> **Note**: JWT tokens expire after ~1 hour. Refresh by re-running the command above.

### Step 3: Verify

In Cursor, open a chat and try:
```
List all databases in my Cosmos DB account
```

## Project Structure

```
cosmosdb-cursor-plugin/
├── .cursor-plugin/
│   └── plugin.json          # Plugin manifest
├── .mcp.json                # MCP server configuration
├── assets/
│   └── logo.svg             # Plugin logo
├── rules/
│   ├── cosmosdb-sdk-patterns.mdc
│   └── cosmosdb-data-modeling.mdc
├── skills/
│   ├── cosmosdb-nosql-best-practices/
│   │   └── SKILL.md
│   └── cosmosdb-data-modeling/
│       └── SKILL.md
├── LICENSE
└── README.md
```

## Usage Examples

### With MCP Server (requires deployment)

- "List all databases in my Cosmos DB account"
- "Show me the schema of the `users` container in the `mydb` database"
- "Get the latest 10 documents from the `orders` container"
- "Search for documents where the name contains 'Azure'"
- "Find the document with id 'user-001' in the `users` container"

### With Skills (no setup needed)

- "Review my Cosmos DB data model for this application"
- "What partition key should I use for a multi-tenant SaaS app?"
- "Optimize this Cosmos DB query for lower RU cost"
- "Should I embed or reference this related data?"

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m 'feat: add my feature'`
4. Push to the branch: `git push origin feature/my-feature`
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
