---
name: todolist-agent
description: Your personal todo list for tracking tasks you need to execute. Create, check, and complete your own todos with subtasks support.
user-invocable: true
metadata: {"openclaw": {"requires": {"env": ["TODOLIST_API_URL", "TODOLIST_API_KEY"]}, "emoji": "✅"}}
---

# Agent TodoList

This is YOUR personal todo list. Use it to track tasks you need to execute yourself. Supports subtasks for complex tasks.

## Authentication

All API calls require the Authorization header:

```
Authorization: Bearer ${TODOLIST_API_KEY}
Content-Type: application/json
```

## Base URL

`${TODOLIST_API_URL}` (default: http://localhost:8000)

---

## Todo APIs

### 1. Create Todo

**POST** `${TODOLIST_API_URL}/agent/todos`

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

**GET** `${TODOLIST_API_URL}/agent/todos?status=pending&due_before=now&priority=high&limit=50`

Query parameters:
- `status`: `pending` | `done` | `failed` | `all` (default: pending)
- `due_before`: ISO datetime or `now`
- `priority`: `low` | `normal` | `high` | `urgent`
- `limit`: 1-200 (default: 50)

### 3. Check Due Tasks (for periodic checks)

**GET** `${TODOLIST_API_URL}/agent/todos/check`

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
