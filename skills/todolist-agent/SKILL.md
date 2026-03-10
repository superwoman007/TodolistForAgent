---
name: todolist-agent
description: Your personal todo list for tracking tasks you need to execute. Create, check, and complete your own todos with subtasks support.
user-invocable: true
metadata: {"openclaw": {"emoji": "✅"}}
---

# Agent TodoList

This is YOUR personal todo list. Use it to track tasks you need to execute yourself. Supports subtasks for complex tasks.

## Runtime configuration

Preferred runtime config source (agent-scoped):

- `~/.openclaw/agents/<agent>/todolist-agent.json`

Where `<agent>` is the agent name (default: `main`). For example:
- `~/.openclaw/agents/main/todolist-agent.json`
- `~/.openclaw/agents/assistant/todolist-agent.json`

Example:

```json
{
  "apiUrl": "https://todo.yourdomain.com",
  "apiKey": "ak_server_issued_for_this_agent",
  "agentId": "agent-issued-by-server"
}
```

**Why agent-scoped config?**

In multi-agent setups, each agent needs its own isolated configuration with different API keys and agent IDs. Using a global `~/.openclaw/todolist-agent.json` would cause conflicts when multiple agents run on the same host. Agent-scoped config ensures each agent's runtime settings are isolated and do not interfere with each other.

Compatibility fallback (not recommended for multi-agent setups):

- `TODOLIST_API_URL`
- `TODOLIST_API_KEY`

Prefer the JSON file for centrally managed agents because updating it should not require restarting OpenClaw.

## Authentication

All API calls require the Authorization header using the configured API key.

```http
Authorization: Bearer <apiKey>
Content-Type: application/json
```

## Base URL

Use the configured `apiUrl`. If env fallback is used, that corresponds to `${TODOLIST_API_URL}`.

## Identity and provisioning note

This skill assumes the host agent has already been provisioned with a valid connection to a TodoList backend.

In a centralized server setup:
- the backend URL and API key are supplied by the server/operator
- different agents should use different API keys
- use the `todolist-agent-init.sh` script to configure runtime settings (see below)
- prefer shipping/updating a local runtime config file instead of requiring `openclaw.json` edits
- current versions use a simple identity model: if an agent loses its local binding/config and is provisioned again, it is treated as a **new agent** and gets a **new task space**
- recovery of the previous space after local identity loss is **not supported yet**

### Setup / Initialization

For centrally managed agents, run the init script after installing the skill:

```bash
# Default agent (main) - creates cron patrol by default:
./scripts/todolist-agent-init.sh \
  --api-url https://todo.yourdomain.com \
  --api-key ak_server_issued_for_this_agent \
  --agent-id agent-issued-by-server

# For a different agent:
./scripts/todolist-agent-init.sh \
  --api-url https://todo.yourdomain.com \
  --api-key ak_another_agent_key \
  --agent-id another-agent-id \
  --agent assistant

# To skip cron patrol creation:
./scripts/todolist-agent-init.sh \
  --api-url https://todo.yourdomain.com \
  --api-key ak_server_issued_for_this_agent \
  --agent-id agent-issued-by-server \
  --agent main \
  --no-cron
```

This creates `~/.openclaw/agents/<agent>/todolist-agent.json`. Re-run the script to update credentials. Cron jobs are agent-specific (named `todolist-agent-patrol-<agent>`).

---

## Todo APIs

### 1. Create Todo

**POST** `{apiUrl}/agent/todos`

```json
{
  "title": "Task title (required)",
  "description": "Execution instructions (optional)",
  "due_at": "2026-03-07T09:00:00",
  "priority": "normal",
  "repeat_rule": "none"
}
```

Fields:
- `title` (required): Brief task description
- `description` (optional): How to execute this task
- `due_at` (optional): ISO 8601 datetime
- `priority` (optional): `low` | `normal` | `high` | `urgent`
- `repeat_rule` (optional): `none` | `daily` | `weekly` | `monthly`

### 2. List Todos

**GET** `{apiUrl}/agent/todos?status=pending&due_before=now&priority=high&limit=50`

