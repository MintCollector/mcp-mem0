from mcp.server.fastmcp import FastMCP, Context
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass
from dotenv import load_dotenv
from mem0 import Memory
import asyncio
import json
import os

from utils import get_mem0_client

load_dotenv()

# Default user ID for memory operations
DEFAULT_USER_ID = "user"

# Create a dataclass for our application context
@dataclass
class Mem0Context:
    """Context for the Mem0 MCP server."""
    mem0_client: Memory

@asynccontextmanager
async def mem0_lifespan(server: FastMCP) -> AsyncIterator[Mem0Context]:
    """
    Manages the Mem0 client lifecycle.
    
    Args:
        server: The FastMCP server instance
        
    Yields:
        Mem0Context: The context containing the Mem0 client
    """
    # Create and return the Memory client with the helper function in utils.py
    mem0_client = get_mem0_client()
    
    try:
        yield Mem0Context(mem0_client=mem0_client)
    finally:
        # No explicit cleanup needed for the Mem0 client
        pass

# Initialize FastMCP server with the Mem0 client as context
mcp = FastMCP(
    "mcp-mem0",
    description="MCP server for long term memory storage and retrieval with Mem0",
    lifespan=mem0_lifespan,
    host=os.getenv("HOST", "0.0.0.0"),
    port=os.getenv("PORT", "8050")
)        

@mcp.tool()
async def save_memory(ctx: Context, text: str) -> str:
    """Save information to your long-term memory.

    This tool is designed to store any type of information that might be useful in the future.
    The content will be processed and indexed for later retrieval through semantic search.

    Args:
        ctx: The MCP server provided context which includes the Mem0 client
        text: The content to store in memory, including any relevant details and context
    """
    try:
        mem0_client = ctx.request_context.lifespan_context.mem0_client
        messages = [{"role": "user", "content": text}]
        mem0_client.add(messages, user_id=DEFAULT_USER_ID)
        return f"Successfully saved memory: {text[:100]}..." if len(text) > 100 else f"Successfully saved memory: {text}"
    except Exception as e:
        return f"Error saving memory: {str(e)}"

@mcp.tool()
async def get_all_memories(ctx: Context) -> str:
    """Get all stored memories for the user.
    
    Call this tool when you need complete context of all previously memories.

    Args:
        ctx: The MCP server provided context which includes the Mem0 client

    Returns a JSON formatted list of all stored memories, including their IDs, content,
    and creation timestamps. Memory IDs can be used with delete_memory and update_memory tools.
    """
    try:
        mem0_client = ctx.request_context.lifespan_context.mem0_client
        memories = mem0_client.get_all(user_id=DEFAULT_USER_ID)
        
        if isinstance(memories, dict) and "results" in memories:
            # Return full memory objects with IDs for delete/update operations
            formatted_memories = []
            for memory in memories["results"]:
                formatted_memories.append({
                    "id": memory.get("id"),
                    "memory": memory.get("memory"),
                    "created_at": memory.get("created_at"),
                    "updated_at": memory.get("updated_at")
                })
            return json.dumps(formatted_memories, indent=2)
        else:
            return json.dumps(memories, indent=2)
    except Exception as e:
        return f"Error retrieving memories: {str(e)}"

@mcp.tool()
async def search_memories(ctx: Context, query: str, limit: int = 3) -> str:
    """Search memories using semantic search.

    This tool should be called to find relevant information from your memory. Results are ranked by relevance.
    Always search your memories before making decisions to ensure you leverage your existing knowledge.

    Args:
        ctx: The MCP server provided context which includes the Mem0 client
        query: Search query string describing what you're looking for. Can be natural language.
        limit: Maximum number of results to return (default: 3)
    """
    try:
        mem0_client = ctx.request_context.lifespan_context.mem0_client
        memories = mem0_client.search(query, user_id=DEFAULT_USER_ID, limit=limit)
        if isinstance(memories, dict) and "results" in memories:
            flattened_memories = [memory["memory"] for memory in memories["results"]]
        else:
            flattened_memories = memories
        return json.dumps(flattened_memories, indent=2)
    except Exception as e:
        return f"Error searching memories: {str(e)}"

