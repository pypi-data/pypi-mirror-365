"""
FastMCP服务器实现

使用官方MCP Python SDK的FastMCP创建HTTP传输的MCP服务器，
暴露现有的任务管理功能给AI客户端。
"""

import logging
from typing import Dict, Any, List, Optional

from mcp.server.fastmcp import FastMCP

from .config import TodoConfig
from .services.task_service import TaskService


def create_mcp_server(config: TodoConfig, host: str = "0.0.0.0", port: int = 8000) -> FastMCP:
    """
    创建配置好的FastMCP服务器实例
    
    Args:
        config: Todo MCP配置
        
    Returns:
        配置好的FastMCP服务器实例
    """
    logger = logging.getLogger(__name__)
    logger.info("创建FastMCP服务器实例")
    
    # 创建FastMCP服务器
    mcp = FastMCP(
        name=config.server_name,
        # 使用有状态模式保持会话状态
        stateless_http=False,
        # 配置主机和端口
        host=host,
        port=port
    )
    
    # 注册所有工具
    register_task_tools(mcp, config)
    register_status_tools(mcp, config)
    register_hierarchy_tools(mcp, config)
    register_query_tools(mcp, config)
    
    # 注册LLM指导prompts
    register_llm_prompts(mcp, config)
    
    logger.info(f"FastMCP服务器创建完成，服务器名称: {config.server_name}")
    return mcp


