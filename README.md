<h1 align="center">MCP-Mem0: Long-Term Memory for AI Agents</h1>

<p align="center">
  <img src="public/Mem0AndMCP.png" alt="Mem0 and MCP Integration" width="600">
</p>

A template implementation of the [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server integrated with [Mem0](https://mem0.ai) for providing AI agents with persistent memory capabilities.

Use this as a reference point to build your MCP servers yourself, or give this as an example to an AI coding assistant and tell it to follow this example for structure and code correctness!

## Overview

This project demonstrates how to build an MCP server that enables AI agents to store, retrieve, and search memories using semantic search. It serves as a practical template for creating your own MCP servers, simply using Mem0 and a practical example.

The implementation follows the best practices laid out by Anthropic for building MCP servers, allowing seamless integration with any MCP-compatible client.

## Features

The server provides three essential memory management tools:

1. **`save_memory`**: Store any information in long-term memory with semantic indexing
2. **`get_all_memories`**: Retrieve all stored memories for comprehensive context
3. **`search_memories`**: Find relevant memories using semantic search

## Prerequisites

- Python 3.12+
- Vector store: Either Qdrant or Supabase/PostgreSQL (for vector storage of memories)
- API keys for your chosen LLM provider (OpenAI, OpenRouter, or Ollama)
- Docker if running the MCP server as a container (recommended)
- (Optional) Neo4j database for graph-based memory storage

## Installation

### Using uv

1. Install uv if you don't have it:
   ```bash
   pip install uv
   ```

2. Clone this repository:
   ```bash
   git clone https://github.com/coleam00/mcp-mem0.git
   cd mcp-mem0
   ```

3. Install dependencies:
   ```bash
   uv pip install -e .
   ```

4. Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   ```

5. Configure your environment variables in the `.env` file (see Configuration section)

### Using Docker (Recommended)

> **Note**: The Docker configuration has not been updated for Neo4j graph store support. If you need Docker with Neo4j, you'll need to update the Dockerfile accordingly.

1. Build the Docker image:
   ```bash
   docker build -t mcp/mem0 --build-arg PORT=8050 .
   ```

2. Create a `.env` file based on `.env.example` and configure your environment variables

## Configuration

The following environment variables can be configured in your `.env` file:

| Variable | Description | Example |
|----------|-------------|----------|
| `TRANSPORT` | Transport protocol (sse or stdio) | `sse` |
| `HOST` | Host to bind to when using SSE transport | `0.0.0.0` |
| `PORT` | Port to listen on when using SSE transport | `8050` |
| `LLM_PROVIDER` | LLM provider (openai, openrouter, or ollama) | `openai` |
| `LLM_BASE_URL` | Base URL for the LLM API | `https://api.openai.com/v1` |
| `LLM_API_KEY` | API key for the LLM provider | `sk-...` |
| `LLM_CHOICE` | LLM model to use | `gpt-4o-mini` |
| `EMBEDDING_MODEL_CHOICE` | Embedding model to use | `text-embedding-3-small` |
| `VECTOR_STORE_PROVIDER` | Vector store to use (qdrant or supabase) | `supabase` |
| `QDRANT_HOST` | Qdrant host (if using Qdrant) | `localhost` |
| `QDRANT_PORT` | Qdrant port (if using Qdrant) | `6333` |
| `QDRANT_COLLECTION` | Qdrant collection name | `mem0_memories` |
| `QDRANT_API_KEY` | Qdrant API key (for cloud) | `your-api-key` |
| `DATABASE_URL` | PostgreSQL connection string (if using Supabase) | `postgresql://user:pass@host:port/db` |
| `NEO4J_URL` | Neo4j connection URL (optional) | `bolt://localhost:7687` |
| `NEO4J_USERNAME` | Neo4j username (optional) | `neo4j` |
| `NEO4J_PASSWORD` | Neo4j password (optional) | `password` |

### Vector Store Configuration

This server supports two vector store options:

#### Qdrant (Recommended for local development)
- Set `VECTOR_STORE_PROVIDER=qdrant` in your `.env` file
- Run Qdrant locally with Docker: `docker run -p 6333:6333 qdrant/qdrant`
- Or use Qdrant Cloud with `QDRANT_API_KEY`

#### Supabase/PostgreSQL
- Leave `VECTOR_STORE_PROVIDER` empty or set to `supabase`
- Configure `DATABASE_URL` with your PostgreSQL connection string
- Works with Supabase or any PostgreSQL database with pgvector extension

### Graph Store Support (Optional)

This server now supports Neo4j as a graph store in addition to the vector store. When Neo4j credentials are provided, Mem0 will:

- Store memories in both vector and graph databases simultaneously
- Extract entities and relationships from conversations
- Enable more sophisticated memory retrieval using graph traversal

To enable graph store support:

1. Set up a Neo4j instance (local or cloud-based like Neo4j AuraDB)
2. Configure the Neo4j environment variables in your `.env` file
3. The server will automatically detect and use Neo4j when credentials are provided

Note: If Neo4j credentials are not provided, the server will function normally using only the vector store.

## Running the Server

### Using uv

#### SSE Transport

```bash
# Set TRANSPORT=sse in .env then:
uv run src/main.py
```

The MCP server will essentially be run as an API endpoint that you can then connect to with config shown below.

#### Stdio Transport

With stdio, the MCP client iself can spin up the MCP server, so nothing to run at this point.

### Using Docker

#### SSE Transport

```bash
docker run --env-file .env -p:8050:8050 mcp/mem0
```

The MCP server will essentially be run as an API endpoint within the container that you can then connect to with config shown below.

#### Stdio Transport

With stdio, the MCP client iself can spin up the MCP server container, so nothing to run at this point.

## Integration with MCP Clients

### SSE Configuration

Once you have the server running with SSE transport, you can connect to it using this configuration:

```json
{
  "mcpServers": {
    "mem0": {
      "transport": "sse",
      "url": "http://localhost:8050/sse"
    }
  }
}
```

> **Note for Windsurf users**: Use `serverUrl` instead of `url` in your configuration:
> ```json
> {
>   "mcpServers": {
>     "mem0": {
>       "transport": "sse",
>       "serverUrl": "http://localhost:8050/sse"
>     }
>   }
> }
> ```

> **Note for n8n users**: Use host.docker.internal instead of localhost since n8n has to reach outside of it's own container to the host machine:
> 
> So the full URL in the MCP node would be: http://host.docker.internal:8050/sse

Make sure to update the port if you are using a value other than the default 8050.

### Python with Stdio Configuration

Add this server to your MCP configuration for Claude Desktop, Windsurf, or any other MCP client:

```json
{
  "mcpServers": {
    "mem0": {
      "command": "your/path/to/mcp-mem0/.venv/Scripts/python.exe",
      "args": ["your/path/to/mcp-mem0/src/main.py"],
      "env": {
        "TRANSPORT": "stdio",
        "LLM_PROVIDER": "openai",
        "LLM_BASE_URL": "https://api.openai.com/v1",
        "LLM_API_KEY": "YOUR-API-KEY",
        "LLM_CHOICE": "gpt-4o-mini",
        "EMBEDDING_MODEL_CHOICE": "text-embedding-3-small",
        "DATABASE_URL": "YOUR-DATABASE-URL",
        "NEO4J_URL": "bolt://localhost:7687",
        "NEO4J_USERNAME": "neo4j",
        "NEO4J_PASSWORD": "YOUR-NEO4J-PASSWORD"
      }
    }
  }
}
```

### Docker with Stdio Configuration

```json
{
  "mcpServers": {
    "mem0": {
      "command": "docker",
      "args": ["run", "--rm", "-i", 
               "-e", "TRANSPORT", 
               "-e", "LLM_PROVIDER", 
               "-e", "LLM_BASE_URL", 
               "-e", "LLM_API_KEY", 
               "-e", "LLM_CHOICE", 
               "-e", "EMBEDDING_MODEL_CHOICE", 
               "-e", "DATABASE_URL",
               "-e", "NEO4J_URL",
               "-e", "NEO4J_USERNAME", 
               "-e", "NEO4J_PASSWORD",
               "mcp/mem0"],
      "env": {
        "TRANSPORT": "stdio",
        "LLM_PROVIDER": "openai",
        "LLM_BASE_URL": "https://api.openai.com/v1",
        "LLM_API_KEY": "YOUR-API-KEY",
        "LLM_CHOICE": "gpt-4o-mini",
        "EMBEDDING_MODEL_CHOICE": "text-embedding-3-small",
        "DATABASE_URL": "YOUR-DATABASE-URL",
        "NEO4J_URL": "bolt://localhost:7687",
        "NEO4J_USERNAME": "neo4j",
        "NEO4J_PASSWORD": "YOUR-NEO4J-PASSWORD"
      }
    }
  }
}
```

## Building Your Own Server

This template provides a foundation for building more complex MCP servers. To build your own:

1. Add your own tools by creating methods with the `@mcp.tool()` decorator
2. Create your own lifespan function to add your own dependencies (clients, database connections, etc.)
3. Modify the `utils.py` file for any helper functions you need for your MCP server
4. Feel free to add prompts and resources as well  with `@mcp.resource()` and `@mcp.prompt()`
