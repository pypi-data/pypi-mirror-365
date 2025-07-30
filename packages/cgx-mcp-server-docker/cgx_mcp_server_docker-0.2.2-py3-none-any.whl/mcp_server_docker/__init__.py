import asyncio  
import argparse  
import docker  
from .settings import ServerSettings  
from .server import run_stdio  
from .http_server import run_http  
  
def main():  
    """Main entry point supporting both stdio and HTTP transports."""  
    parser = argparse.ArgumentParser(description="MCP Docker Server")  
    parser.add_argument(  
        "--transport",   
        choices=["stdio", "http"],   
        default="stdio",  
        help="Transport method (default: stdio)"  
    )  
    parser.add_argument(  
        "--host",   
        default="0.0.0.0",  
        help="Host to bind HTTP server (default: 0.0.0.0)"  
    )  
    parser.add_argument(  
        "--port",   
        type=int,   
        default=8080,  
        help="Port for HTTP server (default: 8080)"  
    )  
      
    args = parser.parse_args()  
      
    # Initialize settings and Docker client  
    settings = ServerSettings()  
    docker_client = docker.from_env()  
      
    # Run appropriate transport  
    if args.transport == "http":  
        asyncio.run(run_http(settings, docker_client, args.host, args.port))  
    else:  
        asyncio.run(run_stdio(settings, docker_client))  
  
if __name__ == "__main__":  
    main()

# Optionally expose other important items at package level
__all__ = ["main", "run_stdio", "run_http", "ServerSettings"]

