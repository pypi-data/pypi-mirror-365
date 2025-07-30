import asyncio  
import contextlib
from typing import AsyncIterator
import docker  
import uvicorn
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager

from .settings import ServerSettings  
  
async def run_http(settings: ServerSettings, docker_client: docker.DockerClient, host: str = "0.0.0.0", port: int = 8080):  
    """Run the server over HTTP using streamable HTTP transport."""  
    # Import and configure the existing server
    from . import server
    
    # Set the global variables  
    server._docker = docker_client
    server._server_settings = settings
    
    print(f"Starting MCP Docker Server with streamable HTTP on http://{host}:{port}")
    print("Server will be available at all endpoints")
    print("Use Ctrl+C to stop the server.")
    
    # Create streamable HTTP session manager with the MCP server
    session_manager = StreamableHTTPSessionManager(server.app)
    
    # Create ASGI application directly without Starlette
    async def app(scope, receive, send):
        # Start the session manager if not already started
        if not hasattr(session_manager, '_task_group') or session_manager._task_group is None:
            async with session_manager.run():
                await session_manager.handle_request(scope, receive, send)
        else:
            await session_manager.handle_request(scope, receive, send)
    
    # Configure and run the uvicorn server  
    config = uvicorn.Config(  
        app=app,  
        host=host,  
        port=port,  
        log_level="info"  
    )  
    uvicorn_server = uvicorn.Server(config)  
    
    # Run the session manager and uvicorn server together
    async with session_manager.run():
        await uvicorn_server.serve()