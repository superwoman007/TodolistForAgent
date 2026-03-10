# Agent TodoList

> The missing task backend for AI agents.

为 AI Agent 而生的 Todo 后端：支持 **任务创建、子任务拆解、周期调度、到期检查、执行回写、结果追踪**。

不是给人手动点按钮的 Todo App。  
而是给 **OpenClaw / AI Assistant / Autonomous Agent** 直接接入的任务系统。

## Why People Star This

现在很多 Agent 能聊天、能调用工具、能写代码，**但没有一个真正像样的任务系统**：

- 任务记不住
- 复杂工作拆不开
- 到点了不会主动执行
- 做完了没有结果沉淀
- 周期任务全靠临时拼逻辑

`Agent TodoList` 就是补这块空白的。

它把“提醒事项”升级成了 **Agent 可执行任务基础设施**：

- Agent 自己创建任务
- Agent 自己轮询到期任务
- Agent 自己执行并回写结果
- 复杂任务可拆成 subtasks
- 重复任务自动生成下一次

一句话：

> **If your agent can think and act, it also needs a task system.**

## Highlights

- 🔐 **Per-Agent Isolation**：每个 Agent 独立 API Key、独立任务空间
- ✅ **Agent-First API**：从 Agent 调用视角设计，不是人类产品接口魔改
- 🧩 **Subtasks Built In**：适合拆解复杂任务和多步骤执行
- 🔁 **Recurring Tasks**：支持 daily / weekly / monthly 周期任务
- ⏰ **Due Task Polling**：天然适合 cron、heartbeat、scheduler、worker
- 📊 **Execution Trace**：记录待办、完成、失败、逾期与执行结果
- 🪶 **Lightweight & Hackable**：FastAPI + SQLite，轻量、直观、容易二次开发
- 🤖 **OpenClaw Skill Included**：不是“兼容”，是已经能接

## What You Can Build With It

- 会定时提醒、定时检查、定时执行的 AI 助手
- 能把复杂任务拆成多步推进的 Autonomous Agent
- 私人数字秘书 / Personal AI OS
- 具备“之后帮我做这件事”能力的聊天机器人
- 你自己 Agent stack 里的任务中台

## Demo Mindset

想象一下你的 Agent 收到这些话：

> “每天早上 9 点提醒我处理邮件。”  
> “周五前帮我准备汇报，拆成几步慢慢做。”  
> “每 30 分钟检查一次有没有到期任务。”

大部分项目做到“理解这句话”就结束了。  
这个项目解决的是下一步：

**理解之后，怎么把任务可靠地存起来、追踪起来、执行起来。**

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

典型执行流：

1. 用户或系统创建任务
2. Agent 调用 `/agent/todos/check`
3. 获取已到期任务
4. 执行任务或逐个执行 subtasks
5. 成功则标记 done，失败则标记 fail
6. 若为周期任务，系统自动生成下一次任务

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

### Command Shortcuts

```bash
make install   # Install dependencies
make run       # Start the API server
make test      # Run test suite
```

### 1. Install dependencies

```bash
pip install -r requirements.txt
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

**Priority ordering:** When polling due tasks via `/agent/todos/check`, tasks are ordered by priority weight (urgent > high > normal > low), then by due date.

**Monthly recurrence:** Monthly recurring tasks advance by calendar month (e.g., Jan 31 → Feb 29), not by fixed 30 days. End-of-month dates are clamped to the last day of the target month.

## Testing

Run the test suite with pytest:

```bash
cd apps/api
pytest tests/ -v
```

Test coverage includes:
- Health check endpoint
- Credential creation and validation
- Authentication failure cases
- Todo CRUD operations
- Recurring task behavior
- Subtask management flow

## OpenClaw Integration

项目已经附带 `skills/todolist-agent`，可直接接入 OpenClaw。

```bash
cp -r skills/todolist-agent ~/.openclaw/skills/
```

### Recommended runtime config (no OpenClaw restart)

Do **not** rely on editing `~/.openclaw/openclaw.json` for per-agent TodoList connection settings, because that may require restarting OpenClaw.

Instead, provide a separate runtime config file:

`~/.openclaw/todolist-agent.json`

Example:

```json
{
  "apiUrl": "https://todo.yourdomain.com",
  "apiKey": "ak_server_issued_for_this_agent",
  "agentId": "agent-issued-by-server"
}
```

Recommended behavior for host agents using this skill:
- install the skill once
- update `~/.openclaw/todolist-agent.json` when connection info changes
- avoid using `~/.openclaw/openclaw.json` for these per-agent runtime values

### Backward-compatible env mode

If a host environment already injects runtime env vars without requiring restart, the skill may still use:

- `TODOLIST_API_URL`
- `TODOLIST_API_KEY`

But this should be treated as a compatibility path, not the preferred setup for centrally managed agents.

### Central server mode

If you host TodoList as a central server for other agents, those agents should:

1. install the `todolist-agent` skill locally
2. run the initialization script to configure runtime settings (see below)
3. point `apiUrl` to **your** hosted backend
4. use a **server-issued dedicated API key** for that agent

### Initialization script for centrally managed agents

For centrally managed agents, use the init script to configure runtime settings without editing `openclaw.json`:

```bash
# Clone or copy the repository
git clone https://github.com/yourrepo/TodoList.git
cd TodoList