@mcp.tool()
async def delete_memory(ctx: Context, memory_id: str) -> str:
    """Delete a specific memory by its ID.

    Use this tool to remove memories that are no longer relevant or accurate.
    You can get memory IDs from search results or get_all_memories.

    Args:
        ctx: The MCP server provided context which includes the Mem0 client
        memory_id: The unique identifier of the memory to delete
    """
    try:
        mem0_client = ctx.request_context.lifespan_context.mem0_client
        result = mem0_client.delete(memory_id, user_id=DEFAULT_USER_ID)
        return f"Successfully deleted memory with ID: {memory_id}"
    except Exception as e:
        return f"Error deleting memory {memory_id}: {str(e)}"

@mcp.tool()
async def update_memory(ctx: Context, memory_id: str, new_content: str) -> str:
    """Update an existing memory with new content.

    Use this tool to modify or correct existing memories while preserving their ID.
    You can get memory IDs from search results or get_all_memories.

    Args:
        ctx: The MCP server provided context which includes the Mem0 client
        memory_id: The unique identifier of the memory to update
        new_content: The new content to replace the existing memory
    """
    try:
        mem0_client = ctx.request_context.lifespan_context.mem0_client
        result = mem0_client.update(memory_id, new_content, user_id=DEFAULT_USER_ID)
        return f"Successfully updated memory {memory_id} with: {new_content[:100]}..." if len(new_content) > 100 else f"Successfully updated memory {memory_id} with: {new_content}"
    except Exception as e:
        return f"Error updating memory {memory_id}: {str(e)}"

@mcp.tool()
async def find_relationships(ctx: Context, entity: str) -> str:
    """Find all relationships and connections for a specific entity (person, organization, etc.).

    This tool leverages the graph database to discover how entities are connected.
    Use this to understand relationships like who works with whom, what projects people are involved in, etc.

    Args:
        ctx: The MCP server provided context which includes the Mem0 client
        entity: The name of the person, organization, or concept to find relationships for
    """
    try:
        mem0_client = ctx.request_context.lifespan_context.mem0_client
        
        # Search for memories containing the entity
        search_results = mem0_client.search(entity, user_id=DEFAULT_USER_ID, limit=10)
        
        relationships = []
        if isinstance(search_results, dict) and "relations" in search_results:
            # Extract relationships from search results
            relations = search_results.get("relations", [])
            entity_lower = entity.lower().replace(" ", "_")
            
            for relation in relations:
                source = relation.get("source", "")
                relationship = relation.get("relationship", relation.get("relation", ""))
                target = relation.get("destination", relation.get("target", ""))
                
                # Check if the entity is involved in this relationship
                if entity_lower in source.lower() or entity_lower in target.lower():
                    relationships.append({
                        "source": source,
                        "relationship": relationship,
                        "target": target
                    })
        
        if relationships:
            return json.dumps({
                "entity": entity,
                "relationships": relationships,
                "count": len(relationships)
            }, indent=2)
        else:
            # Fallback: search for mentions in memory content
            memories = search_results.get("results", []) if isinstance(search_results, dict) else search_results
            related_memories = []
            
            for memory in memories:
                if isinstance(memory, dict) and "memory" in memory:
                    memory_text = memory["memory"]
                    if entity.lower() in memory_text.lower():
                        related_memories.append(memory_text)
            
            return json.dumps({
                "entity": entity,
                "related_memories": related_memories,
                "note": "No structured relationships found, showing related memories instead"
            }, indent=2)
            
    except Exception as e:
        return f"Error finding relationships for {entity}: {str(e)}"

async def main():
    transport = os.getenv("TRANSPORT", "sse")
    if transport == 'sse':
        # Run the MCP server with sse transport
        await mcp.run_sse_async()
    else:
        # Run the MCP server with stdio transport
        await mcp.run_stdio_async()

if __name__ == "__main__":
    asyncio.run(main())
