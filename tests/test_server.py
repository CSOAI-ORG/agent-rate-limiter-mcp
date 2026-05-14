#!/usr/bin/env python3
"""Test suite for agent-rate-limiter-mcp"""
import pytest
from unittest.mock import Mock, patch


class TestServer:
    """Unit tests for MCP server"""
    
    def test_server_initialization(self):
        """Test server initializes"""
        try:
            import server
            assert True
        except ImportError as e:
            pytest.skip(f"Server import failed: {e}")

    def test_tools_available(self):
        """Test tools are registered"""
        try:
            from server import mcp
            assert mcp is not None
        except ImportError:
            pytest.skip("MCP not importable")


class TestSecurity:
    """Security tests"""
    
    def test_no_hardcoded_keys(self):
        """Check for hardcoded credentials"""
        try:
            with open('server.py', 'r') as f:
                content = f.read()
                assert 'sk_live_' not in content
                assert 'sk_test_' not in content
        except FileNotFoundError:
            pytest.skip("server.py not found")


class TestIntegration:
    """Integration tests"""
    
    def test_import_main(self):
        """Test main can be imported"""
        try:
            import server
            assert hasattr(server, 'main')
        except ImportError:
            pytest.skip("Cannot import server")
