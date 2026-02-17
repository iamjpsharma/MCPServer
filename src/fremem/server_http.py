import logging
import os
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from mcp.server.sse import SseServerTransport
from fremem.server import server

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fremem-http")

# The transport needs to know the endpoint where clients should send messages.
# In a real deployment, this might need to be a full URL or absolute path.
# For local use, "/messages" is usually sufficient if the client resolves it relative to the connection.
transport = SseServerTransport("/messages")

async def handle_sse(scope, receive, send):
    """
    Handle incoming SSE connections.
    """
    logger.info("New SSE connection")
    async with transport.connect_sse(scope, receive, send) as streams:
        read_stream, write_stream = streams
        # Run the server with the streams from this connection
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

async def handle_messages(scope, receive, send):
    """
    Handle incoming messages (JSON-RPC via HTTP POST).
    """
    await transport.handle_post_message(scope, receive, send)

routes = [
    Mount("/sse", app=handle_sse),
    Mount("/messages", app=handle_messages),
]

middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
]

app = Starlette(debug=True, routes=routes, middleware=middleware)

if __name__ == "__main__":
    import uvicorn
    # Allow passing port via env var
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
