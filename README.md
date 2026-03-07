# Agent TodoList

> Give your AI agent a real task system — todos, subtasks, recurring schedules, priorities, and execution records.

一个给 AI Agent 用的待办系统：不仅能记任务，还能让 Agent **自主查询、执行、回写结果**。

如果你在做 OpenClaw、自动化助手、AI 管家、工作流 Agent，这个项目就是把“提醒事项”升级成“Agent 可执行任务栈”的那块基础设施。

## Why This Project

大多数 Todo 工具是给人点点点用的，不是给 Agent 调 API 用的。

`Agent TodoList` 的目标很直接：

- 让 Agent 拥有自己的任务队列
- 让每个 Agent 拥有独立认证和数据空间
- 让复杂任务可以拆成 subtasks 分步完成
- 让周期任务自动生成下一次执行项
- 让任务结果可以被记录、追踪、统计

一句话：**它不是一个“待办 UI”，而是一个“给 AI Agent 用的任务后端”。**

## Features

- 🔐 **Per-Agent API Key**：每个 Agent 独立身份、独立数据隔离
- ✅ **Agent-native Todo API**：面向 Agent 设计，不是把人类产品硬改成接口
- 🧩 **Subtasks**：复杂任务可拆解、可逐步完成
- 🔁 **Recurring Tasks**：支持 daily / weekly / monthly 周期任务
- ⏰ **Due Task Checking**：可轮询到期任务，适合定时执行器
- 📊 **Execution Stats**：待办、完成、失败、逾期一目了然
- 🪶 **Lightweight Stack**：FastAPI + SQLite，启动快，部署轻
- 🤖 **OpenClaw Skill Included**：开箱可接入 Agent 工作流

## Typical Use Cases

- AI 助手定时检查邮件、日历、消息
- Agent 自动执行周期巡检任务
- 复杂工作拆成多步 subtasks 顺序推进
- 智能秘书记录“之后帮我做”的事项
- 私人自动化系统的任务中枢 / Agent memory layer

## How It Works

```text
User / Scheduler
      ↓
OpenClaw Agent / Other AI Agent
      ↓
Agent TodoList API
      ↓
Todos / Subtasks / Recurring Rules / Results
```

典型流程：

1. 用户或系统创建任务
2. Agent 定期调用 `/agent/todos/check`
3. 获取已到期任务并执行
4. 成功后标记 done，失败则标记 fail
5. 如果是重复任务，系统自动生成下一次任务

## Project Structure

```text
.
├── apps/
│   └── api/
│       ├── app/
│       │   ├── main.py
│       │   ├── dependencies_agent.py
│       │   ├── db/
│       │   ├── models/
│       │   ├── routers/
│       │   └── schemas/
│       └── todolist.db
├── skills/
│   └── todolist-agent/
│       ├── SKILL.md
│       └── README.md
├── LICENSE
└── README.md
```

## Quick Start

### 1. Install dependencies

```bash
pip install fastapi uvicorn sqlalchemy
```

### 2. Start the API server

```bash
cd apps/api
uvicorn app.main:app --reload --port 8000
```

启动后可访问：

- Health check: `http://localhost:8000/health`
- Swagger docs: `http://localhost:8000/docs`

### 3. Create an API key for your agent

```bash
curl -X POST http://localhost:8000/agent/credentials \
  -H "Content-Type: application/json" \
  -d '{"agent_id": "my-agent", "name": "My Agent"}'
```

### 4. Create the first todo

```bash
curl -X POST http://localhost:8000/agent/todos \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Check important emails",
    "description": "Review inbox and summarize urgent items",
    "priority": "high"
  }'
```

### 5. Let the agent poll due tasks

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  http://localhost:8000/agent/todos/check
```

## OpenClaw Integration

项目已经附带 `skills/todolist-agent`，可直接接入 OpenClaw。

```bash
cp -r skills/todolist-agent ~/.openclaw/skills/
```

在 `~/.openclaw/openclaw.json` 中配置：

```json
{
  "skills": {
    "entries": {
      "todolist-agent": {
        "enabled": true,
        "env": {
          "TODOLIST_API_URL": "http://localhost:8000",
          "TODOLIST_API_KEY": "ak_your_key_here"
        }
      }
    }
  }
}
```

这样你的 Agent 就能：

- 创建任务
- 查询待办
- 获取到期任务
- 标记完成/失败
- 管理 subtasks

## Example Scenarios

### Scenario 1: recurring reminder

用户说：

> 每天早上 9 点提醒我看邮件

Agent 可以创建一个 `daily` 周期任务；每次完成后，系统自动生成下一次任务。

### Scenario 2: complex work execution

用户说：

> 帮我准备周五汇报

Agent 可以拆成：

- 收集数据
- 生成大纲
- 制作幻灯片
- 预演汇报

每一步都能独立追踪，不会一坨糊在一起。

### Scenario 3: autonomous periodic checks

Agent 每 30 分钟调用一次：

```http
GET /agent/todos/check
```

拿到到期任务后自动执行，再写回执行结果。

## Core API

### Health

- `GET /health`

### Agent credentials

- `POST /agent/credentials`

### Todos

- `GET /agent/todos`
- `POST /agent/todos`
- `GET /agent/todos/check`
- `GET /agent/todos/stats`
- `GET /agent/todos/{id}`
- `PUT /agent/todos/{id}`
- `DELETE /agent/todos/{id}`
- `POST /agent/todos/{id}/done`
- `POST /agent/todos/{id}/fail`

### Subtasks

- `GET /agent/todos/{id}/subtasks`
- `POST /agent/todos/{id}/subtasks`
- `PUT /agent/todos/{id}/subtasks/{sub_id}`
- `DELETE /agent/todos/{id}/subtasks/{sub_id}`
- `POST /agent/todos/{id}/subtasks/{sub_id}/done`

完整请求格式可查看：

- `skills/todolist-agent/SKILL.md`
- `http://localhost:8000/docs`

## Why It Can Be Interesting on GitHub

这个项目比较容易让人点星，核心是它踩在几个很容易传播的话题上：

- `AI Agent infrastructure`
- `OpenClaw ecosystem`
- `autonomous task execution`
- `personal AI assistant`
- `FastAPI micro-backend`

它不是泛泛而谈的 “AI TODO App”，而是一个非常具体、很容易让开发者代入自己项目的基础模块：

> “如果我的 Agent 也需要一个能执行、能回写、能周期调度的任务系统，我是不是直接能拿这个用？”

这类仓库更容易获得收藏、复用、二次开发和转发。

## Roadmap

- [ ] Docker compose 一键启动
- [ ] PostgreSQL support
- [ ] Webhook / event callbacks
- [ ] Task labels / tags
- [ ] Retry policy for failed tasks
- [ ] Agent execution logs
- [ ] Multi-tenant admin dashboard
- [ ] MCP / tool-calling friendly schema exports

## Tech Stack

- Python
- FastAPI
- SQLAlchemy
- SQLite
- OpenClaw Skill

## License

MIT

---

如果你在做 AI Agent、自动化助手、数字管家，欢迎 star、fork、提 issue，一起把“Agent 的任务系统”做成真正可复用的基础设施。
