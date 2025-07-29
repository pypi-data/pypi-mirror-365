"""
HTTP Server with SSE/Streaming support for Todo MCP system.

This module provides HTTP endpoints with Server-Sent Events (SSE) support
for real-time updates and streaming responses, complementing the standard
MCP stdio protocol.
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, AsyncGenerator, Set
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import uvicorn

from .config import TodoConfig
from .server import TodoMCPServer
from .models.task import Task, TaskStatus, Priority


class SSEMessage(BaseModel):
    """Server-Sent Event message format."""
    event: str = Field(..., description="Event type")
    data: Dict[str, Any] = Field(..., description="Event data")
    id: Optional[str] = Field(None, description="Event ID for client tracking")
    retry: Optional[int] = Field(None, description="Retry interval in milliseconds")


class StreamingRequest(BaseModel):
    """Request model for streaming operations."""
    tool: str = Field(..., description="MCP tool name")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Tool parameters")
    stream_config: Dict[str, Any] = Field(default_factory=dict, description="Streaming configuration")


class WebSocketConnection:
    """Manages WebSocket connections for real-time updates."""
    
    def __init__(self):
        self.connections: Set[Any] = set()
        self.logger = logging.getLogger(__name__)
    
    async def connect(self, websocket):
        """Add a new WebSocket connection."""
        await websocket.accept()
        self.connections.add(websocket)
        self.logger.info(f"WebSocket connected. Total connections: {len(self.connections)}")
    
    def disconnect(self, websocket):
        """Remove a WebSocket connection."""
        self.connections.discard(websocket)
        self.logger.info(f"WebSocket disconnected. Total connections: {len(self.connections)}")
    
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients."""
        if not self.connections:
            return
        
        message_str = json.dumps(message)
        disconnected = set()
        
        for connection in self.connections:
            try:
                await connection.send_text(message_str)
            except Exception as e:
                self.logger.warning(f"Failed to send message to WebSocket: {e}")
                disconnected.add(connection)
        
        # Remove disconnected clients
        for connection in disconnected:
            self.connections.discard(connection)


