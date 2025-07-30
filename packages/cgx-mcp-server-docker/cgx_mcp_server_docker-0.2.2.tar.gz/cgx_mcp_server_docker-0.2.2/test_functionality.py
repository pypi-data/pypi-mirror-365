#!/usr/bin/env python3
"""
Test script to verify the MCP Docker Server functionality.
This script validates that the server can be imported and basic functionality works.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all modules can be imported successfully."""
    print("Testing imports...")
    try:
        import mcp_server_docker
        print("✓ Main module imported successfully")
        
        from mcp_server_docker import main
        print("✓ Main function imported successfully")
        
        from mcp_server_docker.settings import ServerSettings
        print("✓ Settings module imported successfully")
        
        from mcp_server_docker.server import app
        print("✓ Server module imported successfully")
        
        from mcp_server_docker.http_server import run_http
        print("✓ HTTP server module imported successfully")
        
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_settings():
    """Test that settings can be loaded."""
    print("\nTesting settings...")
    try:
        from mcp_server_docker.settings import ServerSettings
        settings = ServerSettings()
        print(f"✓ Settings loaded: {type(settings).__name__}")
        return True
    except Exception as e:
        print(f"✗ Settings test failed: {e}")
        return False

def test_docker_connection():
    """Test Docker connection (if Docker is available)."""
    print("\nTesting Docker connection...")
    try:
        import docker
        client = docker.from_env()
        client.ping()
        print("✓ Docker connection successful")
        return True
    except Exception as e:
        print(f"⚠ Docker connection failed (this is OK if Docker is not running): {e}")
        return False  # This is not a failure since Docker might not be available

def main():
    """Run all tests."""
    print("=== MCP Docker Server Test Suite ===\n")
    
    all_passed = True
    
    # Test imports
    if not test_imports():
        all_passed = False
    
    # Test settings
    if not test_settings():
        all_passed = False
    
    # Test Docker (optional)
    test_docker_connection()
    
    print("\n=== Test Results ===")
    if all_passed:
        print("✓ All critical tests passed! The server is ready for deployment.")
        return 0
    else:
        print("✗ Some tests failed. Please fix the issues before deployment.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
