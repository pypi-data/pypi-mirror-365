"""
Modern MCP server implementation using official MCP Python SDK.

This module provides a compliant MCP server implementation that follows
the official Model Context Protocol Python SDK patterns and best practices.
Updated to use the latest SDK patterns including proper server initialization,
lifespan management, and structured output support.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

import mcp.server.stdio
import mcp.types as types
from mcp.server.lowlevel import NotificationOptions, Server
from mcp.server.models import InitializationOptions

from .config import TodoConfig
from .services.task_service import TaskService


class TodoMCPServer:
    """
    Modern MCP server implementation using official Python SDK.
    
    This server provides MCP-compatible tools for AI agents to manage
    tasks through structured interfaces following the latest MCP protocol
    specifications and SDK best practices.
    """
    
    def __init__(self, config: TodoConfig):
        """
        Initialize the Todo MCP server.
        
        Args:
            config: Configuration settings for the server
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize MCP server with lifespan management
        self.server = Server(self.config.server_name, lifespan=self._server_lifespan)
        self._setup_handlers()
        
        # Tool registry for better organization
        self._tools_registry = {}
        self._register_all_tools()
    
    @asynccontextmanager
    async def _server_lifespan(self, server: Server) -> AsyncIterator[Dict[str, Any]]:
        """
        Manage server startup and shutdown lifecycle.
        
        This provides proper resource initialization and cleanup
        following the official SDK patterns.
        """
        # Initialize resources on startup
        self.logger.info("Initializing server resources...")
        task_service = TaskService(self.config)
        await task_service.initialize()
        
        try:
            # Yield context with initialized resources
            yield {"task_service": task_service}
        finally:
            # Clean up on shutdown
            self.logger.info("Cleaning up server resources...")
            await task_service.cleanup()
        
    def _setup_handlers(self) -> None:
        """Set up MCP protocol handlers following SDK best practices."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
            """Handle list_tools request with proper logging."""
            self.logger.debug("Handling list_tools request")
            tools = list(self._tools_registry.values())
            self.logger.info(f"Returning {len(tools)} available tools")
            return tools
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
            """Handle call_tool request with comprehensive error handling."""
            self.logger.debug(f"Received call_tool request: {name} with args: {arguments}")
            
            try:
                # Get task service from lifespan context
                ctx = self.server.request_context
                task_service = ctx.lifespan_context["task_service"]
                
                # Execute tool
                result = await self._execute_tool(name, arguments, task_service)
                
                # Format response
                response_text = json.dumps(result, ensure_ascii=False, indent=2)
                self.logger.info(f"Tool '{name}' executed successfully")
                
                return [types.TextContent(type="text", text=response_text)]
                
            except Exception as e:
                self.logger.error(f"Tool '{name}' execution failed: {e}")
                error_result = {
                    "error": True,
                    "error_type": type(e).__name__,
                    "message": str(e),
                    "tool": name,
                    "timestamp": datetime.utcnow().isoformat()
                }
                return [types.TextContent(type="text", text=json.dumps(error_result, ensure_ascii=False, indent=2))]
    
    def _register_all_tools(self) -> None:
        """Register all available tools with proper schemas."""
        # Task management tools
        self._register_tool(
            "create_task",
            "Create a new task with optional hierarchy and metadata",
            {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Task title (required)"},
                    "description": {"type": "string", "description": "Task description"},
                    "priority": {"type": "string", "enum": ["low", "medium", "high", "urgent"], "default": "medium"},
                    "tags": {"type": "array", "items": {"type": "string"}, "description": "Task tags"},
                    "parent_id": {"type": "string", "description": "Parent task ID for hierarchy"},
                    "due_date": {"type": "string", "format": "date-time", "description": "Due date in ISO format"},
                    "metadata": {"type": "object", "description": "Additional metadata"}
                },
                "required": ["title"]
            }
        )
        
        self._register_tool(
            "update_task",
            "Update an existing task's properties",
            {
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "Task ID to update (required)"},
                    "title": {"type": "string", "description": "New task title"},
                    "description": {"type": "string", "description": "New task description"},
                    "priority": {"type": "string", "enum": ["low", "medium", "high", "urgent"]},
                    "tags": {"type": "array", "items": {"type": "string"}},
                    "due_date": {"type": "string", "format": "date-time"},
                    "metadata": {"type": "object"}
                },
                "required": ["task_id"]
            }
        )
        
        self._register_tool(
            "delete_task",
            "Delete a task and handle child task relationships",
            {
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "Task ID to delete (required)"},
                    "cascade": {"type": "boolean", "default": False, "description": "Delete child tasks as well"}
                },
                "required": ["task_id"]
            }
        )
        
        self._register_tool(
            "get_task",
            "Retrieve a single task by ID",
            {
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "Task ID to retrieve (required)"}
                },
                "required": ["task_id"]
            }
        )
        
        self._register_tool(
            "list_tasks",
            "List tasks with optional filtering and pagination",
            {
                "type": "object",
                "properties": {
                    "status": {"type": "array", "items": {"type": "string", "enum": ["pending", "in_progress", "completed", "blocked"]}},
                    "priority": {"type": "array", "items": {"type": "string", "enum": ["low", "medium", "high", "urgent"]}},
                    "tags": {"type": "array", "items": {"type": "string"}},
                    "parent_id": {"type": "string"},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 1000, "default": 100}
                }
            }
        )
        
        # Status management tools
        self._register_tool(
            "update_task_status",
            "Update task status with validation",
            {
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "Task ID to update (required)"},
                    "status": {"type": "string", "enum": ["pending", "in_progress", "completed", "blocked"], "description": "New status (required)"}
                },
                "required": ["task_id", "status"]
            }
        )
        
        self._register_tool(
            "bulk_status_update",
            "Update status for multiple tasks in a single operation",
            {
                "type": "object",
                "properties": {
                    "task_ids": {"type": "array", "items": {"type": "string"}, "description": "List of task IDs (required)"},
                    "status": {"type": "string", "enum": ["pending", "in_progress", "completed", "blocked"], "description": "New status (required)"}
                },
                "required": ["task_ids", "status"]
            }
        )
        
        # Hierarchy management tools
        self._register_tool(
            "add_child_task",
            "Add a child task relationship",
            {
                "type": "object",
                "properties": {
                    "parent_id": {"type": "string", "description": "Parent task ID (required)"},
                    "child_id": {"type": "string", "description": "Child task ID (required)"}
                },
                "required": ["parent_id", "child_id"]
            }
        )
        
        self._register_tool(
            "get_task_hierarchy",
            "Get task hierarchy tree",
            {
                "type": "object",
                "properties": {
                    "root_id": {"type": "string", "description": "Root task ID (optional)"}
                }
            }
        )
        
        # Query tools
        self._register_tool(
            "search_tasks",
            "Search tasks by text content",
            {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query (required)"},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 100, "default": 20}
                },
                "required": ["query"]
            }
        )
        
        self._register_tool(
            "get_task_statistics",
            "Get comprehensive task statistics and metrics",
            {
                "type": "object",
                "properties": {}
            }
        )
    
    def _register_tool(self, name: str, description: str, input_schema: Dict[str, Any]) -> None:
        """Register a tool with the server."""
        tool = types.Tool(
            name=name,
            description=description,
            inputSchema=input_schema
        )
        self._tools_registry[name] = tool
    
    async def _execute_tool(self, name: str, arguments: Dict[str, Any], task_service: TaskService) -> Dict[str, Any]:
        """Execute a tool with the given arguments."""
        # Import tool modules dynamically to avoid circular imports
        if name in ["create_task", "update_task", "delete_task", "get_task", "list_tasks", "get_task_context"]:
            from .tools import task_tools
            handler = getattr(task_tools, name)
        elif name in ["update_task_status", "bulk_status_update", "get_task_status", "get_pending_tasks", 
                     "get_in_progress_tasks", "get_blocked_tasks", "get_completed_tasks"]:
            from .tools import status_tools
            handler = getattr(status_tools, name)
        elif name in ["add_child_task", "remove_child_task", "get_task_hierarchy", "move_task"]:
            from .tools import hierarchy_tools
            handler = getattr(hierarchy_tools, name)
        elif name in ["search_tasks", "filter_tasks", "get_task_statistics"]:
            from .tools import query_tools
            handler = getattr(query_tools, name)
        else:
            raise ValueError(f"Unknown tool: {name}")
        
        # Execute the handler
        return await handler(arguments)
    
    def _get_tool_definitions_legacy(self) -> List[types.Tool]:
        """Get all tool definitions for MCP introspection."""
        tools = []
        
        # Task management tools
        tools.extend([
            Tool(
                name="create_task",
                description="Create a new task with optional hierarchy and metadata",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "Task title"},
                        "description": {"type": "string", "description": "Task description"},
                        "priority": {"type": "string", "enum": ["low", "medium", "high", "urgent"], "default": "medium"},
                        "tags": {"type": "array", "items": {"type": "string"}, "description": "Task tags"},
                        "parent_id": {"type": "string", "description": "Parent task ID"},
                        "due_date": {"type": "string", "format": "date-time", "description": "Due date in ISO format"},
                        "metadata": {"type": "object", "description": "Additional metadata"}
                    },
                    "required": ["title"]
                }
            ),
            Tool(
                name="update_task",
                description="Update an existing task's properties",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string", "description": "Task ID to update"},
                        "title": {"type": "string", "description": "New task title"},
                        "description": {"type": "string", "description": "New task description"},
                        "priority": {"type": "string", "enum": ["low", "medium", "high", "urgent"]},
                        "tags": {"type": "array", "items": {"type": "string"}},
                        "due_date": {"type": "string", "format": "date-time"},
                        "metadata": {"type": "object"}
                    },
                    "required": ["task_id"]
                }
            ),
            Tool(
                name="delete_task",
                description="Delete a task and handle child task relationships",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string", "description": "Task ID to delete"},
                        "cascade": {"type": "boolean", "default": False, "description": "Delete child tasks as well"}
                    },
                    "required": ["task_id"]
                }
            ),
            Tool(
                name="get_task",
                description="Retrieve a single task by ID",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string", "description": "Task ID to retrieve"}
                    },
                    "required": ["task_id"]
                }
            ),
            Tool(
                name="list_tasks",
                description="List tasks with optional filtering",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "status": {"type": "array", "items": {"type": "string", "enum": ["pending", "in_progress", "completed", "blocked"]}},
                        "priority": {"type": "array", "items": {"type": "string", "enum": ["low", "medium", "high", "urgent"]}},
                        "tags": {"type": "array", "items": {"type": "string"}},
                        "parent_id": {"type": "string"},
                        "limit": {"type": "integer", "minimum": 1, "maximum": 1000, "default": 100}
                    }
                }
            )
        ])
        
        # Status management tools
        tools.extend([
            Tool(
                name="update_task_status",
                description="Update task status with validation",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string", "description": "Task ID to update"},
                        "status": {"type": "string", "enum": ["pending", "in_progress", "completed", "blocked"], "description": "New status"}
                    },
                    "required": ["task_id", "status"]
                }
            ),
            Tool(
                name="bulk_status_update",
                description="Update status for multiple tasks",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_ids": {"type": "array", "items": {"type": "string"}, "description": "List of task IDs"},
                        "status": {"type": "string", "enum": ["pending", "in_progress", "completed", "blocked"], "description": "New status"}
                    },
                    "required": ["task_ids", "status"]
                }
            ),
            Tool(
                name="get_task_status",
                description="Get current status of a task",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string", "description": "Task ID to check"}
                    },
                    "required": ["task_id"]
                }
            ),
            Tool(
                name="get_pending_tasks",
                description="Get all tasks with pending status",
                inputSchema={"type": "object", "properties": {}}
            ),
            Tool(
                name="get_in_progress_tasks",
                description="Get all tasks with in_progress status",
                inputSchema={"type": "object", "properties": {}}
            ),
            Tool(
                name="get_blocked_tasks",
                description="Get all tasks with blocked status",
                inputSchema={"type": "object", "properties": {}}
            ),
            Tool(
                name="get_completed_tasks",
                description="Get all tasks with completed status",
                inputSchema={"type": "object", "properties": {}}
            )
        ])
        
        # Hierarchy management tools
        tools.extend([
            Tool(
                name="add_child_task",
                description="Add a child task relationship",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "parent_id": {"type": "string", "description": "Parent task ID"},
                        "child_id": {"type": "string", "description": "Child task ID"}
                    },
                    "required": ["parent_id", "child_id"]
                }
            ),
            Tool(
                name="remove_child_task",
                description="Remove a child task relationship",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "parent_id": {"type": "string", "description": "Parent task ID"},
                        "child_id": {"type": "string", "description": "Child task ID"}
                    },
                    "required": ["parent_id", "child_id"]
                }
            ),
            Tool(
                name="get_task_hierarchy",
                description="Get task hierarchy tree",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "root_id": {"type": "string", "description": "Root task ID (optional)"}
                    }
                }
            ),
            Tool(
                name="move_task",
                description="Move a task to a different parent",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string", "description": "Task ID to move"},
                        "new_parent_id": {"type": "string", "description": "New parent task ID (null for root level)"}
                    },
                    "required": ["task_id"]
                }
            )
        ])
        
        # Query tools
        tools.extend([
            Tool(
                name="search_tasks",
                description="Search tasks by text content",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "limit": {"type": "integer", "minimum": 1, "maximum": 100, "default": 20}
                    },
                    "required": ["query"]
                }
            ),
            Tool(
                name="filter_tasks",
                description="Filter tasks with advanced criteria",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "status": {"type": "array", "items": {"type": "string", "enum": ["pending", "in_progress", "completed", "blocked"]}},
                        "priority": {"type": "array", "items": {"type": "string", "enum": ["low", "medium", "high", "urgent"]}},
                        "tags": {"type": "array", "items": {"type": "string"}},
                        "created_after": {"type": "string", "format": "date-time"},
                        "created_before": {"type": "string", "format": "date-time"},
                        "due_after": {"type": "string", "format": "date-time"},
                        "due_before": {"type": "string", "format": "date-time"},
                        "limit": {"type": "integer", "minimum": 1, "maximum": 1000, "default": 100}
                    }
                }
            ),
            Tool(
                name="get_task_statistics",
                description="Get task statistics and metrics",
                inputSchema={"type": "object", "properties": {}}
            ),
            Tool(
                name="get_task_context",
                description="Get complete context for a task including hierarchy and history",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string", "description": "Task ID to get context for"}
                    },
                    "required": ["task_id"]
                }
            )
        ])
        
        return []  # Legacy method - not used in new implementation
    
    async def run(self) -> None:
        """
        Run the MCP server using the official SDK patterns.
        
        This method starts the server with proper initialization
        and lifespan management following SDK best practices.
        """
        self.logger.info(f"Starting {self.config.server_name} v{self.config.server_version}")
        
        try:
            # Run the MCP server with stdio transport and proper initialization
            async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
                await self.server.run(
                    read_stream,
                    write_stream,
                    InitializationOptions(
                        server_name=self.config.server_name,
                        server_version=self.config.server_version,
                        capabilities=self.server.get_capabilities(
                            notification_options=NotificationOptions(),
                            experimental_capabilities={},
                        ),
                    ),
                )
                
        except Exception as e:
            self.logger.error(f"Server error: {e}")
            raise
    
    def get_server_info(self) -> Dict[str, Any]:
        """Get server information for debugging and monitoring."""
        return {
            "name": self.config.server_name,
            "version": self.config.server_version,
            "description": "Task management server with MCP protocol support",
            "capabilities": self.server.get_capabilities(
                notification_options=NotificationOptions(),
                experimental_capabilities={},
            ),
            "tools_count": len(self._tools_registry),
            "tools": list(self._tools_registry.keys())
        }