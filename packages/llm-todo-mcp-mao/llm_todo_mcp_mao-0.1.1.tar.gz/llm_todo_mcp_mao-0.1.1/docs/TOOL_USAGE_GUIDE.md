# MCP工具使用指南 - 简化版

本指南专为AI客户端和大模型设计，提供简单易懂的工具使用说明。

## 🚀 快速开始

### 启动服务器
```bash
# SSE传输（推荐用于Web客户端）
uv run todo-mcp-server serve-sse --port 8000

# StreamableHTTP传输（推荐用于MCP客户端）
uv run todo-mcp-server serve-fastmcp --port 8000
```

## 📋 核心工具

### 1. 任务管理

#### 创建任务
```json
{
  "name": "create_task",
  "arguments": {
    "title": "任务标题",
    "description": "任务描述",
    "priority": "high",
    "tags": ["标签1", "标签2"]
  }
}
```

#### 更新任务
```json
{
  "name": "update_task",
  "arguments": {
    "task_id": "任务ID",
    "title": "新标题",
    "priority": "medium"
  }
}
```

#### 获取任务
```json
{
  "name": "get_task",
  "arguments": {
    "task_id": "任务ID"
  }
}
```

#### 列出任务
```json
{
  "name": "list_tasks",
  "arguments": {
    "status": "pending",
    "priority": "high",
    "include_completed": false
  }
}
```

#### 删除任务
```json
{
  "name": "delete_task",
  "arguments": {
    "task_id": "任务ID",
    "cascade": false
  }
}
```

### 2. 状态管理

#### 更新任务状态
```json
{
  "name": "update_task_status",
  "arguments": {
    "task_id": "任务ID",
    "status": "completed"
  }
}
```

#### 获取不同状态的任务
```json
// 获取待处理任务
{"name": "get_pending_tasks", "arguments": {}}

// 获取进行中任务
{"name": "get_in_progress_tasks", "arguments": {}}

// 获取已完成任务
{"name": "get_completed_tasks", "arguments": {}}

// 获取阻塞任务
{"name": "get_blocked_tasks", "arguments": {}}
```

### 3. 搜索和过滤

#### 搜索任务
```json
{
  "name": "search_tasks",
  "arguments": {
    "search_text": "搜索关键词",
    "status": ["pending", "in_progress"],
    "limit": 10
  }
}
```

#### 高级过滤
```json
{
  "name": "filter_tasks",
  "arguments": {
    "priority": ["high", "urgent"],
    "tags": ["重要", "紧急"],
    "created_after": "2024-01-01T00:00:00Z",
    "limit": 20
  }
}
```

#### 获取统计信息
```json
{
  "name": "get_task_statistics",
  "arguments": {}
}
```

### 4. 层级管理

#### 添加子任务关系
```json
{
  "name": "add_child_task",
  "arguments": {
    "parent_id": "父任务ID",
    "child_id": "子任务ID"
  }
}
```

#### 获取任务层级
```json
{
  "name": "get_task_hierarchy",
  "arguments": {
    "task_id": "根任务ID",
    "max_depth": 3,
    "include_ancestors": true
  }
}
```

#### 移动任务
```json
{
  "name": "move_task",
  "arguments": {
    "task_id": "任务ID",
    "new_parent_id": "新父任务ID"
  }
}
```

## 📝 参数说明

### 优先级 (priority)
- `low` - 低优先级
- `medium` - 中等优先级（默认）
- `high` - 高优先级
- `urgent` - 紧急

### 状态 (status)
- `pending` - 待处理（默认）
- `in_progress` - 进行中
- `completed` - 已完成
- `blocked` - 阻塞
- `cancelled` - 已取消

### 日期格式
使用ISO 8601格式：`2024-01-20T17:00:00Z`

## 🎯 常用场景

### 场景1：创建项目任务
```json
{
  "name": "create_task",
  "arguments": {
    "title": "网站重构项目",
    "description": "重构公司官网，提升用户体验",
    "priority": "high",
    "tags": ["项目", "网站", "重构"]
  }
}
```

### 场景2：查找高优先级待处理任务
```json
{
  "name": "filter_tasks",
  "arguments": {
    "status": ["pending"],
    "priority": ["high", "urgent"],
    "include_completed": false,
    "limit": 10
  }
}
```

### 场景3：完成任务
```json
{
  "name": "update_task_status",
  "arguments": {
    "task_id": "任务ID",
    "status": "completed"
  }
}
```

### 场景4：搜索相关任务
```json
{
  "name": "search_tasks",
  "arguments": {
    "search_text": "数据分析",
    "include_completed": true,
    "limit": 5
  }
}
```

## ⚠️ 注意事项

1. **必需参数**: `task_id`、`title`等标记为必需的参数不能省略
2. **可选参数**: 可以省略，系统会使用默认值
3. **数组参数**: `tags`、`status`等可以传递数组
4. **日期参数**: 使用ISO格式，时区建议使用UTC (Z后缀)
5. **ID格式**: 任务ID是UUID格式的字符串

## 🔍 错误处理

工具调用失败时会返回错误信息：
```json
{
  "success": false,
  "error": "错误描述",
  "data": null
}
```

成功时返回：
```json
{
  "success": true,
  "data": { /* 结果数据 */ },
  "message": "操作成功信息"
}
```

## 📞 获取帮助

- 查看完整API文档：`docs/API.md`
- 客户端连接指南：`docs/CLIENT_CONNECTION_GUIDE.md`
- 架构说明：`docs/ARCHITECTURE.md`