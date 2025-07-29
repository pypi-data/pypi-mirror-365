# Design Document

## Overview

使用官方MCP Python SDK的FastMCP创建一个简单的MCP服务器，暴露现有的任务管理功能给大模型客户端。目标是提供一个标准的MCP接口，让AI客户端可以通过HTTP协议调用我们的任务管理工具。

## Architecture

### 简化架构
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AI Client     │    │   FastMCP       │    │   Task Tools    │
│                 │◄──►│                 │◄──►│                 │
│ - StreamableHttp│    │ - Official SDK  │    │ - create_task   │
│ - /mcp endpoint │    │ - Auto Protocol │    │ - list_tasks    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

**核心思路**：
1. 使用FastMCP创建标准MCP服务器
2. 用@mcp.tool()装饰器注册现有工具函数
3. 服务器自动处理HTTP协议和JSON-RPC
4. 客户端连接到 `http://localhost:8000/mcp`

## Components and Interfaces

### 1. FastMCP服务器 (核心组件)

**目的**: 使用官方SDK创建MCP服务器

**实现**:
```python
from mcp.server.fastmcp import FastMCP
from .tools import task_tools

# 创建FastMCP实例
mcp = FastMCP("todo-mcp-server")

# 直接注册现有工具函数
@mcp.tool()
async def create_task(title: str, description: str = "", priority: str = "medium") -> dict:
    """创建新任务"""
    return await task_tools.create_task({
        "title": title,
        "description": description, 
        "priority": priority
    })

# 运行服务器
mcp.run(transport="streamable-http", port=8000)
```

### 2. 工具注册 (简单包装)

**目的**: 将现有工具函数包装为FastMCP工具

**方法**:
- 为每个现有工具创建一个FastMCP装饰器函数
- 函数参数直接映射到工具参数
- 调用现有的工具实现
- 返回结果给FastMCP处理

### 3. 启动集成

**目的**: 在现有启动流程中添加FastMCP选项

**实现**:
```python
# 在__main__.py中添加新命令
@cli.command()
def serve_mcp_http(host: str = "0.0.0.0", port: int = 8000):
    """启动MCP HTTP服务器"""
    from .fastmcp_server import create_mcp_server
    mcp = create_mcp_server(config)
    mcp.run(transport="streamable-http", host=host, port=port)
```

## Data Models

### 工具函数签名

直接使用现有工具的参数，FastMCP自动处理JSON Schema生成：

```python
@mcp.tool()
async def create_task(title: str, description: str = "", priority: str = "medium") -> dict:
    """创建新任务"""
    
@mcp.tool() 
async def list_tasks(status: List[str] = None, limit: int = 100) -> dict:
    """列出任务"""
    
@mcp.tool()
async def update_task_status(task_id: str, status: str) -> dict:
    """更新任务状态"""
```

### 配置

复用现有的TodoConfig，无需额外配置类：

```python
def create_mcp_server(config: TodoConfig) -> FastMCP:
    mcp = FastMCP("todo-mcp-server")
    # 注册所有工具...
    return mcp
```

## Error Handling

FastMCP自动处理所有MCP协议错误，我们只需要：

```python
@mcp.tool()
async def create_task(title: str) -> dict:
    try:
        return await task_tools.create_task({"title": title})
    except Exception as e:
        # FastMCP自动转换为MCP错误响应
        raise e
```

## 实现要点

1. **最小化更改**: 只添加FastMCP服务器，不修改现有代码
2. **复用逻辑**: 直接调用现有的task_tools函数
3. **标准协议**: FastMCP处理所有MCP协议细节
4. **简单部署**: 一个命令启动HTTP MCP服务器

## Testing Strategy

### 基本测试
- 测试FastMCP服务器启动
- 测试工具注册和调用
- 测试MCP客户端连接

### 集成测试  
- 使用官方MCP客户端测试连接
- 验证所有工具功能正常
- 测试错误处理

## Implementation Notes

### 核心实现
```python
# src/todo_mcp/fastmcp_server.py
from mcp.server.fastmcp import FastMCP
from .tools import task_tools, status_tools, hierarchy_tools, query_tools

def create_mcp_server(config: TodoConfig) -> FastMCP:
    mcp = FastMCP("todo-mcp-server")
    
    # 注册所有现有工具
    register_task_tools(mcp)
    register_status_tools(mcp) 
    register_hierarchy_tools(mcp)
    register_query_tools(mcp)
    
    return mcp

def register_task_tools(mcp: FastMCP):
    @mcp.tool()
    async def create_task(title: str, description: str = "", priority: str = "medium") -> dict:
        return await task_tools.create_task({"title": title, "description": description, "priority": priority})
    
    @mcp.tool()
    async def list_tasks(limit: int = 100) -> dict:
        return await task_tools.list_tasks({"limit": limit})
    
    # ... 其他工具
```

### 启动命令
```python
# 在__main__.py中添加
@cli.command()
def serve_fastmcp(host: str = "0.0.0.0", port: int = 8000):
    """启动FastMCP HTTP服务器"""
    from .fastmcp_server import create_mcp_server
    mcp = create_mcp_server(config)
    mcp.run(transport="streamable-http", host=host, port=port)
```

这样客户端就可以连接到 `http://localhost:8000/mcp` 使用所有任务管理功能。