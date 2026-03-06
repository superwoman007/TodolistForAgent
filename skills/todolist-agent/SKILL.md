---
name: todolist-agent
description: Your personal todo list for tracking tasks you need to execute. Create, check, and complete your own todos.
user-invocable: true
metadata: {"openclaw": {"requires": {"env": ["TODOLIST_API_URL", "TODOLIST_API_KEY"]}, "emoji": "✅"}}
---

# Agent TodoList

This is YOUR personal todo list. Use it to track tasks you need to execute yourself.

## Authentication

All API calls require authentication via API Key in the Authorization header:

```
Authorization: Bearer ${TODOLIST_API_KEY}
```

Your API key is stored in the environment variable `TODOLIST_API_KEY`.

## Base URL

All API calls use: `${TODOLIST_API_URL}` (default: http://localhost:8000)

## Getting Your API Key

**First-time setup:** An administrator needs to create your API key using:

```
POST ${TODOLIST_API_URL}/agent/credentials
Content-Type: application/json

{
  "agent_id": "your-unique-agent-id",
  "name": "My Assistant Agent"
}
```

Response will include your `api_key`. Store it in `TODOLIST_API_KEY` environment variable.

---

## Available APIs

### 1. Create Todo

**POST** `${TODOLIST_API_URL}/agent/todos`

Create a new todo for yourself.

**Headers:**
```
Authorization: Bearer ${TODOLIST_API_KEY}
Content-Type: application/json
```

**Request Body:**
```json
{
  "title": "Task title (required)",
  "description": "Detailed execution instructions (optional)",
  "due_at": "2026-03-07T09:00:00",
  "priority": "normal",
  "repeat_rule": "none"
}
```

**Fields:**
- `title` (required): Brief task description
- `description` (optional): How to execute this task
- `due_at` (optional): ISO 8601 datetime when task should be executed
- `priority` (optional): `low` | `normal` | `high` | `urgent` (default: normal)
- `repeat_rule` (optional): `none` | `daily` | `weekly` | `monthly` (default: none)

**Response:**
```json
{
  "id": 123,
  "agent_id": "your-agent-id",
  "title": "Send weather report",
  "status": "pending",
  "due_at": "2026-03-07T09:00:00",
  "priority": "normal",
  "repeat_rule": "daily",
  "created_at": "2026-03-06T13:00:00"
}
```

---

### 2. List Todos

**GET** `${TODOLIST_API_URL}/agent/todos?status=pending&due_before=now&priority=high&limit=50`

Query your todo list with filters.

**Headers:**
```
Authorization: Bearer ${TODOLIST_API_KEY}
```

**Query Parameters:**
- `status` (optional): `pending` | `done` | `failed` | `all` (default: pending)
- `due_before` (optional): ISO datetime or `now` to filter overdue tasks
- `priority` (optional): `low` | `normal` | `high` | `urgent`
- `limit` (optional): Max results, 1-200 (default: 50)

**Response:**
```json
[
  {
    "id": 123,
    "agent_id": "your-agent-id",
    "title": "Send weather report",
    "description": "Search current weather and send to user",
    "status": "pending",
    "priority": "normal",
    "due_at": "2026-03-07T09:00:00",
    "repeat_rule": "daily",
    "created_at": "2026-03-06T13:00:00"
  }
]
```

---

### 3. Check Due Tasks

**GET** `${TODOLIST_API_URL}/agent/todos/check`

Get all pending tasks that are due now (due_at <= current time). Use this for periodic checks.

**Headers:**
```
Authorization: Bearer ${TODOLIST_API_KEY}
```

**Response:** Same format as list todos, sorted by priority and due time.

**When to use:** Run this every 30 minutes to find tasks you need to execute.

---

### 4. Get Todo Details

**GET** `${TODOLIST_API_URL}/agent/todos/{id}`

Get full details of a specific todo.

**Headers:**
```
Authorization: Bearer ${TODOLIST_API_KEY}
```

**Response:** Single todo object (same format as list).

---

### 5. Mark as Done

**POST** `${TODOLIST_API_URL}/agent/todos/{id}/done`

Mark a todo as completed after execution.

**Headers:**
```
Authorization: Bearer ${TODOLIST_API_KEY}
Content-Type: application/json
```

**Request Body:**
```json
{
  "result": "Execution result or notes (optional)"
}
```

**Effect:**
- Sets status to "done"
- Records completion time
- If repeat_rule is set, automatically creates next occurrence

---

### 6. Mark as Failed

**POST** `${TODOLIST_API_URL}/agent/todos/{id}/fail`

Mark a todo as failed if execution encountered errors.

**Headers:**
```
Authorization: Bearer ${TODOLIST_API_KEY}
Content-Type: application/json
```

**Request Body:**
```json
{
  "result": "Error message or reason (optional)"
}
```

---

### 7. Update Todo

**PUT** `${TODOLIST_API_URL}/agent/todos/{id}`

Update todo details. All fields are optional.

**Headers:**
```
Authorization: Bearer ${TODOLIST_API_KEY}
Content-Type: application/json
```

**Request Body:**
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

---

### 8. Delete Todo

**DELETE** `${TODOLIST_API_URL}/agent/todos/{id}`

Permanently delete a todo.

**Headers:**
```
Authorization: Bearer ${TODOLIST_API_KEY}
```

**Response:** 204 No Content

---

### 9. Statistics

**GET** `${TODOLIST_API_URL}/agent/todos/stats`

Get summary statistics of your todos.

**Headers:**
```
Authorization: Bearer ${TODOLIST_API_KEY}
```

**Response:**
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

## Usage Workflow

### When user assigns you a task:

**User:** "Remind me to check emails every day at 9am"

**You should:**
1. Create todo with Authorization header
2. Respond: "✅ Added to my todo list: I'll remind you to check emails daily at 9am"

### Periodic check (every 30 minutes):

1. Check for due tasks (with Authorization header)
2. For each task: execute → mark as done/failed

### When user asks "what are your todos":

1. List pending todos (with Authorization header)
2. Format and present with emojis

---

## Error Handling

- **401 Unauthorized**: Invalid or missing API key
- **404 Not Found**: Todo doesn't exist or doesn't belong to you
- **422 Validation Error**: Invalid request body

Always include the Authorization header in every request.


## Available APIs

### 1. Create Todo

**POST** `${TODOLIST_API_URL}/agent/todos`

Create a new todo for yourself.

**Request Body:**
```json
{
  "title": "Task title (required)",
  "description": "Detailed execution instructions (optional)",
  "due_at": "2026-03-07T09:00:00",
  "priority": "normal",
  "repeat_rule": "none"
}
```

**Fields:**
- `title` (required): Brief task description
- `description` (optional): How to execute this task
- `due_at` (optional): ISO 8601 datetime when task should be executed
- `priority` (optional): `low` | `normal` | `high` | `urgent` (default: normal)
- `repeat_rule` (optional): `none` | `daily` | `weekly` | `monthly` (default: none)

**Response:**
```json
{
  "id": 123,
  "title": "Send weather report",
  "status": "pending",
  "due_at": "2026-03-07T09:00:00",
  "priority": "normal",
  "repeat_rule": "daily",
  "created_at": "2026-03-06T13:00:00"
}
```

**Example:**
```
POST ${TODOLIST_API_URL}/agent/todos
Content-Type: application/json

{
  "title": "Send morning weather report",
  "description": "Search current weather and send to user",
  "due_at": "2026-03-07T09:00:00",
  "repeat_rule": "daily",
  "priority": "normal"
}
```

---

### 2. List Todos

**GET** `${TODOLIST_API_URL}/agent/todos?status=pending&due_before=now&priority=high&limit=50`

Query your todo list with filters.

**Query Parameters:**
- `status` (optional): `pending` | `done` | `failed` | `all` (default: pending)
- `due_before` (optional): ISO datetime or `now` to filter overdue tasks
- `priority` (optional): `low` | `normal` | `high` | `urgent`
- `limit` (optional): Max results, 1-200 (default: 50)

**Response:**
```json
[
  {
    "id": 123,
    "title": "Send weather report",
    "description": "Search current weather and send to user",
    "status": "pending",
    "priority": "normal",
    "due_at": "2026-03-07T09:00:00",
    "repeat_rule": "daily",
    "created_at": "2026-03-06T13:00:00"
  }
]
```

**Examples:**
- List all pending: `GET ${TODOLIST_API_URL}/agent/todos`
- List completed: `GET ${TODOLIST_API_URL}/agent/todos?status=done`
- List overdue: `GET ${TODOLIST_API_URL}/agent/todos?status=pending&due_before=now`
- List high priority: `GET ${TODOLIST_API_URL}/agent/todos?priority=high`

---

### 3. Check Due Tasks

**GET** `${TODOLIST_API_URL}/agent/todos/check`

Get all pending tasks that are due now (due_at <= current time). Use this for periodic checks.

**Response:** Same format as list todos, sorted by priority and due time.

**When to use:** Run this every 30 minutes to find tasks you need to execute.

---

### 4. Get Todo Details

**GET** `${TODOLIST_API_URL}/agent/todos/{id}`

Get full details of a specific todo.

**Response:** Single todo object (same format as list).

---

### 5. Mark as Done

**POST** `${TODOLIST_API_URL}/agent/todos/{id}/done`

Mark a todo as completed after execution.

**Request Body:**
```json
{
  "result": "Execution result or notes (optional)"
}
```

**Effect:**
- Sets status to "done"
- Records completion time
- If repeat_rule is set, automatically creates next occurrence

**Example:**
```
POST ${TODOLIST_API_URL}/agent/todos/123/done
Content-Type: application/json

{
  "result": "Weather report sent successfully at 09:01"
}
```

---

### 6. Mark as Failed

**POST** `${TODOLIST_API_URL}/agent/todos/{id}/fail`

Mark a todo as failed if execution encountered errors.

**Request Body:**
```json
{
  "result": "Error message or reason (optional)"
}
```

**Example:**
```
POST ${TODOLIST_API_URL}/agent/todos/123/fail
Content-Type: application/json

{
  "result": "Weather API unavailable"
}
```

---

### 7. Update Todo

**PUT** `${TODOLIST_API_URL}/agent/todos/{id}`

Update todo details. All fields are optional.

**Request Body:**
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

---

### 8. Delete Todo

**DELETE** `${TODOLIST_API_URL}/agent/todos/{id}`

Permanently delete a todo.

**Response:** 204 No Content

---

### 9. Statistics

**GET** `${TODOLIST_API_URL}/agent/todos/stats`

Get summary statistics of your todos.

**Response:**
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

## Usage Workflow

### When user assigns you a task:

**User:** "Remind me to check emails every day at 9am"

**You should:**
1. Create todo:
   ```
   POST ${TODOLIST_API_URL}/agent/todos
   Body: {
     "title": "Remind user to check emails",
     "description": "Send reminder message to user",
     "due_at": "2026-03-07T09:00:00",
     "repeat_rule": "daily"
   }
   ```
2. Respond: "✅ Added to my todo list: I'll remind you to check emails daily at 9am"

### Periodic check (every 30 minutes):

1. Check for due tasks:
   ```
   GET ${TODOLIST_API_URL}/agent/todos/check
   ```
2. For each task returned:
   - Read the `description` field for execution instructions
   - Execute the task
   - Mark as done:
     ```
     POST ${TODOLIST_API_URL}/agent/todos/{id}/done
     Body: {"result": "Task completed"}
     ```
   - If execution fails:
     ```
     POST ${TODOLIST_API_URL}/agent/todos/{id}/fail
     Body: {"result": "Error message"}
     ```

### When user asks "what are your todos":

1. List pending todos:
   ```
   GET ${TODOLIST_API_URL}/agent/todos?status=pending
   ```
2. Format and present the list to user with emojis:
   - 🔴 High priority
   - 🟡 Normal priority
   - 🟢 Low priority
   - ⏰ Include due time
   - 🔁 Indicate if repeating

### When user asks "what have you completed":

```
GET ${TODOLIST_API_URL}/agent/todos?status=done&limit=20
```

---

## Best Practices

1. **Always check periodically**: Run `/agent/todos/check` every 30 minutes when active
2. **Record results**: Always include `result` when marking done/failed for debugging
3. **Use descriptions**: Store execution instructions in `description` field
4. **Set priorities**: Use priority to determine execution order when multiple tasks are due
5. **Handle failures gracefully**: Mark as failed with error message, don't silently skip
6. **Clean up**: Delete completed one-time tasks after a few days to keep list clean

---

## Example Scenarios

### Scenario 1: Daily reminder
```
User: "Remind me to take medicine every day at 8am and 8pm"

You create two todos:
POST ${TODOLIST_API_URL}/agent/todos
{"title": "Medicine reminder (morning)", "due_at": "2026-03-07T08:00:00", "repeat_rule": "daily"}

POST ${TODOLIST_API_URL}/agent/todos
{"title": "Medicine reminder (evening)", "due_at": "2026-03-07T20:00:00", "repeat_rule": "daily"}
```

### Scenario 2: One-time task
```
User: "Remind me about the meeting tomorrow at 2pm"

POST ${TODOLIST_API_URL}/agent/todos
{
  "title": "Meeting reminder",
  "description": "Remind user about the meeting",
  "due_at": "2026-03-07T14:00:00",
  "priority": "high",
  "repeat_rule": "none"
}
```

### Scenario 3: Check and execute
```
Every 30 minutes:

1. GET ${TODOLIST_API_URL}/agent/todos/check
   Response: [{"id": 5, "title": "Medicine reminder (morning)", "description": "Remind user to take medicine", ...}]

2. Execute: Send message "⏰ Time to take your medicine!"

3. POST ${TODOLIST_API_URL}/agent/todos/5/done
   Body: {"result": "Reminder sent at 08:01"}
```

---

## Error Handling

- **404 Not Found**: Todo doesn't exist, check ID
- **422 Validation Error**: Invalid request body, check required fields
- **500 Server Error**: Backend issue, retry or report to user

Always handle errors gracefully and inform the user if a task cannot be completed.
