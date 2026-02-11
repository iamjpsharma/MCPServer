import asyncio
import sys
import traceback
import json
from mcp.server import Server
from mcp.server.stdio import stdio_server
# This is the Windsurf/IDE stdio MCP endpoint
# See README for usage examples
import mcp.types as types
from mcp_memory.db import store

server = Server("mcp-memory")

@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="memory_search",
            description="Search the semantic memory for a specific project using a natural language query.",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Unique identifier for the project scope"
                    },
                    "q": {
                        "type": "string",
                        "description": "The search query"
                    },
                    "k": {
                        "type": "integer",
                        "description": "Number of results to return (default: 5)",
                        "default": 5
                    }
                },
                "required": ["project_id", "q"]
            }
        ),
        types.Tool(
            name="memory_add",
            description="Add a new memory fragment/document to the project's vector store.",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Unique identifier for the project scope"
                    },
                    "id": {
                        "type": "string",
                        "description": "Unique ID for this memory fragment (to support updates)"
                    },
                    "text": {
                        "type": "string",
                        "description": "The text content to verify"
                    },
                    "meta": {
                        "type": "object",
                        "description": "Optional JSON metadata",
                        "additionalProperties": True
                    }
                },
                "required": ["project_id", "id", "text"]
            }
        ),
        types.Tool(
            name="memory_list_sources",
            description="List all files/sources ingested for a project.",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": "Project ID"}
                },
                "required": ["project_id"]
            }
        ),
        types.Tool(
            name="memory_delete_source",
            description="Delete all memories associated with a specific file source.",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string"},
                    "source": {"type": "string", "description": "The exact source (e.g., file path) to delete."}
                },
                "required": ["project_id", "source"]
            }
        ),
        types.Tool(
            name="memory_stats",
            description="Get statistics for a project's memory (chunk count).",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string"}
                },
                "required": ["project_id"]
            }
        ),
        types.Tool(
            name="memory_reset",
            description="Reset (clear) all memories for a project.",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string"}
                },
                "required": ["project_id"]
            }
        )
    ]

@server.list_resources()
async def list_resources() -> list[types.Resource]:
    """List available resources."""
    # Currently no resources are exposed, returning empty list
    return []

@server.read_resource()
async def read_resource(uri: types.AnyUrl) -> str:
    """Read a specific resource."""
    # No resources to read yet
    raise ValueError(f"Resource not found: {uri}")

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    try:
        if name == "memory_search":
            project_id = arguments["project_id"]
            q = arguments["q"]
            k = arguments.get("k", 5)
            
            results = store.search(project_id, q, k)
            
            # Format results for the LLM
            formatted_results = []
            for i, res in enumerate(results):
                formatted_results.append(f"Result {i+1} (Score: {res.get('_distance', 'N/A')}):\n{res['text']}\nMetadata: {json.dumps(res['metadata'])}")
            
            output = "\n\n".join(formatted_results)
            if not output:
                output = "No relevant memories found."
                
            return [types.TextContent(type="text", text=output)]
            
        elif name == "memory_add":
            project_id = arguments["project_id"]
            doc_id = arguments["id"]
            text = arguments["text"]
            meta = arguments.get("meta", {})
            
            store.add(project_id, doc_id, text, meta)
            
            return [types.TextContent(type="text", text=f"Successfully added memory '{doc_id}' to project '{project_id}'")]

        elif name == "memory_list_sources":
            project_id = arguments["project_id"]
            sources = store.list_sources(project_id)
            return [types.TextContent(type="text", text=json.dumps(sources, indent=2))]

        elif name == "memory_delete_source":
            project_id = arguments["project_id"]
            source = arguments["source"]
            success = store.delete_source(project_id, source)
            msg = f"Deleted source '{source}'" if success else f"Failed to delete source '{source}' (not found?)"
            return [types.TextContent(type="text", text=msg)]

        elif name == "memory_stats":
            project_id = arguments["project_id"]
            stats = store.get_stats(project_id)
            return [types.TextContent(type="text", text=json.dumps(stats, indent=2))]

        elif name == "memory_reset":
            project_id = arguments["project_id"]
            success = store.delete_project(project_id)
            msg = f"Reset project '{project_id}'" if success else f"Failed to reset project '{project_id}'"
            return [types.TextContent(type="text", text=msg)]
            
        else:
            raise ValueError(f"Unknown tool: {name}")
            
    except Exception as e:
        # Capture stack trace for debugging via the MCP channel if needed, 
        # but usually returning error text is safer for the LLM flow
        err_msg = f"Error executing {name}: {str(e)}\n{traceback.format_exc()}"
        return [types.TextContent(type="text", text=err_msg)]

async def main():
    # Initialize DB (lazy loading in db.py, but good to prep)
    store.initialize()
    
    # Run stdio server
    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            options
        )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