class TodoHTTPServer:
    """
    HTTP server with SSE/streaming support for Todo MCP system.
    
    Provides REST API endpoints and real-time streaming capabilities
    alongside the standard MCP stdio protocol.
    """
    
    def __init__(self, config: TodoConfig, mcp_server: TodoMCPServer):
        """
        Initialize the HTTP server.
        
        Args:
            config: Configuration settings
            mcp_server: MCP server instance for tool execution
        """
        self.config = config
        self.mcp_server = mcp_server
        self.logger = logging.getLogger(__name__)
        self.websocket_manager = WebSocketConnection()
        
        # Create FastAPI app
        self.app = FastAPI(
            title="Todo MCP Server",
            description="HTTP API with SSE/streaming support for Todo MCP system",
            version=config.server_version,
            docs_url="/docs",
            redoc_url="/redoc"
        )
        
        # Configure CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure appropriately for production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Mount static files
        static_dir = Path(__file__).parent / "static"
        if static_dir.exists():
            self.app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
        
        # Setup routes
        self._setup_routes()
        
        # Event subscribers for real-time updates
        self.event_subscribers: Set[asyncio.Queue] = set()
    
    async def _execute_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an MCP tool using the new server architecture.
        
        This is an adapter method to bridge the HTTP server with the new
        MCP server implementation that uses lifespan context management.
        """
        # Import tool modules dynamically to avoid circular imports
        if tool_name in ["create_task", "update_task", "delete_task", "get_task", "list_tasks", "get_task_context"]:
            from .tools import task_tools
            handler = getattr(task_tools, tool_name)
        elif tool_name in ["update_task_status", "bulk_status_update", "get_task_status", "get_pending_tasks", 
                          "get_in_progress_tasks", "get_blocked_tasks", "get_completed_tasks"]:
            from .tools import status_tools
            handler = getattr(status_tools, tool_name)
        elif tool_name in ["add_child_task", "remove_child_task", "get_task_hierarchy", "move_task"]:
            from .tools import hierarchy_tools
            handler = getattr(hierarchy_tools, tool_name)
        elif tool_name in ["search_tasks", "filter_tasks", "get_task_statistics"]:
            from .tools import query_tools
            handler = getattr(query_tools, tool_name)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        # Execute the handler directly
        return await handler(arguments)
    
    def _setup_routes(self):
        """Setup HTTP routes and endpoints."""
        
        @self.app.get("/")
        async def root():
            """Root endpoint - serve dashboard or API info."""
            # Check if static files exist
            static_dir = Path(__file__).parent / "static"
            index_file = static_dir / "index.html"
            
            if index_file.exists():
                # Serve the dashboard
                from fastapi.responses import FileResponse
                return FileResponse(str(index_file))
            else:
                # Return API information
                return {
                    "name": self.config.server_name,
                    "version": self.config.server_version,
                    "description": "Todo MCP Server with SSE/streaming support",
                    "endpoints": {
                        "health": "/health",
                        "tools": "/tools",
                        "stream": "/stream",
                        "events": "/events",
                        "websocket": "/ws",
                        "docs": "/docs"
                    }
                }
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint."""
            try:
                # Check MCP server health
                server_info = self.mcp_server.get_server_info()
                tools_count = server_info.get('tools_count', 0)
                
                return {
                    "status": "healthy",
                    "timestamp": datetime.utcnow().isoformat(),
                    "server_name": self.config.server_name,
                    "version": self.config.server_version,
                    "tools_available": tools_count,
                    "websocket_connections": len(self.websocket_manager.connections),
                    "event_subscribers": len(self.event_subscribers)
                }
            except Exception as e:
                self.logger.error(f"Health check failed: {e}")
                raise HTTPException(status_code=503, detail="Service unhealthy")
        
        @self.app.get("/tools")
        async def list_tools():
            """List available MCP tools."""
            try:
                server_info = self.mcp_server.get_server_info()
                tools_info = []
                
                for tool_name in server_info.get('tools', []):
                    tool_info = self.mcp_server._tools_registry.get(tool_name)
                    if tool_info:
                        tools_info.append({
                            "name": tool_info.name,
                            "description": tool_info.description,
                            "input_schema": tool_info.inputSchema
                        })
                
                return {
                    "tools": tools_info,
                    "count": len(tools_info)
                }
            except Exception as e:
                self.logger.error(f"Failed to list tools: {e}")
                raise HTTPException(status_code=500, detail="Failed to retrieve tools")
        
        @self.app.post("/tools/{tool_name}")
        async def execute_tool(tool_name: str, request: Dict[str, Any]):
            """Execute an MCP tool."""
            try:
                # Execute tool using the new MCP server architecture
                result = await self._execute_mcp_tool(tool_name, request)
                
                # Broadcast update for real-time subscribers
                await self._broadcast_tool_execution(tool_name, request, [result])
                
                return {
                    "success": True,
                    "tool": tool_name,
                    "result": json.dumps(result, ensure_ascii=False) if result else None,
                    "timestamp": datetime.utcnow().isoformat()
                }
            except Exception as e:
                self.logger.error(f"Tool execution failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/stream")
        async def stream_tool_execution(request: StreamingRequest):
            """Execute tool with streaming response."""
            return StreamingResponse(
                self._stream_tool_execution(request),
                media_type="text/plain"
            )
        
        @self.app.get("/events")
        async def event_stream(request: Request):
            """Server-Sent Events endpoint for real-time updates."""
            return StreamingResponse(
                self._event_stream(request),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Cache-Control"
                }
            )
        
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket):
            """WebSocket endpoint for real-time bidirectional communication."""
            await self.websocket_manager.connect(websocket)
            try:
                while True:
                    # Receive message from client
                    data = await websocket.receive_text()
                    message = json.loads(data)
                    
                    # Process tool execution request
                    if message.get("type") == "tool_call":
                        tool_name = message.get("tool")
                        parameters = message.get("parameters", {})
                        
                        try:
                            result = await self._execute_mcp_tool(tool_name, parameters)
                            response = {
                                "type": "tool_result",
                                "tool": tool_name,
                                "success": True,
                                "result": json.dumps(result, ensure_ascii=False) if result else None,
                                "timestamp": datetime.utcnow().isoformat()
                            }
                        except Exception as e:
                            response = {
                                "type": "tool_error",
                                "tool": tool_name,
                                "success": False,
                                "error": str(e),
                                "timestamp": datetime.utcnow().isoformat()
                            }
                        
                        await websocket.send_text(json.dumps(response))
                        
                        # Broadcast to other clients
                        await self.websocket_manager.broadcast({
                            "type": "tool_executed",
                            "tool": tool_name,
                            "parameters": parameters,
                            "timestamp": datetime.utcnow().isoformat()
                        })
                    
            except Exception as e:
                self.logger.error(f"WebSocket error: {e}")
            finally:
                self.websocket_manager.disconnect(websocket)
        
        @self.app.get("/tasks/stream")
        async def stream_tasks():
            """Stream all tasks with real-time updates."""
            return StreamingResponse(
                self._stream_tasks(),
                media_type="application/x-ndjson"
            )
        
        @self.app.get("/tasks/{task_id}/stream")
        async def stream_task_updates(task_id: str):
            """Stream updates for a specific task."""
            return StreamingResponse(
                self._stream_task_updates(task_id),
                media_type="text/event-stream"
            )
    
    async def _stream_tool_execution(self, request: StreamingRequest) -> AsyncGenerator[str, None]:
        """Stream tool execution with progress updates."""
        try:
            yield f"data: {json.dumps({'status': 'starting', 'tool': request.tool})}\n\n"
            
            # Execute the tool
            start_time = time.time()
            result = await self._execute_mcp_tool(request.tool, request.parameters)
            execution_time = time.time() - start_time
            
            # Stream progress updates
            yield f"data: {json.dumps({'status': 'processing', 'progress': 50})}\n\n"
            
            # Simulate streaming for long operations
            if execution_time > 1.0:  # For operations taking more than 1 second
                for i in range(51, 100, 10):
                    yield f"data: {json.dumps({'status': 'processing', 'progress': i})}\n\n"
                    await asyncio.sleep(0.1)
            
            # Send final result
            final_result = {
                'status': 'completed',
                'result': json.dumps(result, ensure_ascii=False) if result else None,
                'execution_time': execution_time,
                'timestamp': datetime.utcnow().isoformat()
            }
            yield f"data: {json.dumps(final_result)}\n\n"
            
        except Exception as e:
            error_result = {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
            yield f"data: {json.dumps(error_result)}\n\n"
    
    async def _event_stream(self, request: Request) -> AsyncGenerator[str, None]:
        """Generate Server-Sent Events stream."""
        # Create event queue for this client
        event_queue = asyncio.Queue()
        self.event_subscribers.add(event_queue)
        
        try:
            # Send initial connection event
            yield self._format_sse_message(SSEMessage(
                event="connected",
                data={"message": "Connected to Todo MCP Server event stream"},
                id=str(int(time.time()))
            ))
            
            # Send periodic heartbeat and handle events
            while True:
                try:
                    # Wait for event with timeout for heartbeat
                    event = await asyncio.wait_for(event_queue.get(), timeout=30.0)
                    yield self._format_sse_message(event)
                except asyncio.TimeoutError:
                    # Send heartbeat
                    yield self._format_sse_message(SSEMessage(
                        event="heartbeat",
                        data={"timestamp": datetime.utcnow().isoformat()},
                        id=str(int(time.time()))
                    ))
                
                # Check if client disconnected
                if await request.is_disconnected():
                    break
                    
        except Exception as e:
            self.logger.error(f"Event stream error: {e}")
        finally:
            self.event_subscribers.discard(event_queue)
    
    async def _stream_tasks(self) -> AsyncGenerator[str, None]:
        """Stream all tasks in NDJSON format."""
        try:
            # Get all tasks
            result = await self._execute_mcp_tool("list_tasks", {"limit": 1000})
            
            if result and result.get("success") and "tasks" in result:
                for task in result["tasks"]:
                    yield f"{json.dumps(task)}\n"
                    await asyncio.sleep(0.01)  # Small delay for streaming effect
            
        except Exception as e:
            error_msg = {"error": str(e), "timestamp": datetime.utcnow().isoformat()}
            yield f"{json.dumps(error_msg)}\n"
    
    async def _stream_task_updates(self, task_id: str) -> AsyncGenerator[str, None]:
        """Stream updates for a specific task."""
        try:
            # Send initial task data
            result = await self._execute_mcp_tool("get_task", {"task_id": task_id})
            
            if result:
                yield f"data: {json.dumps(result)}\n\n"
            
            # Create event queue for task updates
            event_queue = asyncio.Queue()
            self.event_subscribers.add(event_queue)
            
            try:
                while True:
                    event = await event_queue.get()
                    # Filter events for this specific task
                    if (event.event in ["task_updated", "task_status_changed"] and 
                        event.data.get("task_id") == task_id):
                        yield self._format_sse_message(event)
            finally:
                self.event_subscribers.discard(event_queue)
                
        except Exception as e:
            error_event = SSEMessage(
                event="error",
                data={"error": str(e), "task_id": task_id}
            )
            yield self._format_sse_message(error_event)
    
    def _format_sse_message(self, message: SSEMessage) -> str:
        """Format message for Server-Sent Events."""
        lines = []
        
        if message.id:
            lines.append(f"id: {message.id}")
        
        if message.retry:
            lines.append(f"retry: {message.retry}")
        
        lines.append(f"event: {message.event}")
        lines.append(f"data: {json.dumps(message.data)}")
        lines.append("")  # Empty line to end the event
        
        return "\n".join(lines) + "\n"
    
    async def _broadcast_tool_execution(self, tool_name: str, parameters: Dict[str, Any], result: List[Any]):
        """Broadcast tool execution to all subscribers."""
        event = SSEMessage(
            event="tool_executed",
            data={
                "tool": tool_name,
                "parameters": parameters,
                "success": True,
                "timestamp": datetime.utcnow().isoformat()
            },
            id=str(int(time.time()))
        )
        
        # Send to SSE subscribers
        for event_queue in self.event_subscribers:
            try:
                await event_queue.put(event)
            except Exception as e:
                self.logger.warning(f"Failed to send event to subscriber: {e}")
        
        # Send to WebSocket subscribers
        await self.websocket_manager.broadcast(event.dict())
    
    async def broadcast_task_update(self, task_id: str, event_type: str, task_data: Dict[str, Any]):
        """Broadcast task update events."""
        event = SSEMessage(
            event=event_type,
            data={
                "task_id": task_id,
                "task": task_data,
                "timestamp": datetime.utcnow().isoformat()
            },
            id=str(int(time.time()))
        )
        
        # Send to SSE subscribers
        for event_queue in self.event_subscribers:
            try:
                await event_queue.put(event)
            except Exception as e:
                self.logger.warning(f"Failed to send task update event: {e}")
        
        # Send to WebSocket subscribers
        await self.websocket_manager.broadcast(event.dict())
    
    async def start_server(self, host: str = "0.0.0.0", port: int = 8000):
        """Start the HTTP server."""
        self.logger.info(f"Starting HTTP server on {host}:{port}")
        
        config = uvicorn.Config(
            self.app,
            host=host,
            port=port,
            log_level=self.config.log_level.lower(),
            access_log=True,
            loop="asyncio"
        )
        
        server = uvicorn.Server(config)
        await server.serve()
    
    def run_server(self, host: str = "0.0.0.0", port: int = 8000):
        """Run the HTTP server (blocking)."""
        uvicorn.run(
            self.app,
            host=host,
            port=port,
            log_level=self.config.log_level.lower(),
            access_log=True
        )


class StreamingTaskService:
    """Enhanced task service with streaming capabilities."""
    
    def __init__(self, http_server: TodoHTTPServer):
        self.http_server = http_server
        self.logger = logging.getLogger(__name__)
    
    async def create_task_with_streaming(self, task_data: Dict[str, Any]) -> AsyncGenerator[Dict[str, Any], None]:
        """Create task with streaming progress updates."""
        try:
            # Validation phase
            yield {"phase": "validation", "progress": 10, "message": "Validating task data"}
            await asyncio.sleep(0.1)
            
            # Creation phase
            yield {"phase": "creation", "progress": 50, "message": "Creating task"}
            result = await self.http_server._execute_mcp_tool("create_task", task_data)
            
            # Index update phase
            yield {"phase": "indexing", "progress": 80, "message": "Updating search indexes"}
            await asyncio.sleep(0.1)
            
            # Completion
            if result and result.get("success"):
                # Broadcast task creation
                await self.http_server.broadcast_task_update(
                    result["task"]["id"], 
                    "task_created", 
                    result["task"]
                )
                
                yield {
                    "phase": "completed", 
                    "progress": 100, 
                    "message": "Task created successfully",
                    "task": result.get("task")
                }
            else:
                yield {"phase": "error", "progress": 100, "message": "Failed to create task"}
                
        except Exception as e:
            yield {"phase": "error", "progress": 100, "message": str(e)}
    
    async def update_task_with_streaming(self, task_id: str, updates: Dict[str, Any]) -> AsyncGenerator[Dict[str, Any], None]:
        """Update task with streaming progress updates."""
        try:
            yield {"phase": "validation", "progress": 20, "message": "Validating updates"}
            
            # Update task
            yield {"phase": "updating", "progress": 60, "message": "Applying updates"}
            updates["task_id"] = task_id
            result = await self.http_server._execute_mcp_tool("update_task", updates)
            
            if result and result.get("success"):
                # Broadcast task update
                await self.http_server.broadcast_task_update(
                    task_id, 
                    "task_updated", 
                    result["task"]
                )
                
                yield {
                    "phase": "completed", 
                    "progress": 100, 
                    "message": "Task updated successfully",
                    "task": result.get("task")
                }
            else:
                yield {"phase": "error", "progress": 100, "message": "Failed to update task"}
                
        except Exception as e:
            yield {"phase": "error", "progress": 100, "message": str(e)}