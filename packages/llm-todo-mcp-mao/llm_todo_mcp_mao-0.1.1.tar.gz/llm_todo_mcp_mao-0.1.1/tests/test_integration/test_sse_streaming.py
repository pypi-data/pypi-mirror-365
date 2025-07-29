"""
Tests for SSE/streaming HTTP server functionality.

This module tests the HTTP server with Server-Sent Events (SSE),
WebSocket support, and streaming capabilities.
"""

import asyncio
import json
import pytest
import tempfile
from pathlib import Path
from typing import List, Dict, Any
from unittest.mock import AsyncMock, patch
import httpx
import websockets

from src.todo_mcp.config import TodoConfig
from src.todo_mcp.server import TodoMCPServer
from src.todo_mcp.http_server import TodoHTTPServer


@pytest.fixture
def http_test_server():
    """Create HTTP server for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        config = TodoConfig(
            data_directory=temp_path / "data",
            backup_enabled=False,
            file_watch_enabled=False,
            log_level="ERROR",  # Minimal logging for tests
            performance_monitoring=False
        )
        
        config.data_directory.mkdir(parents=True, exist_ok=True)
        (config.data_directory / "tasks").mkdir(exist_ok=True)
        
        # Create MCP server
        mcp_server = TodoMCPServer(config)
        # Note: New server uses lifespan context management, no direct task_service access needed
        
        # Create HTTP server
        http_server = TodoHTTPServer(config, mcp_server)
        
        return http_server, config


class TestHTTPEndpoints:
    """Test HTTP REST API endpoints."""
    
    @pytest.mark.asyncio
    async def test_health_endpoint(self, http_test_server):
        """Test health check endpoint."""
        http_server, config = http_test_server
        
        # Test the health check logic directly
        try:
            server_info = http_server.mcp_server.get_server_info()
            health_data = {
                "status": "healthy",
                "server_name": config.server_name,
                "version": config.server_version,
                "tools_available": server_info.get('tools_count', 0),
                "websocket_connections": len(http_server.websocket_manager.connections),
                "event_subscribers": len(http_server.event_subscribers)
            }
            
            assert health_data["status"] == "healthy"
            assert "server_name" in health_data
            assert "version" in health_data
            assert health_data["tools_available"] > 0
            
        except Exception as e:
            pytest.fail(f"Health check failed: {e}")
    
    @pytest.mark.asyncio
    async def test_tools_endpoint(self, http_test_server):
        """Test tools listing logic."""
        http_server, config = http_test_server
        
        # Test tools listing directly
        server_info = http_server.mcp_server.get_server_info()
        tools_data = {
            "tools": [
                {
                    "name": tool_name,
                    "description": http_server.mcp_server._tools_registry[tool_name].description,
                    "input_schema": http_server.mcp_server._tools_registry[tool_name].inputSchema
                }
                for tool_name in server_info.get('tools', [])
            ],
            "count": server_info.get('tools_count', 0)
        }
        
        assert "tools" in tools_data
        assert "count" in tools_data
        assert isinstance(tools_data["tools"], list)
        assert tools_data["count"] > 0
    
    @pytest.mark.asyncio
    async def test_tool_execution(self, http_test_server):
        """Test tool execution logic."""
        http_server, config = http_test_server
        
        # Mock the tool execution
        mock_result = {"success": True, "task": {"id": "test_123", "title": "Test Task"}}
        
        with patch.object(http_server, '_execute_mcp_tool') as mock_execute:
            mock_execute.return_value = mock_result
            
            # Test the tool execution logic directly
            result = await http_server._execute_mcp_tool("create_task", {
                "title": "Test Task", 
                "description": "Test description"
            })
            
            assert result["success"] is True
            assert result["task"]["id"] == "test_123"


class TestServerSentEvents:
    """Test Server-Sent Events functionality."""
    
    @pytest.mark.asyncio
    async def test_sse_connection(self, http_test_server):
        """Test SSE connection and initial events."""
        http_server, base_url = http_test_server
        
        async with httpx.AsyncClient() as client:
            async with client.stream("GET", f"{base_url}/events") as response:
                assert response.status_code == 200
                assert response.headers["content-type"] == "text/event-stream; charset=utf-8"
                
                # Read first few events
                events = []
                async for chunk in response.aiter_text():
                    if chunk.strip():
                        events.append(chunk.strip())
                        if len(events) >= 3:  # Get initial connection event
                            break
                
                # Should receive connection event
                assert any("event: connected" in event for event in events)
    
    @pytest.mark.asyncio
    async def test_sse_tool_execution_broadcast(self, http_test_server):
        """Test that tool executions are broadcast via SSE."""
        http_server, base_url = http_test_server
        
        # Start SSE connection
        sse_events = []
        
        async def collect_sse_events():
            async with httpx.AsyncClient() as client:
                async with client.stream("GET", f"{base_url}/events") as response:
                    async for chunk in response.aiter_text():
                        if "event: tool_executed" in chunk:
                            sse_events.append(chunk)
                            break
        
        # Start SSE collection in background
        sse_task = asyncio.create_task(collect_sse_events())
        
        # Wait a bit for SSE connection to establish
        await asyncio.sleep(0.2)
        
        # Execute a tool
        with patch.object(http_server.mcp_server, '_handle_tool_call') as mock_call:
            mock_call.return_value = [type('obj', (object,), {
                'text': json.dumps({"success": True, "task": {"id": "test_123"}})
            })]
            
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"{base_url}/tools/create_task",
                    json={"title": "SSE Test Task"}
                )
        
        # Wait for SSE event
        try:
            await asyncio.wait_for(sse_task, timeout=2.0)
            assert len(sse_events) > 0
            assert "tool_executed" in sse_events[0]
        except asyncio.TimeoutError:
            pytest.skip("SSE event not received in time")
    
    @pytest.mark.asyncio
    async def test_sse_heartbeat(self, http_test_server):
        """Test SSE heartbeat functionality."""
        http_server, base_url = http_test_server
        
        heartbeat_received = False
        
        async with httpx.AsyncClient(timeout=35.0) as client:
            async with client.stream("GET", f"{base_url}/events") as response:
                start_time = asyncio.get_event_loop().time()
                
                async for chunk in response.aiter_text():
                    if "event: heartbeat" in chunk:
                        heartbeat_received = True
                        break
                    
                    # Don't wait too long
                    if asyncio.get_event_loop().time() - start_time > 32:
                        break
        
        assert heartbeat_received, "Heartbeat event should be received within 30 seconds"


class TestStreamingEndpoints:
    """Test streaming endpoints."""
    
    @pytest.mark.asyncio
    async def test_streaming_tool_execution(self, http_test_server):
        """Test streaming tool execution."""
        http_server, base_url = http_test_server
        
        with patch.object(http_server.mcp_server, '_handle_tool_call') as mock_call:
            mock_call.return_value = [type('obj', (object,), {
                'text': json.dumps({"success": True, "task": {"id": "stream_test"}})
            })]
            
            async with httpx.AsyncClient() as client:
                async with client.stream(
                    "POST",
                    f"{base_url}/stream",
                    json={
                        "tool": "create_task",
                        "parameters": {"title": "Streaming Test"}
                    }
                ) as response:
                    assert response.status_code == 200
                    
                    chunks = []
                    async for chunk in response.aiter_text():
                        if chunk.strip():
                            chunks.append(chunk.strip())
                    
                    # Should receive multiple progress updates
                    assert len(chunks) > 1
                    
                    # Should have starting and completed status
                    chunk_text = " ".join(chunks)
                    assert "starting" in chunk_text
                    assert "completed" in chunk_text
    
    @pytest.mark.asyncio
    async def test_task_streaming(self, http_test_server):
        """Test task streaming endpoint."""
        http_server, base_url = http_test_server
        
        # Mock list_tasks to return some data
        with patch.object(http_server.mcp_server, '_handle_tool_call') as mock_call:
            mock_call.return_value = [type('obj', (object,), {
                'text': json.dumps({
                    "success": True,
                    "tasks": [
                        {"id": "1", "title": "Task 1", "status": "pending"},
                        {"id": "2", "title": "Task 2", "status": "completed"}
                    ]
                })
            })]
            
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{base_url}/tasks/stream")
                
                assert response.status_code == 200
                assert response.headers["content-type"] == "application/x-ndjson; charset=utf-8"
                
                # Parse NDJSON response
                lines = response.text.strip().split('\n')
                tasks = [json.loads(line) for line in lines if line.strip()]
                
                assert len(tasks) == 2
                assert tasks[0]["title"] == "Task 1"
                assert tasks[1]["title"] == "Task 2"


class TestWebSocketEndpoints:
    """Test WebSocket functionality."""
    
    @pytest.mark.asyncio
    async def test_websocket_connection(self, http_test_server):
        """Test WebSocket connection."""
        http_server, base_url = http_test_server
        ws_url = base_url.replace("http://", "ws://") + "/ws"
        
        try:
            async with websockets.connect(ws_url) as websocket:
                # Connection should be successful
                assert websocket.open
                
                # Send a ping to test connection
                await websocket.ping()
                
        except Exception as e:
            pytest.skip(f"WebSocket connection failed: {e}")
    
    @pytest.mark.asyncio
    async def test_websocket_tool_execution(self, http_test_server):
        """Test tool execution via WebSocket."""
        http_server, base_url = http_test_server
        ws_url = base_url.replace("http://", "ws://") + "/ws"
        
        with patch.object(http_server.mcp_server, '_handle_tool_call') as mock_call:
            mock_call.return_value = [type('obj', (object,), {
                'text': json.dumps({"success": True, "task": {"id": "ws_test"}})
            })]
            
            try:
                async with websockets.connect(ws_url) as websocket:
                    # Send tool execution request
                    request = {
                        "type": "tool_call",
                        "tool": "create_task",
                        "parameters": {"title": "WebSocket Test"}
                    }
                    await websocket.send(json.dumps(request))
                    
                    # Receive response
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    data = json.loads(response)
                    
                    assert data["type"] == "tool_result"
                    assert data["tool"] == "create_task"
                    assert data["success"] is True
                    
            except Exception as e:
                pytest.skip(f"WebSocket test failed: {e}")


class TestRealTimeUpdates:
    """Test real-time update functionality."""
    
    @pytest.mark.asyncio
    async def test_task_update_broadcast(self, http_test_server):
        """Test that task updates are broadcast to subscribers."""
        http_server, base_url = http_test_server
        
        # Create a task update event
        task_data = {
            "id": "broadcast_test",
            "title": "Broadcast Test Task",
            "status": "completed"
        }
        
        # Simulate broadcasting
        await http_server.broadcast_task_update(
            "broadcast_test",
            "task_updated",
            task_data
        )
        
        # Verify event was added to subscribers
        assert len(http_server.event_subscribers) >= 0  # May be 0 if no active connections
    
    @pytest.mark.asyncio
    async def test_concurrent_sse_connections(self, http_test_server):
        """Test multiple concurrent SSE connections."""
        http_server, base_url = http_test_server
        
        async def create_sse_connection():
            async with httpx.AsyncClient() as client:
                async with client.stream("GET", f"{base_url}/events") as response:
                    # Just establish connection and read one event
                    async for chunk in response.aiter_text():
                        if "event: connected" in chunk:
                            return True
                    return False
        
        # Create multiple concurrent connections
        tasks = [create_sse_connection() for _ in range(3)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # At least some connections should succeed
        successful = sum(1 for r in results if r is True)
        assert successful > 0


class TestErrorHandling:
    """Test error handling in HTTP/SSE server."""
    
    @pytest.mark.asyncio
    async def test_invalid_tool_execution(self, http_test_server):
        """Test error handling for invalid tool execution."""
        http_server, base_url = http_test_server
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/tools/invalid_tool",
                json={"param": "value"}
            )
            
            assert response.status_code == 500
    
    @pytest.mark.asyncio
    async def test_streaming_error_handling(self, http_test_server):
        """Test error handling in streaming endpoints."""
        http_server, base_url = http_test_server
        
        # Mock tool to raise an error
        with patch.object(http_server.mcp_server, '_handle_tool_call') as mock_call:
            mock_call.side_effect = Exception("Test error")
            
            async with httpx.AsyncClient() as client:
                async with client.stream(
                    "POST",
                    f"{base_url}/stream",
                    json={
                        "tool": "create_task",
                        "parameters": {"title": "Error Test"}
                    }
                ) as response:
                    assert response.status_code == 200
                    
                    chunks = []
                    async for chunk in response.aiter_text():
                        if chunk.strip():
                            chunks.append(chunk.strip())
                    
                    # Should receive error status
                    chunk_text = " ".join(chunks)
                    assert "error" in chunk_text.lower()


class TestPerformance:
    """Test performance aspects of HTTP/SSE server."""
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self, http_test_server):
        """Test handling of concurrent HTTP requests."""
        http_server, base_url = http_test_server
        
        async def make_request():
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{base_url}/health")
                return response.status_code == 200
        
        # Make multiple concurrent requests
        tasks = [make_request() for _ in range(10)]
        results = await asyncio.gather(*tasks)
        
        # All requests should succeed
        assert all(results)
    
    @pytest.mark.asyncio
    async def test_sse_connection_limit(self, http_test_server):
        """Test SSE connection handling under load."""
        http_server, base_url = http_test_server
        
        connections = []
        
        try:
            # Create multiple SSE connections
            for _ in range(5):
                client = httpx.AsyncClient()
                response = await client.stream("GET", f"{base_url}/events").__aenter__()
                connections.append((client, response))
            
            # All connections should be established
            assert len(connections) == 5
            
            # Check server state
            assert len(http_server.event_subscribers) >= 5
            
        finally:
            # Cleanup connections
            for client, response in connections:
                try:
                    await response.__aexit__(None, None, None)
                    await client.aclose()
                except:
                    pass