# Install the skill
cp -r skills/todolist-agent ~/.openclaw/skills/

# Initialize runtime config (required for skill to work)
./scripts/todolist-agent-init.sh \
  --api-url https://todo.yourdomain.com \
  --api-key ak_server_issued_for_this_agent \
  --agent-id agent-issued-by-server

# Optional: also set up cron patrol (every 30 minutes)
./scripts/todolist-agent-init.sh \
  --api-url https://todo.yourdomain.com \
  --api-key ak_server_issued_for_this_agent \
  --agent-id agent-issued-by-server \
  --cron
```

The init script:
- Creates/updates `~/.openclaw/todolist-agent.json` with your credentials
- Is idempotent (safe to re-run; only updates if values change)
- With `--cron`, creates or updates an **OpenClaw cron job** that patrols every 30 minutes

To reconfigure later, simply run the script again with new values.

### Current identity model (important)

Current versions use a **simple non-recoverable local identity model**:

- the local agent configuration acts as the agent's current identity binding
- if that local binding/config is lost, re-initializing the agent is treated as a **new agent registration**
- a new registration gets a **new task space**
- recovering the old space after local identity loss is **not supported yet**

This is an intentional simplification for the current phase.

接入后你的 Agent 可以：

- 创建任务
- 查询待办
- 拉取到期任务
- 标记完成 / 失败
- 管理 subtasks
- 构建自己的任务循环

## Example Scenarios

### 1. Recurring reminder

用户说：

> 每天早上 9 点提醒我看邮件

Agent 创建一个 `daily` 周期任务；每次完成后，系统自动生成下一次。

### 2. Complex task execution

用户说：

> 帮我准备周五汇报

Agent 可以拆成：

- 收集数据
- 生成大纲
- 制作幻灯片
- 预演汇报

每一步都能独立追踪，而不是只留下一个“准备汇报”的大黑盒。

### 3. Autonomous periodic checks

Agent 每 30 分钟调用一次：

```http
GET /agent/todos/check
```

拿到到期任务后自动执行，再把结果写回系统。

## Core API

### Health

- `GET /health`

### Agent credentials

- `POST /agent/credentials`

### Admin Protection

Credential management endpoints (`GET /agent/credentials`, `DELETE /agent/credentials/{agent_id}`) require an admin token. Set the `ADMIN_TOKEN` environment variable to protect these admin-style operations:

```bash
export ADMIN_TOKEN=your_secret_token
```

Requests to protected endpoints must include the token in the Authorization header:

```bash
curl -X GET http://localhost:8000/agent/credentials \
  -H "Authorization: Bearer your_secret_token"
```

Credential creation (`POST /agent/credentials`) remains open for bootstrap purposes.

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

## Why This Repo Has Potential

这个仓库容易吸引开发者，不是因为它“功能很多”，而是因为它的定位非常清晰：

- 它踩中 `AI Agent infrastructure`
- 它解决的是一个真实空缺，不是伪需求
- 它够小，开发者一眼能看懂
- 它够实用，别人拿去就能塞进自己项目里
- 它适合做独立模块，也适合做大系统一部分

这类项目最容易出现一句让人想 star 的反应：

> “卧槽，这不就是我正想给 Agent 补的那块吗？”

## Roadmap

- [ ] Docker Compose 一键启动
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

如果你也觉得 **Agent 不该只有大脑和工具，还该有任务系统**，欢迎 star、fork、提 issue，一起把这块基础设施做扎实。