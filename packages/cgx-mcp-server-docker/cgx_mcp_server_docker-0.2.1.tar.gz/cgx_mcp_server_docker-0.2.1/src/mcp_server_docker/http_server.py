import asyncio  
import json  
from typing import Any, Dict  
import docker  
from starlette.applications import Starlette  
from starlette.routing import Route  
from starlette.requests import Request  
from starlette.responses import JSONResponse, StreamingResponse  
import uvicorn  
from mcp import types  
from mcp.server import Server  
  
from .server import app as mcp_app  
from .settings import ServerSettings  
  
class MCPHTTPHandler:  
    def __init__(self, docker_client: docker.DockerClient, settings: ServerSettings):  
        self.docker_client = docker_client  
        self.settings = settings  
        # Set global variables for compatibility  
        from . import server  
        server._docker = docker_client  
        server._server_settings = settings  
  
    async def handle_mcp_request(self, request: Request) -> StreamingResponse:  
        """Handle MCP requests over HTTP with streaming response."""  
        try:  
            body = await request.json()  
            method = body.get("method")  
            params = body.get("params", {})  
              
            # Route to appropriate MCP method  
            if method == "initialize":  
                result = await self._handle_initialize(params)  
            elif method == "tools/list":  
                result = await self._handle_list_tools()  
            elif method == "tools/call":  
                result = await self._handle_call_tool(params)  
            elif method == "prompts/list":  
                result = await self._handle_list_prompts()  
            elif method == "prompts/get":  
                result = await self._handle_get_prompt(params)  
            elif method == "resources/list":  
                result = await self._handle_list_resources()  
            elif method == "resources/read":  
                result = await self._handle_read_resource(params)  
            else:  
                result = {"error": f"Unknown method: {method}"}  
              
            # Stream the response  
            async def generate_response():  
                yield json.dumps(result) + "\n"  
              
            return StreamingResponse(  
                generate_response(),  
                media_type="application/json",  
                headers={"Cache-Control": "no-cache"}  
            )  
              
        except Exception as e:  
            return JSONResponse({"error": str(e)}, status_code=500)  
  
    async def _handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:  
        return {  
            "protocolVersion": "2024-11-05",  
            "capabilities": {  
                "tools": {},  
                "prompts": {},  
                "resources": {}  
            },  
            "serverInfo": {  
                "name": "docker-server",  
                "version": "1.0.0"  
            }  
        }  
  
    async def _handle_list_tools(self) -> Dict[str, Any]:  
        tools = await mcp_app._list_tools_impl()  
        return {"tools": [tool.model_dump() for tool in tools]}  
  
    async def _handle_call_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:  
        name = params.get("name")  
        arguments = params.get("arguments", {})  
        result = await mcp_app._call_tool_impl(name, arguments)  
        return {"content": [item.model_dump() for item in result]}  
  
    async def _handle_list_prompts(self) -> Dict[str, Any]:  
        prompts = await mcp_app._list_prompts_impl()  
        return {"prompts": [prompt.model_dump() for prompt in prompts]}  
  
    async def _handle_get_prompt(self, params: Dict[str, Any]) -> Dict[str, Any]:  
        name = params.get("name")  
        arguments = params.get("arguments")  
        result = await mcp_app._get_prompt_impl(name, arguments)  
        return {"messages": [msg.model_dump() for msg in result.messages]}  
  
    async def _handle_list_resources(self) -> Dict[str, Any]:  
        resources = await mcp_app._list_resources_impl()  
        return {"resources": [resource.model_dump() for resource in resources]}  
  
    async def _handle_read_resource(self, params: Dict[str, Any]) -> Dict[str, Any]:  
        uri = params.get("uri")  
        result = await mcp_app._read_resource_impl(uri)  
        return {"contents": [{"uri": uri, "mimeType": "text/plain", "text": result}]}  
  
# Create Starlette app  
async def create_app(docker_client: docker.DockerClient, settings: ServerSettings) -> Starlette:  
    handler = MCPHTTPHandler(docker_client, settings)  
      
    app = Starlette(routes=[  
        Route("/mcp", handler.handle_mcp_request, methods=["POST"])  
    ])  
      
    return app  
  
async def run_http(settings: ServerSettings, docker_client: docker.DockerClient, host: str = "0.0.0.0", port: int = 8080):  
    """Run the server over HTTP with streamable transport at /mcp endpoint."""  
    app = await create_app(docker_client, settings)  
      
    config = uvicorn.Config(  
        app=app,  
        host=host,  
        port=port,  
        log_level="info"  
    )  
    server = uvicorn.Server(config)  
    await server.serve()