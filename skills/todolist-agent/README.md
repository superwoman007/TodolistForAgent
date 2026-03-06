# Agent TodoList Skill

这是一个让 Agent 拥有自己待办清单的 OpenClaw Skill，支持 API Key 认证。

## 功能特性

- 🔐 API Key 认证，每个 Agent 独立空间
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

### 2. 启动 TodoList API 后端

```bash
cd apps/api
uvicorn app.main:app --reload --port 8000
```

### 3. 创建 Agent API Key

首次使用需要创建 API Key：

```bash
curl -X POST http://localhost:8000/agent/credentials \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "my-assistant-001",
    "name": "My Personal Assistant"
  }'
```

响应示例：
```json
{
  "agent_id": "my-assistant-001",
  "api_key": "ak_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "name": "My Personal Assistant",
  "created_at": "2026-03-06T13:00:00"
}
```

**保存好你的 API Key！**

### 4. 配置环境变量

编辑 `~/.openclaw/openclaw.json`：

```json
{
  "skills": {
    "entries": {
      "todolist-agent": {
        "enabled": true,
        "env": {
          "TODOLIST_API_URL": "http://localhost:8000",
          "TODOLIST_API_KEY": "ak_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        }
      }
    }
  }
}
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

核心接口（所有接口需要 Authorization header）：
- `POST /agent/credentials` - 创建 API Key（管理接口）
- `POST /agent/todos` - 创建待办
- `GET /agent/todos` - 查询待办
- `GET /agent/todos/check` - 检查到期任务
- `POST /agent/todos/{id}/done` - 标记完成
- `GET /agent/todos/stats` - 统计信息

## 数据隔离

每个 Agent 通过 API Key 认证，数据完全隔离：
- Agent A 只能看到自己的待办
- Agent B 只能看到自己的待办
- 互不干扰

## 数据模型

```
agent_credentials 表：
- agent_id: Agent 唯一标识（主键）
- api_key: API 密钥
- name: Agent 名称
- created_at: 创建时间
- last_used_at: 最后使用时间

agent_todos 表：
- id: 主键
- agent_id: 所属 Agent（外键）
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
- `apps/api/app/models/agent_credential.py` - 凭证模型
- `apps/api/app/models/agent_todo.py` - 待办模型
- `apps/api/app/schemas/agent_credential.py` - 凭证 Schema
- `apps/api/app/schemas/agent_todo.py` - 待办 Schema
- `apps/api/app/routers/agent_credentials.py` - 凭证管理 API
- `apps/api/app/routers/agent_todos.py` - 待办 API
- `apps/api/app/dependencies_agent.py` - 认证依赖注入

## 许可证

MIT License
