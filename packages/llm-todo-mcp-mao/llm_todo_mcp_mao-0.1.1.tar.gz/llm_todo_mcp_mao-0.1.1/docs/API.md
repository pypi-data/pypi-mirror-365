# Todo MCP Server API Documentation

This document provides comprehensive documentation for all MCP tools available in the Todo MCP Server.

## Table of Contents

- [Task Management Tools](#task-management-tools)
- [Status Management Tools](#status-management-tools)
- [Hierarchy Management Tools](#hierarchy-management-tools)
- [Query Tools](#query-tools)
- [Data Models](#data-models)
- [Error Handling](#error-handling)

## Task Management Tools

### create_task

Creates a new task with optional metadata and hierarchy information.

**Parameters:**
- `title` (string, required): Task title (max 200 characters)
- `description` (string, optional): Task description (max 10,000 characters)
- `priority` (string, optional): Task priority - "low", "medium", "high", "urgent" (default: "medium")
- `tags` (array[string], optional): List of tags for categorization
- `parent_id` (string, optional): ID of parent task for hierarchy
- `due_date` (string, optional): Due date in ISO 8601 format
- `metadata` (object, optional): Additional metadata as key-value pairs

**Response:**
```json
{
  "success": true,
  "task": {
    "id": "task-001",
    "title": "Example Task",
    "description": "Task description",
    "status": "pending",
    "priority": "medium",
    "tags": ["example"],
    "parent_id": null,
    "child_ids": [],
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z",
    "due_date": null,
    "metadata": {}
  }
}
```

**Example:**
```python
result = await mcp_client.call_tool("create_task", {
    "title": "Implement user authentication",
    "description": "Add secure login functionality",
    "priority": "high",
    "tags": ["security", "backend"],
    "due_date": "2024-02-01T17:00:00Z",
    "metadata": {
        "estimated_hours": 8,
        "complexity": "medium"
    }
})
```

### update_task

Updates an existing task's properties.

**Parameters:**
- `task_id` (string, required): ID of the task to update
- `title` (string, optional): New task title
- `description` (string, optional): New task description
- `priority` (string, optional): New priority level
- `tags` (array[string], optional): New tags list (replaces existing)
- `due_date` (string, optional): New due date in ISO 8601 format
- `metadata` (object, optional): New metadata (merges with existing)

**Response:**
```json
{
  "success": true,
  "task": {
    "id": "task-001",
    "title": "Updated Task Title",
    "updated_at": "2024-01-15T11:45:00Z"
  }
}
```

### delete_task

Deletes a task and optionally its children.

**Parameters:**
- `task_id` (string, required): ID of the task to delete
- `cascade` (boolean, optional): Whether to delete child tasks (default: false)

**Response:**
```json
{
  "success": true,
  "message": "Task deleted successfully",
  "deleted_count": 1
}
```

### get_task

Retrieves a specific task by ID.

**Parameters:**
- `task_id` (string, required): ID of the task to retrieve

**Response:**
```json
{
  "success": true,
  "task": {
    "id": "task-001",
    "title": "Example Task",
    "description": "Task description",
    "status": "pending",
    "priority": "medium",
    "tags": ["example"],
    "parent_id": null,
    "child_ids": [],
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z",
    "due_date": null,
    "metadata": {}
  }
}
```

### list_tasks

Lists tasks with optional filtering and pagination.

**Parameters:**
- `status` (array[string], optional): Filter by status values
- `priority` (array[string], optional): Filter by priority levels
- `tags` (array[string], optional): Filter by tags (AND operation)
- `parent_id` (string, optional): Filter by parent task ID
- `limit` (integer, optional): Maximum number of tasks to return (default: 100, max: 1000)

**Response:**
```json
{
  "success": true,
  "tasks": [
    {
      "id": "task-001",
      "title": "Example Task",
      "status": "pending",
      "priority": "medium"
    }
  ],
  "total_count": 1
}
```

### get_task_context

Retrieves a task with complete context including hierarchy and history.

**Parameters:**
- `task_id` (string, required): ID of the task

**Response:**
```json
{
  "success": true,
  "task": {
    "id": "task-001",
    "title": "Example Task",
    "description": "Task description",
    "status": "pending",
    "priority": "medium",
    "tags": ["example"],
    "parent_id": null,
    "child_ids": [],
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z",
    "due_date": null,
    "metadata": {}
  },
  "context": {
    "parent": null,
    "children": [],
    "siblings": [],
    "tool_calls": [
      {
        "tool": "create_task",
        "timestamp": "2024-01-15T10:30:00Z",
        "agent": "user-agent"
      }
    ]
  }
}
```

## Status Management Tools

### update_task_status

Updates the status of a single task.

**Parameters:**
- `task_id` (string, required): ID of the task to update
- `status` (string, required): New status - "pending", "in_progress", "completed", "blocked"

**Response:**
```json
{
  "success": true,
  "task": {
    "id": "task-001",
    "status": "in_progress",
    "updated_at": "2024-01-15T11:30:00Z"
  }
}
```

### bulk_status_update

Updates the status of multiple tasks in a single operation.

**Parameters:**
- `task_ids` (array[string], required): List of task IDs to update
- `status` (string, required): New status for all tasks

**Response:**
```json
{
  "success": true,
  "updated_count": 3,
  "failed_count": 0,
  "results": [
    {
      "task_id": "task-001",
      "success": true,
      "status": "completed"
    }
  ]
}
```

### get_task_status

Gets the current status of a specific task.

**Parameters:**
- `task_id` (string, required): ID of the task

**Response:**
```json
{
  "success": true,
  "task_id": "task-001",
  "status": "in_progress",
  "updated_at": "2024-01-15T11:30:00Z"
}
```

### Status Query Tools

The following tools retrieve tasks by specific status:

- `get_pending_tasks`: Returns all tasks with "pending" status
- `get_in_progress_tasks`: Returns all tasks with "in_progress" status
- `get_blocked_tasks`: Returns all tasks with "blocked" status
- `get_completed_tasks`: Returns all tasks with "completed" status

**Parameters:** None

**Response:**
```json
{
  "success": true,
  "tasks": [
    {
      "id": "task-001",
      "title": "Example Task",
      "status": "pending",
      "priority": "medium",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "count": 1
}
```

## Hierarchy Management Tools

### add_child_task

Establishes a parent-child relationship between tasks.

**Parameters:**
- `parent_id` (string, required): ID of the parent task
- `child_id` (string, required): ID of the child task

**Response:**
```json
{
  "success": true,
  "message": "Child task relationship created",
  "parent_id": "parent-001",
  "child_id": "child-001"
}
```

### remove_child_task

Removes a parent-child relationship between tasks.

**Parameters:**
- `parent_id` (string, required): ID of the parent task
- `child_id` (string, required): ID of the child task

**Response:**
```json
{
  "success": true,
  "message": "Child task relationship removed",
  "parent_id": "parent-001",
  "child_id": "child-001"
}
```

### get_task_hierarchy

Retrieves the complete hierarchy tree for a task.

**Parameters:**
- `root_id` (string, optional): ID of the root task (if not provided, returns all root tasks)

**Response:**
```json
{
  "success": true,
  "hierarchy": {
    "id": "parent-001",
    "title": "Parent Task",
    "status": "in_progress",
    "children": [
      {
        "id": "child-001",
        "title": "Child Task 1",
        "status": "completed",
        "children": []
      },
      {
        "id": "child-002",
        "title": "Child Task 2",
        "status": "pending",
        "children": []
      }
    ]
  }
}
```

### move_task

Moves a task to a different parent or to root level.

**Parameters:**
- `task_id` (string, required): ID of the task to move
- `new_parent_id` (string, optional): ID of the new parent (null for root level)

**Response:**
```json
{
  "success": true,
  "message": "Task moved successfully",
  "task_id": "task-001",
  "old_parent_id": "old-parent",
  "new_parent_id": "new-parent"
}
```

## Query Tools

### search_tasks

Performs full-text search across task titles and descriptions.

**Parameters:**
- `query` (string, required): Search query string
- `limit` (integer, optional): Maximum results to return (default: 20, max: 100)

**Response:**
```json
{
  "success": true,
  "tasks": [
    {
      "id": "task-001",
      "title": "Authentication Implementation",
      "description": "Implement user authentication system",
      "relevance_score": 0.95,
      "matched_fields": ["title", "description"]
    }
  ],
  "total_matches": 1,
  "query": "authentication"
}
```

### filter_tasks

Advanced filtering with multiple criteria.

**Parameters:**
- `status` (array[string], optional): Filter by status values
- `priority` (array[string], optional): Filter by priority levels
- `tags` (array[string], optional): Filter by tags
- `created_after` (string, optional): Filter by creation date (ISO 8601)
- `created_before` (string, optional): Filter by creation date (ISO 8601)
- `due_after` (string, optional): Filter by due date (ISO 8601)
- `due_before` (string, optional): Filter by due date (ISO 8601)
- `limit` (integer, optional): Maximum results (default: 100, max: 1000)

**Response:**
```json
{
  "success": true,
  "tasks": [
    {
      "id": "task-001",
      "title": "Example Task",
      "status": "pending",
      "priority": "high",
      "tags": ["urgent", "security"],
      "created_at": "2024-01-15T10:30:00Z",
      "due_date": "2024-01-20T17:00:00Z"
    }
  ],
  "total_count": 1,
  "filters_applied": {
    "status": ["pending"],
    "priority": ["high"],
    "tags": ["urgent"]
  }
}
```

### get_task_statistics

Retrieves comprehensive task statistics and metrics.

**Parameters:** None

**Response:**
```json
{
  "success": true,
  "statistics": {
    "total_tasks": 150,
    "completion_rate": 0.67,
    "status_distribution": {
      "pending": 25,
      "in_progress": 15,
      "completed": 100,
      "blocked": 10
    },
    "priority_distribution": {
      "low": 30,
      "medium": 80,
      "high": 35,
      "urgent": 5
    },
    "tag_usage": {
      "backend": 45,
      "frontend": 30,
      "security": 20,
      "testing": 25
    },
    "hierarchy_stats": {
      "root_tasks": 20,
      "max_depth": 4,
      "avg_children_per_parent": 2.3
    },
    "temporal_stats": {
      "tasks_created_today": 5,
      "tasks_completed_today": 8,
      "overdue_tasks": 3,
      "avg_completion_time_hours": 72.5
    }
  },
  "generated_at": "2024-01-15T12:00:00Z"
}
```

## Data Models

### Task Model

```typescript
interface Task {
  id: string;                    // Unique task identifier
  title: string;                 // Task title (max 200 chars)
  description: string;           // Task description (max 10,000 chars)
  status: TaskStatus;            // Current task status
  priority: Priority;            // Task priority level
  tags: string[];               // List of tags
  parent_id: string | null;     // Parent task ID (null for root)
  child_ids: string[];          // List of child task IDs
  created_at: string;           // ISO 8601 timestamp
  updated_at: string;           // ISO 8601 timestamp
  due_date: string | null;      // ISO 8601 timestamp or null
  metadata: Record<string, any>; // Additional metadata
}
```

### Enums

```typescript
enum TaskStatus {
  PENDING = "pending",
  IN_PROGRESS = "in_progress", 
  COMPLETED = "completed",
  BLOCKED = "blocked"
}

enum Priority {
  LOW = "low",
  MEDIUM = "medium",
  HIGH = "high", 
  URGENT = "urgent"
}
```

### Tool Call Record

```typescript
interface ToolCall {
  tool: string;        // Name of the MCP tool called
  timestamp: string;   // ISO 8601 timestamp
  agent: string;       // Identifier of the calling agent
  parameters: any;     // Tool parameters (optional)
  result: any;         // Tool result (optional)
}
```

## Error Handling

### Error Response Format

All tools return errors in a consistent format:

```json
{
  "error": true,
  "error_type": "ValidationError",
  "message": "Task title cannot be empty",
  "tool": "create_task",
  "timestamp": 1705320000.123,
  "suggestion": "Provide a non-empty title for the task"
}
```

### Common Error Types

- **ValidationError**: Invalid input parameters
- **TaskNotFoundError**: Requested task does not exist
- **HierarchyError**: Invalid hierarchy operation (e.g., circular dependency)
- **PermissionError**: Insufficient permissions for operation
- **StorageError**: File system or storage-related error
- **ConcurrencyError**: Conflict due to concurrent modifications

### Error Codes

| Error Type | HTTP Status | Description |
|------------|-------------|-------------|
| ValidationError | 400 | Invalid input parameters |
| TaskNotFoundError | 404 | Task not found |
| HierarchyError | 409 | Invalid hierarchy operation |
| PermissionError | 403 | Insufficient permissions |
| StorageError | 500 | Storage system error |
| ConcurrencyError | 409 | Concurrent modification conflict |

### Best Practices

1. **Always check the `success` field** in responses before processing data
2. **Handle errors gracefully** by checking for the `error` field
3. **Use appropriate error handling** based on error types
4. **Implement retry logic** for transient errors (StorageError, ConcurrencyError)
5. **Validate inputs** before making tool calls to avoid ValidationErrors
6. **Use bulk operations** when possible to improve performance
7. **Cache frequently accessed data** to reduce API calls
8. **Monitor response times** and adjust timeout values accordingly

## Rate Limits

The server implements the following rate limits:

- **Task Creation**: 100 tasks per minute per agent
- **Bulk Operations**: 10 operations per minute per agent  
- **Search Queries**: 60 queries per minute per agent
- **Status Updates**: 200 updates per minute per agent

Rate limit headers are included in responses:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1705320060
```

## Versioning

The API follows semantic versioning. Current version: **1.0.0**

Version information is available in tool responses:

```json
{
  "success": true,
  "api_version": "1.0.0",
  "server_version": "1.0.0"
}
```

## Authentication

The MCP server uses the standard MCP authentication mechanism. No additional authentication is required for tool calls within an established MCP session.

For production deployments, consider implementing:
- API key authentication
- Rate limiting per API key
- Request signing for security
- Audit logging for compliance