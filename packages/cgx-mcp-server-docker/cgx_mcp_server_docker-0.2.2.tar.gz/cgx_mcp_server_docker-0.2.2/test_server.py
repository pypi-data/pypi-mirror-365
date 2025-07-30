#!/usr/bin/env python3
"""Simple test script for the MCP Docker Server HTTP mode."""

import sys
from mcp_server_docker import main

def test_main():
    """Test the HTTP server startup."""
    try:
        # Override sys.argv to simulate command line arguments
        sys.argv = ['test', '--transport', 'http', '--port', '8081']
        main()
    except KeyboardInterrupt:
        print("Server stopped by user")
    except Exception as e:
        print(f"Error starting server: {e}")

if __name__ == "__main__":
    test_main()