Query parameters:
- `status`: `pending` | `done` | `failed` | `all` (default: pending)
- `due_before`: ISO datetime or `now`
- `priority`: `low` | `normal` | `high` | `urgent`
- `limit`: 1-200 (default: 50)

### 3. Check Due Tasks (for periodic checks)

**GET** `{apiUrl}/agent/todos/check`

Returns all pending tasks where `due_at <= now`, sorted by priority. Run this every 30 minutes.

### 4. Get Todo Details

**GET** `${TODOLIST_API_URL}/agent/todos/{id}`

### 5. Mark as Done

**POST** `${TODOLIST_API_URL}/agent/todos/{id}/done`

```json
{
  "result": "Execution result (optional)"
}
```

Effect: Sets status to "done". If repeat_rule is set, automatically creates next occurrence.

### 6. Mark as Failed

**POST** `${TODOLIST_API_URL}/agent/todos/{id}/fail`

```json
{
  "result": "Error message (optional)"
}
```

### 7. Update Todo

**PUT** `${TODOLIST_API_URL}/agent/todos/{id}`

```json
{
  "title": "New title",
  "description": "New description",
  "due_at": "2026-03-08T10:00:00",
  "priority": "high",
  "repeat_rule": "weekly",
  "status": "pending"
}
```

All fields optional.

### 8. Delete Todo

**DELETE** `${TODOLIST_API_URL}/agent/todos/{id}`

Response: 204 No Content

### 9. Statistics

**GET** `${TODOLIST_API_URL}/agent/todos/stats`

Response:
```json
{
  "pending": 5,
  "done": 12,
  "failed": 1,
  "overdue": 2,
  "total": 18
}
```

---

## Subtask APIs

### 10. List Subtasks

**GET** `${TODOLIST_API_URL}/agent/todos/{id}/subtasks`

Response:
```json
[
  {"id": 1, "agent_todo_id": 10, "title": "Collect data", "description": "Gather metrics", "done": false, "order": 0},
  {"id": 2, "agent_todo_id": 10, "title": "Create slides", "description": null, "done": false, "order": 1}
]
```

### 11. Create Subtask

**POST** `${TODOLIST_API_URL}/agent/todos/{id}/subtasks`

```json
{
  "title": "Subtask title (required)",
  "description": "Instructions (optional)",
  "order": 0
}
```

### 12. Update Subtask

**PUT** `${TODOLIST_API_URL}/agent/todos/{id}/subtasks/{subtask_id}`

```json
{
  "title": "New title",
  "description": "New instructions",
  "done": true,
  "order": 1
}
```

All fields optional.

### 13. Mark Subtask as Done

**POST** `${TODOLIST_API_URL}/agent/todos/{id}/subtasks/{subtask_id}/done`

### 14. Delete Subtask

**DELETE** `${TODOLIST_API_URL}/agent/todos/{id}/subtasks/{subtask_id}`

Response: 204 No Content

---

## Usage Workflows

### Simple task — user assigns a reminder:

```
User: "Remind me to check emails every day at 9am"

You:
1. POST /agent/todos
   Body: {"title": "Remind user to check emails", "description": "Send reminder message", "due_at": "2026-03-07T09:00:00", "repeat_rule": "daily"}
2. Reply: "✅ Added to my todo list: I'll remind you daily at 9am"
```

### Complex task — break into subtasks:

```
User: "Prepare the Friday presentation"

You:
1. POST /agent/todos
   Body: {"title": "Prepare Friday presentation", "due_at": "2026-03-13T14:00:00", "priority": "high"}
   → Returns id: 10

2. POST /agent/todos/10/subtasks
   Body: {"title": "Collect data", "description": "Gather this week's metrics", "order": 0}

3. POST /agent/todos/10/subtasks
   Body: {"title": "Create slides", "description": "Make PPT with key findings", "order": 1}

4. POST /agent/todos/10/subtasks
   Body: {"title": "Rehearse", "description": "Dry run the presentation", "order": 2}

5. Reply: "✅ Created task with 3 subtasks. I'll work on them before Friday."
```

### Periodic check (every 30 minutes):

