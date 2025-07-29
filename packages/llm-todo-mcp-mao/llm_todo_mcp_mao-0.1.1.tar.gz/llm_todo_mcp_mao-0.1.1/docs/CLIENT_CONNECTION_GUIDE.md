# MCP客户端连接指南

Todo MCP服务器支持多种传输协议，以适应不同类型的客户端连接需求。

## 🚀 可用的服务器命令

### 1. 标准MCP服务器 (stdio)
```bash
uv run todo-mcp-server serve
```
- **传输方式**: stdio (标准输入输出)
- **适用客户端**: 官方MCP客户端、Claude Desktop等
- **连接方式**: 进程间通信

### 2. HTTP服务器 (REST API + WebSocket + SSE)
```bash
uv run todo-mcp-server serve-http --port 8000 --host 0.0.0.0
```
- **传输方式**: HTTP REST API, WebSocket, Server-Sent Events
- **适用客户端**: Web应用、HTTP客户端
- **端点**:
  - REST API: `http://localhost:8000/api/`
  - WebSocket: `ws://localhost:8000/ws`
  - SSE: `http://localhost:8000/events`
  - 文档: `http://localhost:8000/docs`

### 3. FastMCP服务器 (StreamableHTTP)
```bash
uv run todo-mcp-server serve-fastmcp --port 8000 --host 0.0.0.0 --transport streamable-http
```
- **传输方式**: StreamableHTTP (官方MCP协议)
- **适用客户端**: 支持StreamableHTTP的MCP客户端
- **端点**: `http://localhost:8000/mcp`

### 4. FastMCP SSE服务器
```bash
uv run todo-mcp-server serve-sse --port 8000 --host 0.0.0.0
```
- **传输方式**: Server-Sent Events
- **适用客户端**: Web客户端、支持SSE的MCP客户端
- **端点**:
  - SSE: `http://localhost:8000/sse`
  - Messages: `http://localhost:8000/messages/`

### 5. 混合模式服务器
```bash
uv run todo-mcp-server serve-hybrid --port 8000 --host 0.0.0.0 --mcp-stdio
```
- **传输方式**: HTTP + MCP stdio (可选)
- **适用客户端**: 多种客户端同时支持

## 🔧 客户端配置示例

### Claude Desktop配置
```json
{
  "mcpServers": {
    "todo-mcp": {
      "command": "uv",
      "args": ["run", "todo-mcp-server", "serve"],
      "cwd": "/path/to/todo-mcp"
    }
  }
}
```

### MCP客户端 (StreamableHTTP)
```json
{
  "servers": {
    "todo-mcp": {
      "url": "http://localhost:8000/mcp",
      "transport": "streamable-http"
    }
  }
}
```

### MCP客户端 (SSE)
```json
{
  "servers": {
    "todo-mcp": {
      "url": "http://localhost:8000/sse",
      "transport": "sse"
    }
  }
}
```

## 🐛 常见问题解决

### 问题1: "Failed to open SSE stream: 400 Bad Request"

**原因**: 客户端尝试使用SSE传输，但服务器配置为其他传输方式。

**解决方案**:
```bash
# 使用SSE传输启动服务器
uv run todo-mcp-server serve-sse --port 8000

# 或使用FastMCP的SSE传输
uv run todo-mcp-server serve-fastmcp --transport sse --port 8000
```

### 问题2: "Connection refused" 或端口冲突

**解决方案**:
```bash
# 使用不同端口
uv run todo-mcp-server serve-fastmcp --port 8001

# 检查端口占用
netstat -an | findstr :8000
```

### 问题3: "Method not found" 错误

**原因**: 客户端和服务器使用不同的MCP协议版本或传输方式。

**解决方案**:
1. 确保使用正确的传输方式
2. 检查客户端配置的URL和端点
3. 查看服务器日志确认连接状态

## 📊 传输方式对比

| 传输方式 | 适用场景 | 优点 | 缺点 |
|---------|---------|------|------|
| stdio | 本地客户端 | 简单、可靠 | 仅限本地 |
| HTTP REST | Web应用 | 标准协议、易调试 | 无实时通信 |
| WebSocket | 实时应用 | 双向通信、低延迟 | 连接管理复杂 |
| SSE | Web客户端 | 服务器推送、简单 | 单向通信 |
| StreamableHTTP | MCP客户端 | 官方协议、标准化 | 较新的协议 |

## 🔍 调试技巧

### 1. 启用调试日志
```bash
uv run todo-mcp-server serve-fastmcp --log-level DEBUG
```

### 2. 测试连接
```bash
# 测试HTTP端点
curl http://localhost:8000/mcp

# 测试SSE端点
curl -H "Accept: text/event-stream" http://localhost:8000/sse
```

### 3. 查看服务器状态
```bash
# 检查端口监听
netstat -an | findstr :8000

# 查看进程
tasklist | findstr python
```

## 📞 获取帮助

如果遇到连接问题，请：

1. 检查服务器日志输出
2. 确认客户端配置正确
3. 验证网络连接和端口
4. 查看本文档的故障排除部分

更多信息请参考：
- [架构文档](ARCHITECTURE.md)
- [API文档](API.md)
- [部署指南](DEPLOYMENT.md)