def register_task_tools(mcp: FastMCP, config: TodoConfig) -> None:
    """注册任务管理工具"""
    logger = logging.getLogger(__name__)
    logger.debug("注册任务管理工具")
    
    @mcp.tool()
    async def create_task(
        title: str,
        description: str = "",
        priority: str = "medium",
        tags: Optional[List[str]] = None,
        parent_id: Optional[str] = None,
        due_date: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """创建新任务"""
        from .tools import task_tools
        
        args = {
            "title": title,
            "description": description,
            "priority": priority
        }
        
        if tags is not None:
            args["tags"] = tags
        if parent_id is not None:
            args["parent_id"] = parent_id
        if due_date is not None:
            args["due_date"] = due_date
        if metadata is not None:
            args["metadata"] = metadata
            
        return await task_tools.create_task(
            title=title,
            description=description,
            priority=priority,
            tags=tags,
            parent_id=parent_id,
            due_date=due_date,
            metadata=metadata
        )
    
    @mcp.tool()
    async def update_task(
        task_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        priority: Optional[str] = None,
        tags: Optional[List[str]] = None,
        due_date: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """更新现有任务"""
        from .tools import task_tools
        
        args = {"task_id": task_id}
        
        if title is not None:
            args["title"] = title
        if description is not None:
            args["description"] = description
        if priority is not None:
            args["priority"] = priority
        if tags is not None:
            args["tags"] = tags
        if due_date is not None:
            args["due_date"] = due_date
        if metadata is not None:
            args["metadata"] = metadata
            
        return await task_tools.update_task(
            task_id=task_id,
            title=title,
            description=description,
            priority=priority,
            tags=tags,
            due_date=due_date,
            metadata=metadata
        )
    
    @mcp.tool()
    async def delete_task(
        task_id: str,
        cascade: bool = False
    ) -> Dict[str, Any]:
        """删除任务"""
        from .tools import task_tools
        
        return await task_tools.delete_task(task_id=task_id, cascade=cascade)
    
    @mcp.tool()
    async def get_task(task_id: str) -> Dict[str, Any]:
        """获取单个任务"""
        from .tools import task_tools
        
        return await task_tools.get_task(task_id=task_id)
    
    @mcp.tool()
    async def list_tasks(
        status: Optional[str] = None,
        priority: Optional[str] = None,
        tags: Optional[List[str]] = None,
        parent_id: Optional[str] = None,
        include_completed: bool = True
    ) -> Dict[str, Any]:
        """列出任务"""
        from .tools import task_tools
        
        return await task_tools.list_tasks(
            status=status,
            priority=priority,
            tags=tags,
            parent_id=parent_id,
            include_completed=include_completed
        )
    
    @mcp.tool()
    async def get_task_context(task_id: str) -> Dict[str, Any]:
        """获取任务完整上下文"""
        from .tools import task_tools
        
        return await task_tools.get_task_context(task_id=task_id)


def register_status_tools(mcp: FastMCP, config: TodoConfig) -> None:
    """注册状态管理工具"""
    logger = logging.getLogger(__name__)
    logger.debug("注册状态管理工具")
    
    @mcp.tool()
    async def update_task_status(task_id: str, status: str) -> Dict[str, Any]:
        """更新任务状态"""
        from .tools import status_tools
        
        return await status_tools.update_task_status(task_id=task_id, status=status)
    
    @mcp.tool()
    async def bulk_status_update(task_ids: List[str], status: str) -> Dict[str, Any]:
        """批量更新任务状态"""
        from .tools import status_tools
        
        return await status_tools.bulk_status_update(task_ids=task_ids, status=status)
    
    @mcp.tool()
    async def get_task_status(task_id: str) -> Dict[str, Any]:
        """获取任务状态"""
        from .tools import status_tools
        
        return await status_tools.get_task_status(task_id=task_id)
    
    @mcp.tool()
    async def get_pending_tasks() -> Dict[str, Any]:
        """获取待处理任务"""
        from .tools import status_tools
        
        return await status_tools.get_pending_tasks()
    
    @mcp.tool()
    async def get_in_progress_tasks() -> Dict[str, Any]:
        """获取进行中任务"""
        from .tools import status_tools
        
        return await status_tools.get_in_progress_tasks()
    
    @mcp.tool()
    async def get_blocked_tasks() -> Dict[str, Any]:
        """获取阻塞任务"""
        from .tools import status_tools
        
        return await status_tools.get_blocked_tasks()
    
    @mcp.tool()
    async def get_completed_tasks() -> Dict[str, Any]:
        """获取已完成任务"""
        from .tools import status_tools
        
        return await status_tools.get_completed_tasks()


def register_hierarchy_tools(mcp: FastMCP, config: TodoConfig) -> None:
    """注册层级管理工具"""
    logger = logging.getLogger(__name__)
    logger.debug("注册层级管理工具")
    
    @mcp.tool()
    async def add_child_task(parent_id: str, child_id: str) -> Dict[str, Any]:
        """添加子任务关系"""
        from .tools import hierarchy_tools
        
        return await hierarchy_tools.add_child_task(parent_id=parent_id, child_id=child_id)
    
    @mcp.tool()
    async def remove_child_task(parent_id: str, child_id: str) -> Dict[str, Any]:
        """移除子任务关系"""
        from .tools import hierarchy_tools
        
        return await hierarchy_tools.remove_child_task(parent_id=parent_id, child_id=child_id)
    
    @mcp.tool()
    async def get_task_hierarchy(
        task_id: str,
        max_depth: Optional[int] = None,
        include_ancestors: bool = False
    ) -> Dict[str, Any]:
        """获取任务层级结构"""
        from .tools import hierarchy_tools
        
        return await hierarchy_tools.get_task_hierarchy(
            task_id=task_id,
            max_depth=max_depth,
            include_ancestors=include_ancestors
        )
    
    @mcp.tool()
    async def move_task(task_id: str, new_parent_id: Optional[str] = None) -> Dict[str, Any]:
        """移动任务到新的父任务"""
        from .tools import hierarchy_tools
        
        args = {"task_id": task_id}
        if new_parent_id is not None:
            args["new_parent_id"] = new_parent_id
            
        return await hierarchy_tools.move_task(task_id=task_id, new_parent_id=new_parent_id)


def register_query_tools(mcp: FastMCP, config: TodoConfig) -> None:
    """注册查询工具"""
    logger = logging.getLogger(__name__)
    logger.debug("注册查询工具")
    
    @mcp.tool()
    async def search_tasks(
        search_text: str,
        search_fields: Optional[List[str]] = None,
        status: Optional[List[str]] = None,
        priority: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        include_completed: bool = True,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> Dict[str, Any]:
        """搜索任务"""
        from .tools import query_tools
        
        return await query_tools.search_tasks(
            search_text=search_text,
            search_fields=search_fields,
            status=status,
            priority=priority,
            tags=tags,
            include_completed=include_completed,
            limit=limit,
            offset=offset
        )
    
    @mcp.tool()
    async def filter_tasks(
        status: Optional[List[str]] = None,
        priority: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        tags_all: Optional[List[str]] = None,
        parent_id: Optional[str] = None,
        has_parent: Optional[bool] = None,
        has_children: Optional[bool] = None,
        has_due_date: Optional[bool] = None,
        created_after: Optional[str] = None,
        created_before: Optional[str] = None,
        updated_after: Optional[str] = None,
        updated_before: Optional[str] = None,
        due_after: Optional[str] = None,
        due_before: Optional[str] = None,
        title_contains: Optional[str] = None,
        description_contains: Optional[str] = None,
        include_completed: bool = True,
        limit: Optional[int] = None,
        offset: int = 0,
        sort_by: str = "created_at",
        sort_desc: bool = True
    ) -> Dict[str, Any]:
        """高级任务过滤"""
        from .tools import query_tools
        
        return await query_tools.filter_tasks(
            status=status,
            priority=priority,
            tags=tags,
            tags_all=tags_all,
            parent_id=parent_id,
            has_parent=has_parent,
            has_children=has_children,
            has_due_date=has_due_date,
            created_after=created_after,
            created_before=created_before,
            updated_after=updated_after,
            updated_before=updated_before,
            due_after=due_after,
            due_before=due_before,
            title_contains=title_contains,
            description_contains=description_contains,
            include_completed=include_completed,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_desc=sort_desc
        )
    
    @mcp.tool()
    async def get_task_statistics() -> Dict[str, Any]:
        """获取任务统计信息"""
        from .tools import query_tools
        
        return await query_tools.get_task_statistics()


def register_llm_prompts(mcp: FastMCP, config: TodoConfig) -> None:
    """注册LLM指导prompts"""
    logger = logging.getLogger(__name__)
    logger.debug("注册LLM指导prompts")
    
    @mcp.prompt()
    async def todo_system_guide() -> str:
        """Todo MCP系统使用指南 - 为LLM提供完整的系统使用说明"""
        return """# Todo MCP 系统指南

## 🎯 系统概述
你现在可以访问一个强大的任务管理系统，提供完整的任务创建、管理、状态跟踪和层级组织功能。

## 🛠️ 核心工具

### 任务管理
- `create_task`: 创建新任务
- `update_task`: 更新现有任务
- `get_task`: 获取单个任务详情
- `list_tasks`: 列出任务（支持基础过滤）
- `delete_task`: 删除任务

### 状态管理
- `update_task_status`: 更新任务状态
- `get_pending_tasks`: 获取待处理任务
- `get_in_progress_tasks`: 获取进行中任务
- `get_completed_tasks`: 获取已完成任务
- `get_blocked_tasks`: 获取阻塞任务

### 搜索查询
- `search_tasks`: 全文搜索任务
- `filter_tasks`: 高级过滤（支持多种条件）
- `get_task_statistics`: 获取任务统计信息

### 层级管理
- `add_child_task`: 建立父子任务关系
- `remove_child_task`: 移除父子关系
- `get_task_hierarchy`: 获取任务层级结构
- `move_task`: 移动任务到新的父任务下

## 📝 参数规范

### 优先级 (priority)
- `low`: 低优先级
- `medium`: 中等优先级（默认）
- `high`: 高优先级
- `urgent`: 紧急

### 状态 (status)
- `pending`: 待处理（默认）
- `in_progress`: 进行中
- `completed`: 已完成
- `blocked`: 阻塞
- `cancelled`: 已取消

### 日期格式
使用ISO 8601格式：`2024-12-31T23:59:59Z`

## 🎨 最佳实践

1. **任务创建**: 标题简洁明确，描述详细具体
2. **优先级设置**: 根据紧急程度和重要性合理设置
3. **标签使用**: 使用有意义的标签便于分类和搜索
4. **层级组织**: 大项目分解为子任务，建立清晰的层级结构
5. **状态跟踪**: 及时更新任务状态，保持信息准确性

## 💡 智能建议
- 主动建议任务分解
- 根据用户习惯调整默认设置
- 提供任务优化建议
- 智能识别任务关系

记住：你的目标是成为用户最得力的任务管理助手！"""

    @mcp.prompt()
    async def quick_reference() -> str:
        """快速参考 - 常用工具和参数速查"""
        return """# 🚀 Todo MCP 快速参考

## 常用工具调用示例

### 创建任务
```json
{
  "name": "create_task",
  "arguments": {
    "title": "任务标题",
    "description": "详细描述",
    "priority": "high",
    "tags": ["标签1", "标签2"],
    "due_date": "2024-12-31T23:59:59Z"
  }
}
```

### 搜索任务
```json
{
  "name": "search_tasks",
  "arguments": {
    "search_text": "关键词",
    "status": ["pending", "in_progress"],
    "limit": 10
  }
}
```

### 更新状态
```json
{
  "name": "update_task_status",
  "arguments": {
    "task_id": "任务ID",
    "status": "completed"
  }
}
```

### 高级过滤
```json
{
  "name": "filter_tasks",
  "arguments": {
    "priority": ["high", "urgent"],
    "tags": ["重要"],
    "created_after": "2024-01-01T00:00:00Z",
    "include_completed": false
  }
}
```

## 参数速查
- **优先级**: low, medium, high, urgent
- **状态**: pending, in_progress, completed, blocked, cancelled
- **日期**: ISO 8601格式 (YYYY-MM-DDTHH:MM:SSZ)

## 响应模板
```
✅ 操作成功：{简要说明}
📋 详情：{关键信息}
💡 建议：{下一步操作}
```"""

    @mcp.prompt()
    async def natural_language_parsing() -> str:
        """自然语言解析指南 - 如何理解用户的自然语言输入"""
        return """# 🗣️ 自然语言解析指南

## 任务创建语法识别

### 基础模式
- "创建任务：{标题}" → create_task
- "添加待办：{标题}" → create_task
- "记录任务：{标题}" → create_task

### 优先级识别
- "重要|紧急|急|火急" → urgent
- "高优先级|重点|关键" → high
- "一般|普通|正常" → medium
- "低优先级|不急|有空" → low

### 时间表达
- "明天" → 明天日期
- "下周五" → 计算具体日期
- "月底" → 当月最后一天
- "3天后" → 当前日期+3天

### 状态识别
- "开始做|开始了|在做" → in_progress
- "完成了|做完了|搞定" → completed
- "卡住了|有问题|阻塞" → blocked
- "暂停|先放放" → pending

## 查询意图识别

### 搜索模式
- "我的任务" → list_tasks
- "搜索XX" → search_tasks
- "找XX相关" → search_tasks
- "高优先级任务" → filter_tasks

### 过滤组合
- "高优先级的进行中任务" → filter_tasks(priority=["high"], status=["in_progress"])
- "开发相关的未完成任务" → filter_tasks(tags=["开发"], status=["pending","in_progress"])

## 层级管理识别
- "分解任务" → 创建子任务
- "XX是YY的子任务" → add_child_task
- "把A移到B下面" → move_task
- "项目结构" → get_task_hierarchy

## 智能建议触发
- 大任务创建后 → 建议分解
- 多个高优先级任务 → 建议优先级调整
- 长期未完成任务 → 建议重新评估

记住：理解用户意图比严格匹配语法更重要！"""

    @mcp.prompt()
    async def error_handling_guide() -> str:
        """错误处理指南 - 如何优雅地处理各种错误情况"""
        return """# 🛠️ 错误处理指南

## 常见错误类型

### 1. 任务不存在
**错误**: 找不到指定的任务ID
**处理**: "抱歉，我找不到这个任务。让我为你列出当前的任务。"
**操作**: 调用 list_tasks 显示可用任务

### 2. 参数格式错误
**错误**: 日期格式、优先级值等参数错误
**处理**: 自动修正并重试，不暴露技术错误
**示例**: "你是指 2024-12-25 吗？" 然后使用修正后的参数

### 3. 权限或系统错误
**错误**: 工具调用失败、系统不可用
**处理**: 提供替代方案或建议稍后重试
**示例**: "系统暂时繁忙，让我尝试其他方式帮你记录这个任务。"

## 优雅降级策略

### 工具不可用时
1. 提供手动记录建议
2. 建议使用其他工具
3. 承诺稍后处理

### 数据不完整时
1. 请求补充信息
2. 使用合理默认值
3. 提供多个选项让用户选择

### 网络或连接问题
1. 建议稍后重试
2. 提供离线替代方案
3. 保存用户输入以便后续处理

## 错误响应模板

```python
error_templates = {
    "not_found": "😅 没找到这个任务，让我列出你当前的任务吧",
    "invalid_date": "🤔 时间格式有点问题，你是指 {suggested_date} 吗？",
    "missing_info": "📝 需要更多信息：{missing_fields}",
    "permission": "🔒 这个操作需要权限，让我尝试其他方式",
    "system_error": "⚠️ 系统暂时繁忙，稍后再试或让我用其他方式帮你"
}
```

## 用户体验原则
1. **永远不要让用户感到困惑**
2. **提供明确的下一步建议**
3. **保持积极和帮助的态度**
4. **将技术问题转化为用户友好的语言**

记住：错误是改善用户体验的机会！"""

    @mcp.prompt()
    async def conversation_patterns() -> str:
        """对话模式指南 - 如何与用户进行自然流畅的对话"""
        return """# 💬 对话模式指南

## 对话流程设计

### 标准流程
1. **理解需求** - 解析用户意图
2. **执行操作** - 调用相应工具
3. **确认结果** - 反馈操作结果
4. **建议下一步** - 主动提供后续建议

### 多轮对话管理
```
轮次1: 用户 "创建一个项目任务"
轮次2: 系统 "好的，项目名称是什么？"
轮次3: 用户 "移动应用开发"
轮次4: 系统 "✅ 已创建项目：移动应用开发。需要我帮你分解成具体的开发阶段吗？"
```

## 响应风格指南

### 成功操作响应
```
✅ 已创建任务：{任务标题}
📋 任务ID: {task_id}
⏰ 截止时间: {due_date}
🏷️ 标签: {tags}

💡 需要我帮你分解这个任务或设置提醒吗？
```

### 查询结果展示
```
📋 你的任务列表：

🔴 高优先级：
• {任务1} - {状态}
• {任务2} - {状态}

🟡 中优先级：
• {任务3} - {状态}

📊 统计：已完成 {完成数量}个 | 进行中 {进行中数量}个 | 待处理 {待处理数量}个
```

### 状态更新确认
```
✅ 任务状态已更新
📋 {任务标题}
🔄 {旧状态} → {新状态}

{根据新状态给出相应建议}
```

## 主动建议模式

### 任务创建后
- 大任务 → "需要分解成子任务吗？"
- 无截止日期 → "要设置截止时间吗？"
- 无标签 → "添加一些标签便于分类？"

### 任务完成后
- "🎉 恭喜完成！还有其他相关任务需要处理吗？"
- "要不要看看其他待处理的任务？"

### 任务过载时
- "你有很多高优先级任务，建议先完成最紧急的几个。"
- "要不要调整一些任务的优先级？"

## 上下文保持

### 记住关键信息
- 最近创建的任务ID
- 当前讨论的项目
- 用户的使用习惯
- 常用的标签和优先级

### 引用上下文
- "刚才创建的那个任务"
- "你提到的项目"
- "按照你平时的习惯"

## 个性化适应

### 学习用户偏好
- 常用的优先级设置
- 喜欢的标签分类
- 时间管理风格
- 项目组织方式

### 调整交互风格
- 简洁型用户 → 减少废话，直接操作
- 详细型用户 → 提供更多解释和选项
- 新手用户 → 更多指导和建议

记住：好的对话让用户感觉像在和一个理解他们的助手交流！"""