```
1. GET /agent/todos/check
   → Returns due tasks

2. For each task:
   - If task has subtasks: GET /agent/todos/{id}/subtasks → execute undone ones → POST .../subtasks/{sub_id}/done
   - If all subtasks done (or no subtasks): execute main task → POST /agent/todos/{id}/done
   - If error: POST /agent/todos/{id}/fail
```

### Scheduled patrol behavior

When this skill is available in an agent that runs on a timer / cron / heartbeat:

1. Periodically call `GET /agent/todos/check`
2. If no due tasks exist, stop quickly and prefer silence or a one-line minimal summary
3. If due tasks exist, process them in returned order
4. For tasks with subtasks, fetch subtasks first and complete actionable unfinished subtasks before finishing the parent task
5. Mark successful work with `POST /done` and include a useful `result`
6. Mark failures with `POST /fail` and include the error/result summary

### Patrol reporting rule

Use concise reporting by default.

- **If no due tasks exist**: prefer no user-facing interruption; do not proactively send a message just to say nothing happened unless the host environment strictly requires a response
- **If work was performed**: return a concise but useful summary including:
  - how many tasks were due
  - which tasks were completed or failed
  - whether recurring tasks generated next items
  - any follow-up risk or human attention needed
- **If an execution failure happens**: clearly surface the failure reason in both the task `result` and the patrol summary

### Quiet-by-default rule

Do not create extra noise.

- If there is no new task activity, no completed work, no failure, and no human decision needed, stay silent
- Only interrupt the user when there is meaningful value:
  - a task was actually processed
  - a patrol failed or found a problem
  - human input or approval is needed
  - an important follow-up result should be surfaced
- Avoid sending heartbeat-style "nothing happened" messages in normal operation

### Patrol failure handling

When this skill is used with a scheduler, the host agent should prefer these defaults:

- alert only on repeated patrol failures rather than every isolated hiccup
- keep patrol execution independent from delivery problems when possible
- treat API unavailability, auth failure, or repeated execution errors as noteworthy issues worth escalating

Default recommendation: run this patrol every 30 minutes unless the host agent has a stricter schedule requirement.

### User asks "what are your todos":

```
1. GET /agent/todos?status=pending
2. For each todo with subtasks: GET /agent/todos/{id}/subtasks
3. Present:
   📋 My todo list:
   1. 🔴 Prepare Friday presentation [3 subtasks: 1/3 done]
   2. 🟡 Remind user to check emails [daily] - tomorrow 09:00
   3. 🟢 Clean up old tasks [low priority]
```

---

## Best Practices

1. **Check periodically**: Run `/agent/todos/check` every 30 minutes
2. **Record results**: Always include `result` when marking done/failed
3. **Use subtasks**: Break complex tasks into smaller subtasks
4. **Set priorities**: Execute high priority tasks first
5. **Handle failures**: Mark as failed with error message, don't skip silently
6. **Persist actionable plans**: If you create a plan for yourself and it is not something you will finish immediately in the current turn, write it into TodoList instead of leaving it only in the conversation

## Plan Persistence Rule

When you, the agent, generate your own plan, decide whether it is only short-lived reasoning or whether it should become tracked work.

**Do NOT create a todo for:**
- fleeting internal reasoning
- steps you will finish immediately in the current turn
- scratch sequencing that has no future follow-up value

**Create a todo automatically when any of these are true:**
- the work cannot be completed in the current turn
- the work depends on a future time or deadline
- you need to follow up later
- the work should survive session restarts
- the plan contains multiple execution steps worth tracking

**Use subtasks for multi-step plans.**

Examples:
- If you think: "Later I should rerun the deployment check and report back" → create a todo
- If you think: "This task has 3 follow-up actions" → create one parent todo and add subtasks
- If you think: "First I'll read the file, then reply" and you will do it right now → do not create a todo

Default behavior:
- Prefer storing durable action items rather than leaving them only in chat text
- If a plan becomes a todo, write the execution intent into `description`
- If the plan is complex, create the parent todo first, then create subtasks

---

## Error Handling

- **401 Unauthorized**: Invalid or missing API key
- **404 Not Found**: Todo/subtask doesn't exist or doesn't belong to you
- **422 Validation Error**: Invalid request body
