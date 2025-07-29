# Todo MCP 快速参考卡片

## 🚀 常用工具速查

### 任务基础操作
```json
// 创建任务
{"name": "create_task", "arguments": {"title": "任务标题", "description": "详细描述", "priority": "high", "due_date": "2024-12-31T23:59:59Z", "tags": ["标签1", "标签2"], "parent_id": "父任务ID"}}

// 更新任务
{"name": "update_task", "arguments": {"task_id": "ID", "title": "新标题", "priority": "urgent", "status": "in_progress"}}

// 获取任务详情
{"name": "get_task", "arguments": {"task_id": "ID"}}

// 获取任务完整上下文
{"name": "get_task_context", "arguments": {"task_id": "ID"}}

// 删除任务
{"name": "delete_task", "arguments": {"task_id": "ID", "cascade": true}}
```

### 查询操作
```json
// 列出任务
{"name": "list_tasks", "arguments": {"status": "pending", "priority": "high"}}

// 搜索任务
{"name": "search_tasks", "arguments": {"search_text": "关键词", "limit": 10}}

// 高级过滤
{"name": "filter_tasks", "arguments": {"priority": ["high"], "tags": ["重要"]}}

// 获取统计
{"name": "get_task_statistics", "arguments": {}}
```

### 状态管理
```json
// 更新状态
{"name": "update_task_status", "arguments": {"task_id": "ID", "status": "completed"}}

// 获取特定状态任务
{"name": "get_pending_tasks", "arguments": {}}
{"name": "get_in_progress_tasks", "arguments": {}}
{"name": "get_completed_tasks", "arguments": {}}
{"name": "get_blocked_tasks", "arguments": {}}
```

### 层级管理
```json
// 添加子任务关系
{"name": "add_child_task", "arguments": {"parent_id": "父ID", "child_id": "子ID"}}

// 获取层级结构
{"name": "get_task_hierarchy", "arguments": {"task_id": "根ID", "max_depth": 3}}

// 移动任务
{"name": "move_task", "arguments": {"task_id": "ID", "new_parent_id": "新父ID"}}
```

## 📝 参数速查

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
`2024-12-31T23:59:59Z` (ISO 8601)

## 🎯 智能工具组合模式

### 项目创建模式
```python
# 1. 创建主项目
main_task = create_task(title="项目名称", priority="high", tags=["项目"])

# 2. 创建子任务结构
create_task(title="阶段1", parent_id=main_task.id, priority="high")
create_task(title="阶段2", parent_id=main_task.id, priority="medium")
create_task(title="阶段3", parent_id=main_task.id, priority="medium")

# 3. 查看完整结构
get_task_hierarchy(task_id=main_task.id, max_depth=3)
```

### 批量状态更新模式
```python
# 1. 筛选目标任务
tasks = filter_tasks(tags=["开发"], status=["pending", "in_progress"])

# 2. 批量更新状态
task_ids = [task.id for task in tasks.data]
bulk_status_update(task_ids=task_ids, status="completed")
```

### 智能搜索模式
```python
# 1. 关键词搜索
search_results = search_tasks(search_text="网站", limit=10)

# 2. 高级过滤
filtered_tasks = filter_tasks(
    priority=["high", "urgent"],
    status=["pending"],
    tags=["重要"],
    due_before="2024-12-31T23:59:59Z"
)

# 3. 获取统计信息
stats = get_task_statistics()
```

### 用户意图 → 工具映射
- "创建项目" → `create_task` + `add_child_task`
- "我的任务" → `list_tasks` + `get_task_statistics`
- "搜索XX" → `search_tasks` + `filter_tasks`
- "完成了XX" → `search_tasks` + `update_task_status`
- "高优先级任务" → `filter_tasks(priority=["high","urgent"])`
- "项目进度" → `get_task_hierarchy` + 状态分析
- "整理任务" → `list_tasks` + 结构优化建议

### 响应模板
```
✅ 操作成功：{简要说明}
📋 详情：{关键信息}
💡 建议：{下一步操作}
🎯 效果：{预期改进}
```

## ⚠️ 注意事项
1. 必需参数不能省略
2. 日期使用UTC时区
3. 任务ID是UUID格式
4. 数组参数用[]包围
5. 错误时提供友好提示