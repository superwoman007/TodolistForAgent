# Agent TodoList API

一个为 AI Agent 提供自主任务管理能力的 OpenClaw Skill 后端。

## 功能特性

- 🔐 API Key 认证，每个 Agent 独立空间
- ✅ Agent 自主创建和管理待办事项
- 📋 支持子任务，拆分复杂任务
- 🔄 支持重复任务（每天/每周/每月）
- ⏰ 定期巡检到期任务并自动执行
- 📊 任务统计和进度跟踪

## 项目结构

```
├── apps/api/                    # FastAPI 后端
│   └── app/
│       ├── main.py              # 应用入口
│       ├── dependencies_agent.py # API Key 认证
│       ├── db/                  # 数据库（SQLite）
│       ├── models/              # 数据模型
│       │   ├── agent_credential.py
│       │   ├── agent_todo.py
│       │   └── agent_subtask.py
│       ├── schemas/             # Pydantic Schema
│       │   ├── agent_credential.py
│       │   ├── agent_todo.py
│       │   └── agent_subtask.py
│       └── routers/             # API 路由
│           ├── agent_credentials.py
│           ├── agent_todos.py
│           └── agent_subtasks.py
└── skills/todolist-agent/       # OpenClaw Skill
    ├── SKILL.md                 # Skill 定义
    └── README.md
```

## 快速开始

### 1. 安装依赖

```bash
pip install fastapi uvicorn sqlalchemy
```

### 2. 启动服务

```bash
cd apps/api
uvicorn app.main:app --reload --port 8000
```

### 3. 创建 Agent API Key

```bash
curl -X POST http://localhost:8000/agent/credentials \
  -H "Content-Type: application/json" \
  -d '{"agent_id": "my-agent", "name": "My Agent"}'
```

### 4. 安装 Skill ��� OpenClaw

```bash
cp -r skills/todolist-agent ~/.openclaw/skills/
```

配置 `~/.openclaw/openclaw.json`：
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

## API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/agent/credentials` | POST | 创建 API Key |
| `/agent/todos` | GET/POST | 查询/创建待办 |
| `/agent/todos/check` | GET | 获取到期任务 |
| `/agent/todos/stats` | GET | 统计信息 |
| `/agent/todos/{id}` | GET/PUT/DELETE | 详情/更新/删除 |
| `/agent/todos/{id}/done` | POST | 标记完成 |
| `/agent/todos/{id}/fail` | POST | 标记失败 |
| `/agent/todos/{id}/subtasks` | GET/POST | 子任务列表/创建 |
| `/agent/todos/{id}/subtasks/{sub_id}/done` | POST | 完成子任务 |
| `/agent/todos/{id}/subtasks/{sub_id}` | PUT/DELETE | 更新/删除子任务 |

## 许可证

MIT License
