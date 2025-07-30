#!/usr/bin/env python3
"""Test script to validate MCP Docker Server functionality."""

import asyncio
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import docker
from mcp_server_docker.settings import ServerSettings
from mcp_server_docker.http_server import run_http

async def test_http_server():
    """Test the HTTP server functionality."""
    print("Testing MCP Docker Server...")
    
    try:
        # Initialize settings and Docker client
        settings = ServerSettings()
        print(f"Settings loaded: {settings}")
        
        # Test Docker client connection
        docker_client = docker.from_env()
        print(f"Docker client created: {docker_client}")
        
        # Test docker connection
        docker_client.ping()
        print("Docker connection successful!")
        
        print("Starting HTTP server on port 8081...")
        print("Press Ctrl+C to stop the server")
        
        # Start the HTTP server
        await run_http(settings, docker_client, host="127.0.0.1", port=8081)
        
    except docker.errors.DockerException as e:
        print(f"Docker error: {e}")
        print("Make sure Docker is running and accessible")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_http_server())
