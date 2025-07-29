#!/usr/bin/env python3
"""
SSE/Streaming Demo for Todo MCP Server

This script demonstrates the Server-Sent Events (SSE) and streaming
capabilities of the Todo MCP Server.
"""

import asyncio
import json
import httpx
import time
from typing import AsyncGenerator


async def test_sse_connection(base_url: str):
    """Test SSE connection and receive events."""
    print("🔗 Testing SSE connection...")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            async with client.stream("GET", f"{base_url}/events") as response:
                print(f"✅ SSE connected: {response.status_code}")
                print(f"📡 Content-Type: {response.headers.get('content-type')}")
                
                event_count = 0
                async for chunk in response.aiter_text():
                    if chunk.strip():
                        print(f"📨 Event {event_count + 1}: {chunk.strip()}")
                        event_count += 1
                        
                        # Stop after receiving a few events
                        if event_count >= 3:
                            break
                            
    except Exception as e:
        print(f"❌ SSE connection failed: {e}")


async def test_streaming_operation(base_url: str):
    """Test streaming task creation."""
    print("\n🚀 Testing streaming task creation...")
    
    try:
        async with httpx.AsyncClient() as client:
            async with client.stream("POST", f"{base_url}/stream", json={
                "tool": "create_task",
                "parameters": {
                    "title": "Streaming Demo Task",
                    "description": "Task created via streaming API",
                    "priority": "medium",
                    "tags": ["demo", "streaming"]
                }
            }) as response:
                print(f"✅ Streaming started: {response.status_code}")
                
                async for chunk in response.aiter_text():
                    if chunk.strip() and chunk.startswith('data: '):
                        try:
                            data = json.loads(chunk[6:])  # Remove 'data: ' prefix
                            status = data.get('status', 'unknown')
                            
                            if status == 'starting':
                                print(f"🏁 Starting: {data.get('tool')}")
                            elif status == 'processing':
                                progress = data.get('progress', 0)
                                print(f"⏳ Progress: {progress}%")
                            elif status == 'completed':
                                print(f"✅ Completed in {data.get('execution_time', 0):.3f}s")
                                print(f"📋 Result: {data.get('result')}")
                                break
                            elif status == 'error':
                                print(f"❌ Error: {data.get('error')}")
                                break
                                
                        except json.JSONDecodeError:
                            print(f"📝 Raw chunk: {chunk.strip()}")
                            
    except Exception as e:
        print(f"❌ Streaming operation failed: {e}")


async def test_rest_api(base_url: str):
    """Test REST API endpoints."""
    print("\n🌐 Testing REST API endpoints...")
    
    try:
        async with httpx.AsyncClient() as client:
            # Test health endpoint
            response = await client.get(f"{base_url}/health")
            if response.status_code == 200:
                health = response.json()
                print(f"💚 Health: {health['status']}")
                print(f"🔧 Tools available: {health.get('tools_available', 0)}")
            
            # Test tools listing
            response = await client.get(f"{base_url}/tools")
            if response.status_code == 200:
                tools = response.json()
                print(f"🛠️  Available tools: {tools['count']}")
                
                # Show first few tools
                for tool in tools['tools'][:3]:
                    print(f"   - {tool['name']}: {tool['description']}")
            
            # Test task creation via REST
            response = await client.post(f"{base_url}/tools/create_task", json={
                "title": "REST API Demo Task",
                "description": "Task created via REST API",
                "priority": "high",
                "tags": ["demo", "rest"]
            })
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Task created via REST: {result['success']}")
                
    except Exception as e:
        print(f"❌ REST API test failed: {e}")


async def test_websocket_connection(base_url: str):
    """Test WebSocket connection (basic test)."""
    print("\n🔌 Testing WebSocket connection...")
    
    try:
        import websockets
        
        ws_url = base_url.replace("http://", "ws://") + "/ws"
        
        async with websockets.connect(ws_url) as websocket:
            print("✅ WebSocket connected")
            
            # Send a tool execution request
            request = {
                "type": "tool_call",
                "tool": "get_task_statistics",
                "parameters": {}
            }
            
            await websocket.send(json.dumps(request))
            print("📤 Sent tool execution request")
            
            # Wait for response
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            data = json.loads(response)
            
            print(f"📥 Received: {data['type']}")
            if data.get('success'):
                print("✅ WebSocket tool execution successful")
            else:
                print(f"❌ WebSocket tool execution failed: {data.get('error')}")
                
    except ImportError:
        print("⚠️  websockets library not available, skipping WebSocket test")
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")


async def main():
    """Main demo function."""
    base_url = "http://localhost:8000"
    
    print("🎯 Todo MCP Server - SSE/Streaming Demo")
    print("=" * 50)
    print(f"🌐 Server URL: {base_url}")
    print(f"📚 Dashboard: {base_url}/")
    print(f"📖 API Docs: {base_url}/docs")
    print()
    
    # Check if server is running
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/health", timeout=5.0)
            if response.status_code != 200:
                raise Exception(f"Server returned {response.status_code}")
    except Exception as e:
        print(f"❌ Server not accessible at {base_url}")
        print(f"💡 Please start the server with: uv run todo-mcp-server serve-http")
        return
    
    print("✅ Server is running!")
    print()
    
    # Run tests
    await test_rest_api(base_url)
    await test_streaming_operation(base_url)
    await test_sse_connection(base_url)
    await test_websocket_connection(base_url)
    
    print("\n🎉 Demo completed!")
    print(f"🌐 Visit {base_url}/ for the interactive dashboard")


if __name__ == "__main__":
    asyncio.run(main())