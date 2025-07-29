# 任务管理语法指南

## 🎯 自然语言解析规则

### 任务创建语法
用户输入 → 解析规则 → 工具调用

#### 基础创建
```
用户: "创建任务：完成项目报告"
解析: title="完成项目报告", priority="medium"

用户: "添加一个重要任务：客户会议准备"  
解析: title="客户会议准备", priority="high"

用户: "记录待办：明天买菜"
解析: title="买菜", due_date="明天日期"
```

#### 复杂创建
```
用户: "我需要在下周五前完成网站重构，这很紧急，标签是开发和前端"
解析: {
  "title": "网站重构",
  "due_date": "下周五日期",
  "priority": "urgent",
  "tags": ["开发", "前端"]
}
```

### 优先级识别
```
关键词 → 优先级映射：
"重要|紧急|急|火急" → urgent
"高优先级|重点|关键" → high  
"一般|普通|正常" → medium
"低优先级|不急|有空" → low
```

### 时间表达解析
```
自然语言 → ISO日期：
"明天" → 明天日期T23:59:59Z
"下周五" → 计算具体日期
"月底" → 当月最后一天
"3天后" → 当前日期+3天
"12月25日" → 2024-12-25T23:59:59Z
```

### 状态识别
```
用户表达 → 状态映射：
"开始做|开始了|在做" → in_progress
"完成了|做完了|搞定" → completed
"卡住了|有问题|阻塞" → blocked
"暂停|先放放|等等" → pending
"取消|不做了|算了" → cancelled
```

## 🔍 查询语法解析

### 搜索意图识别
```
用户输入模式 → 工具选择：

"我的任务" → list_tasks
"所有任务" → list_tasks(include_completed=true)
"待办事项" → list_tasks(status="pending")

"搜索XX" → search_tasks(search_text="XX")
"找XX相关" → search_tasks(search_text="XX")

"高优先级任务" → filter_tasks(priority=["high","urgent"])
"本周任务" → filter_tasks(created_after="本周开始")
"项目相关" → filter_tasks(tags=["项目"])
```

### 过滤条件组合
```
用户: "找出高优先级的进行中任务"
解析: filter_tasks({
  "priority": ["high", "urgent"],
  "status": ["in_progress"]
})

用户: "看看开发相关的未完成任务"
解析: filter_tasks({
  "tags": ["开发"],
  "status": ["pending", "in_progress", "blocked"]
})
```

## 🌳 层级管理语法

### 项目分解识别
```
用户表达 → 层级操作：

"这个任务分解一下" → 创建子任务
"XX是YY的子任务" → add_child_task
"把A移到B下面" → move_task
"看看项目结构" → get_task_hierarchy
```

### 关系建立
```
用户: "网站重构项目包含：前端开发、后端开发、测试"
操作序列:
1. create_task("网站重构项目") → 获得parent_id
2. create_task("前端开发", parent_id=parent_id)
3. create_task("后端开发", parent_id=parent_id)  
4. create_task("测试", parent_id=parent_id)
```

## 📊 智能建议语法

### 上下文感知
```
场景1: 用户刚创建了大任务
建议: "这个任务比较复杂，需要我帮你分解成几个子任务吗？"

场景2: 用户有很多高优先级任务
建议: "你有{数量}个高优先级任务，建议先完成最紧急的几个。"

场景3: 任务长期未完成
建议: "这个任务创建了{天数}天还未完成，是否需要调整或分解？"
```

### 批量操作识别
```
用户: "把这几个任务都标记为完成"
解析: 需要先确定"这几个"指哪些任务，然后bulk_status_update

用户: "所有开发任务改为高优先级"
解析: 
1. filter_tasks(tags=["开发"])
2. 对结果批量update_task(priority="high")
```

## 🎨 响应生成规则

### 成功响应模板
```python
def format_success_response(operation, task_data):
    templates = {
        "create": "✅ 已创建任务：{title}\n📋 ID: {id}\n⏰ 截止: {due_date}",
        "update": "✅ 任务已更新：{title}\n🔄 变更: {changes}",
        "complete": "🎉 任务完成：{title}\n📊 用时: {duration}",
        "list": "📋 找到 {count} 个任务：\n{task_list}"
    }
    return templates[operation].format(**task_data)
```

### 错误处理模板
```python
def format_error_response(error_type, context):
    templates = {
        "not_found": "😅 没找到这个任务，让我列出你当前的任务吧",
        "invalid_date": "🤔 时间格式有点问题，你是指 {suggested_date} 吗？",
        "missing_info": "📝 需要更多信息：{missing_fields}",
        "permission": "🔒 这个操作需要权限，让我尝试其他方式"
    }
    return templates[error_type].format(**context)
```

## 🔄 对话流程控制

### 多轮对话管理
```
轮次1: 用户提出需求
轮次2: 系统执行操作并确认
轮次3: 用户补充信息或确认
轮次4: 系统完成操作并建议下一步

示例:
用户: "创建一个项目任务"
系统: "好的，项目名称是什么？"
用户: "移动应用开发"
系统: "✅ 已创建项目：移动应用开发。需要我帮你分解成具体的开发阶段吗？"
```

### 上下文保持
```python
class ConversationContext:
    last_created_task_id = None
    last_searched_results = []
    current_project_id = None
    user_preferences = {
        "default_priority": "medium",
        "preferred_tags": ["工作", "个人"],
        "timezone": "Asia/Shanghai"
    }
```

## 💡 高级语法特性

### 条件逻辑
```
用户: "如果明天下雨就把户外活动改为室内"
解析: 创建条件任务或提醒

用户: "完成A任务后自动开始B任务"
解析: 建立任务依赖关系
```

### 批量模式
```
用户: "批量创建本周的日常任务"
解析: 根据模板批量创建任务

用户: "把所有过期任务延期一周"
解析: 批量更新due_date
```

### 模板应用
```
用户: "按照上次的项目模板创建新项目"
解析: 复制之前项目的任务结构
```

记住：语法解析的目标是让用户用最自然的方式表达需求，系统智能理解并执行相应操作！