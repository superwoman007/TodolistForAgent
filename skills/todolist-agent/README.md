# Agent TodoList Skill

这是一个让 Agent 拥有自己待办清单的 OpenClaw Skill。

## 功能特性

- ✅ Agent 自己创建和管理待办事项
- 🔄 支持重复任务（每天/每周/每月）
- ⏰ 定期巡检到期任务并自动执行
- 📊 任务统计和进度跟踪
- 🎯 优先级管理

## 安装

### 1. 复制 Skill 到 OpenClaw

```bash
# 方式一：复制到 workspace skills 目录
cp -r skills/todolist-agent <your-workspace>/skills/

# 方式二：复制到全局 skills 目录
cp -r skills/todolist-agent ~/.openclaw/skills/
```

### 2. 配置环境变量

编辑 `~/.openclaw/openclaw.json`：

```json
{
  "skills": {
    "entries": {
      "todolist-agent": {
        "enabled": true,
        "env": {
          "TODOLIST_API_URL": "http://localhost:8000"
        }
      }
    }
  }
}
```

### 3. 启动 TodoList API 后端

```bash
cd apps/api
uvicorn app.main:app --reload --port 8000
```

## 使用示例

### 用户交互

```
用户：帮我每天早上9点发天气预报
Agent：✅ 已添加到我的待办清单：每天早上9点发天气预报

用户：你现在有哪些待办？
Agent：📋 我的待办清单：
       1. 🔴 每天早上9点发天气预报 [待执行] - 明天 09:00
       2. 🟡 每周五汇总工作 [待执行] - 周五 17:00
```

### Agent 自动巡检

Agent 会每 30 分钟自动检查待办清单，执行到期任务。

## API 接口

详见 `SKILL.md` 文件中的完整 API 文档。

核心接口：
- `POST /agent/todos` - 创建待办
- `GET /agent/todos` - 查询待办
- `GET /agent/todos/check` - 检查到期任务
- `POST /agent/todos/{id}/done` - 标记完成
- `GET /agent/todos/stats` - 统计信息

## 数据模型

```
agent_todos 表：
- id: 主键
- title: 任务标题
- description: 执行说明
- status: pending / done / failed
- priority: low / normal / high / urgent
- due_at: 截止时间
- repeat_rule: none / daily / weekly / monthly
- result: 执行结果
```

## 开发

后端代码位于：
- `apps/api/app/models/agent_todo.py` - 数据模型
- `apps/api/app/schemas/agent_todo.py` - 请求/响应模型
- `apps/api/app/routers/agent_todos.py` - API 路由

## 许可证

MIT License
