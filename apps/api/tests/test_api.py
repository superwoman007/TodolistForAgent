import pytest
from fastapi.testclient import TestClient
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

os.environ["ADMIN_TOKEN"] = "test_admin_secret"

from app.main import app
from app.db.session import Base, engine, SessionLocal
from app.models.agent_credential import AgentCredential


@pytest.fixture(scope="function")
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_credential(client):
    response = client.post(
        "/agent/credentials",
        json={"agent_id": "test-agent", "name": "Test Agent"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["agent_id"] == "test-agent"
    assert data["name"] == "Test Agent"
    assert data["api_key"].startswith("ak_")


def test_credential_duplicate_agent_id(client):
    client.post(
        "/agent/credentials",
        json={"agent_id": "test-agent", "name": "Test Agent"}
    )
    response = client.post(
        "/agent/credentials",
        json={"agent_id": "test-agent", "name": "Duplicate"}
    )
    assert response.status_code == 400


def test_auth_failure_no_header(client):
    response = client.get("/agent/todos")
    assert response.status_code == 401


def test_auth_failure_invalid_key(client):
    response = client.get(
        "/agent/todos",
        headers={"Authorization": "Bearer invalid_key"}
    )
    assert response.status_code == 401


def test_create_todo(client, db):
    cred = AgentCredential(agent_id="test-agent", api_key="ak_testkey123")
    db.add(cred)
    db.commit()
    
    response = client.post(
        "/agent/todos",
        headers={"Authorization": "Bearer ak_testkey123"},
        json={
            "title": "Test todo",
            "description": "Test description",
            "priority": "high"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test todo"
    assert data["priority"] == "high"
    assert data["status"] == "pending"


def test_create_todo_invalid_priority(client, db):
    cred = AgentCredential(agent_id="test-agent", api_key="ak_testkey123")
    db.add(cred)
    db.commit()
    
    response = client.post(
        "/agent/todos",
        headers={"Authorization": "Bearer ak_testkey123"},
        json={"title": "Test", "priority": "invalid"}
    )
    assert response.status_code == 422


def test_create_todo_invalid_repeat_rule(client, db):
    cred = AgentCredential(agent_id="test-agent", api_key="ak_testkey123")
    db.add(cred)
    db.commit()
    
    response = client.post(
        "/agent/todos",
        headers={"Authorization": "Bearer ak_testkey123"},
        json={"title": "Test", "repeat_rule": "yearly"}
    )
    assert response.status_code == 422


def test_list_todos(client, db):
    cred = AgentCredential(agent_id="test-agent", api_key="ak_testkey123")
    db.add(cred)
    db.commit()
    
    client.post(
        "/agent/todos",
        headers={"Authorization": "Bearer ak_testkey123"},
        json={"title": "Todo 1", "priority": "high"}
    )
    client.post(
        "/agent/todos",
        headers={"Authorization": "Bearer ak_testkey123"},
        json={"title": "Todo 2", "priority": "low"}
    )
    
    response = client.get(
        "/agent/todos",
        headers={"Authorization": "Bearer ak_testkey123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_check_due_todos_empty(client, db):
    cred = AgentCredential(agent_id="test-agent", api_key="ak_testkey123")
    db.add(cred)
    db.commit()
    
    response = client.get(
        "/agent/todos/check",
        headers={"Authorization": "Bearer ak_testkey123"}
    )
    assert response.status_code == 200
    assert response.json() == []


def test_mark_done_simple(client, db):
    cred = AgentCredential(agent_id="test-agent", api_key="ak_testkey123")
    db.add(cred)
    db.commit()
    
    create_resp = client.post(
        "/agent/todos",
        headers={"Authorization": "Bearer ak_testkey123"},
        json={"title": "Test todo"}
    )
    todo_id = create_resp.json()["id"]
    
    response = client.post(
        f"/agent/todos/{todo_id}/done",
        headers={"Authorization": "Bearer ak_testkey123"},
        json={"result": "Completed successfully"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "done"
    assert data["result"] == "Completed successfully"


def test_recurring_task_creation(client, db):
    cred = AgentCredential(agent_id="test-agent", api_key="ak_testkey123")
    db.add(cred)
    db.commit()
    
    from datetime import datetime, timezone, timedelta
    
    create_resp = client.post(
        "/agent/todos",
        headers={"Authorization": "Bearer ak_testkey123"},
        json={
            "title": "Daily reminder",
            "repeat_rule": "daily",
            "due_at": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
        }
    )
    todo_id = create_resp.json()["id"]
    
    response = client.post(
        f"/agent/todos/{todo_id}/done",
        headers={"Authorization": "Bearer ak_testkey123"},
        json={}
    )
    assert response.status_code == 200
    
    todos_resp = client.get(
        "/agent/todos?status=all",
        headers={"Authorization": "Bearer ak_testkey123"}
    )
    todos = todos_resp.json()
    assert len(todos) == 2
    assert todos[0]["status"] == "done"
    assert todos[1]["status"] == "pending"
    assert todos[1]["repeat_rule"] == "daily"


def test_subtask_flow(client, db):
    cred = AgentCredential(agent_id="test-agent", api_key="ak_testkey123")
    db.add(cred)
    db.commit()
    
    create_resp = client.post(
        "/agent/todos",
        headers={"Authorization": "Bearer ak_testkey123"},
        json={"title": "Complex task"}
    )
    todo_id = create_resp.json()["id"]
    
    subtask1 = client.post(
        f"/agent/todos/{todo_id}/subtasks",
        headers={"Authorization": "Bearer ak_testkey123"},
        json={"title": "Step 1", "order": 1}
    )
    assert subtask1.status_code == 201
    
    subtask2 = client.post(
        f"/agent/todos/{todo_id}/subtasks",
        headers={"Authorization": "Bearer ak_testkey123"},
        json={"title": "Step 2", "order": 2}
    )
    assert subtask2.status_code == 201
    
    list_resp = client.get(
        f"/agent/todos/{todo_id}/subtasks",
        headers={"Authorization": "Bearer ak_testkey123"}
    )
    subtasks = list_resp.json()
    assert len(subtasks) == 2
    assert subtasks[0]["title"] == "Step 1"
    assert subtasks[1]["title"] == "Step 2"
    
    mark_done_resp = client.post(
        f"/agent/todos/{todo_id}/subtasks/{subtasks[0]['id']}/done",
        headers={"Authorization": "Bearer ak_testkey123"}
    )
    assert mark_done_resp.status_code == 200
    assert mark_done_resp.json()["done"] is True
    
    delete_resp = client.delete(
        f"/agent/todos/{todo_id}/subtasks/{subtasks[1]['id']}",
        headers={"Authorization": "Bearer ak_testkey123"}
    )
    assert delete_resp.status_code == 204


def test_todo_not_found_different_agent(client, db):
    cred1 = AgentCredential(agent_id="agent-1", api_key="ak_key1")
    cred2 = AgentCredential(agent_id="agent-2", api_key="ak_key2")
    db.add(cred1)
    db.add(cred2)
    db.commit()
    
    create_resp = client.post(
        "/agent/todos",
        headers={"Authorization": "Bearer ak_key1"},
        json={"title": "Agent 1 todo"}
    )
    todo_id = create_resp.json()["id"]
    
    response = client.get(
        f"/agent/todos/{todo_id}",
        headers={"Authorization": "Bearer ak_key2"}
    )
    assert response.status_code == 404


def test_update_todo(client, db):
    cred = AgentCredential(agent_id="test-agent", api_key="ak_testkey123")
    db.add(cred)
    db.commit()
    
    create_resp = client.post(
        "/agent/todos",
        headers={"Authorization": "Bearer ak_testkey123"},
        json={"title": "Original title", "priority": "low"}
    )
    todo_id = create_resp.json()["id"]
    
    response = client.put(
        f"/agent/todos/{todo_id}",
        headers={"Authorization": "Bearer ak_testkey123"},
        json={"title": "Updated title", "priority": "high"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated title"
    assert data["priority"] == "high"


def test_update_todo_not_found(client, db):
    cred = AgentCredential(agent_id="test-agent", api_key="ak_testkey123")
    db.add(cred)
    db.commit()
    
    response = client.put(
        "/agent/todos/99999",
        headers={"Authorization": "Bearer ak_testkey123"},
        json={"title": "Updated title"}
    )
    assert response.status_code == 404


def test_mark_failed(client, db):
    cred = AgentCredential(agent_id="test-agent", api_key="ak_testkey123")
    db.add(cred)
    db.commit()
    
    create_resp = client.post(
        "/agent/todos",
        headers={"Authorization": "Bearer ak_testkey123"},
        json={"title": "Task that will fail"}
    )
    todo_id = create_resp.json()["id"]
    
    response = client.post(
        f"/agent/todos/{todo_id}/fail",
        headers={"Authorization": "Bearer ak_testkey123"},
        json={"result": "Task failed due to error"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "failed"
    assert data["result"] == "Task failed due to error"


def test_mark_failed_not_found(client, db):
    cred = AgentCredential(agent_id="test-agent", api_key="ak_testkey123")
    db.add(cred)
    db.commit()
    
    response = client.post(
        "/agent/todos/99999/fail",
        headers={"Authorization": "Bearer ak_testkey123"},
        json={"result": "Failed"}
    )
    assert response.status_code == 404


def test_delete_todo(client, db):
    cred = AgentCredential(agent_id="test-agent", api_key="ak_testkey123")
    db.add(cred)
    db.commit()
    
    create_resp = client.post(
        "/agent/todos",
        headers={"Authorization": "Bearer ak_testkey123"},
        json={"title": "Task to delete"}
    )
    todo_id = create_resp.json()["id"]
    
    response = client.delete(
        f"/agent/todos/{todo_id}",
        headers={"Authorization": "Bearer ak_testkey123"}
    )
    assert response.status_code == 204
    
    get_resp = client.get(
        f"/agent/todos/{todo_id}",
        headers={"Authorization": "Bearer ak_testkey123"}
    )
    assert get_resp.status_code == 404


def test_delete_todo_not_found(client, db):
    cred = AgentCredential(agent_id="test-agent", api_key="ak_testkey123")
    db.add(cred)
    db.commit()
    
    response = client.delete(
        "/agent/todos/99999",
        headers={"Authorization": "Bearer ak_testkey123"}
    )
    assert response.status_code == 404


def test_check_due_todos_priority_order(client, db):
    from datetime import datetime, timezone, timedelta
    cred = AgentCredential(agent_id="test-agent", api_key="ak_testkey123")
    db.add(cred)
    db.commit()
    
    now = datetime.now(timezone.utc)
    past = now - timedelta(hours=1)
    
    client.post(
        "/agent/todos",
        headers={"Authorization": "Bearer ak_testkey123"},
        json={"title": "Low priority", "priority": "low", "due_at": past.isoformat()}
    )
    client.post(
        "/agent/todos",
        headers={"Authorization": "Bearer ak_testkey123"},
        json={"title": "Urgent priority", "priority": "urgent", "due_at": past.isoformat()}
    )
    client.post(
        "/agent/todos",
        headers={"Authorization": "Bearer ak_testkey123"},
        json={"title": "Normal priority", "priority": "normal", "due_at": past.isoformat()}
    )
    client.post(
        "/agent/todos",
        headers={"Authorization": "Bearer ak_testkey123"},
        json={"title": "High priority", "priority": "high", "due_at": past.isoformat()}
    )
    
    response = client.get(
        "/agent/todos/check",
        headers={"Authorization": "Bearer ak_testkey123"}
    )
    assert response.status_code == 200
    todos = response.json()
    assert len(todos) == 4
    assert todos[0]["priority"] == "urgent"
    assert todos[1]["priority"] == "high"
    assert todos[2]["priority"] == "normal"
    assert todos[3]["priority"] == "low"


def test_monthly_recurring_calendar_month(client, db):
    from datetime import datetime, timezone
    cred = AgentCredential(agent_id="test-agent", api_key="ak_testkey123")
    db.add(cred)
    db.commit()
    
    due_at = datetime(2024, 1, 31, 10, 0, tzinfo=timezone.utc)
    response = client.post(
        "/agent/todos",
        headers={"Authorization": "Bearer ak_testkey123"},
        json={
            "title": "Monthly task",
            "repeat_rule": "monthly",
            "due_at": due_at.isoformat()
        }
    )
    todo_id = response.json()["id"]
    
    mark_done_resp = client.post(
        f"/agent/todos/{todo_id}/done",
        headers={"Authorization": "Bearer ak_testkey123"},
        json={}
    )
    assert mark_done_resp.status_code == 200
    
    todos_resp = client.get(
        "/agent/todos?status=all",
        headers={"Authorization": "Bearer ak_testkey123"}
    )
    todos = todos_resp.json()
    assert len(todos) == 2
    
    pending_todo = next(t for t in todos if t["status"] == "pending")
    assert pending_todo["due_at"] is not None
    next_due = datetime.fromisoformat(pending_todo["due_at"].replace("Z", "+00:00"))
    assert next_due.year == 2024
    assert next_due.month == 2
    assert next_due.day == 29


def test_monthly_recurring_non_end_of_month(client, db):
    from datetime import datetime, timezone
    cred = AgentCredential(agent_id="test-agent", api_key="ak_testkey123")
    db.add(cred)
    db.commit()
    
    due_at = datetime(2024, 1, 15, 10, 0, tzinfo=timezone.utc)
    response = client.post(
        "/agent/todos",
        headers={"Authorization": "Bearer ak_testkey123"},
        json={
            "title": "Monthly task",
            "repeat_rule": "monthly",
            "due_at": due_at.isoformat()
        }
    )
    todo_id = response.json()["id"]
    
    mark_done_resp = client.post(
        f"/agent/todos/{todo_id}/done",
        headers={"Authorization": "Bearer ak_testkey123"},
        json={}
    )
    assert mark_done_resp.status_code == 200
    
    todos_resp = client.get(
        "/agent/todos?status=all",
        headers={"Authorization": "Bearer ak_testkey123"}
    )
    todos = todos_resp.json()
    
    pending_todo = next(t for t in todos if t["status"] == "pending")
    next_due = datetime.fromisoformat(pending_todo["due_at"].replace("Z", "+00:00"))
    assert next_due.year == 2024
    assert next_due.month == 2
    assert next_due.day == 15


def test_list_credentials_requires_admin(client, db):
    response = client.get("/agent/credentials")
    assert response.status_code == 401


def test_list_credentials_valid_admin(client, db):
    response = client.get(
        "/agent/credentials",
        headers={"Authorization": "Bearer test_admin_secret"}
    )
    assert response.status_code == 200
    assert response.json() == []


def test_list_credentials_invalid_admin(client, db):
    response = client.get(
        "/agent/credentials",
        headers={"Authorization": "Bearer wrong_token"}
    )
    assert response.status_code == 403


def test_list_credentials_no_header(client, db):
    response = client.get("/agent/credentials")
    assert response.status_code == 401


def test_delete_credential_requires_admin(client, db):
    cred = AgentCredential(agent_id="test-agent", api_key="ak_testkey123")
    db.add(cred)
    db.commit()
    
    response = client.delete("/agent/credentials/test-agent")
    assert response.status_code == 401


def test_delete_credential_valid_admin(client, db):
    cred = AgentCredential(agent_id="test-agent", api_key="ak_testkey123")
    db.add(cred)
    db.commit()
    
    response = client.delete(
        "/agent/credentials/test-agent",
        headers={"Authorization": "Bearer test_admin_secret"}
    )
    assert response.status_code == 204


def test_delete_credential_invalid_admin(client, db):
    cred = AgentCredential(agent_id="test-agent", api_key="ak_testkey123")
    db.add(cred)
    db.commit()
    
    response = client.delete(
        "/agent/credentials/test-agent",
        headers={"Authorization": "Bearer wrong_token"}
    )
    assert response.status_code == 403


def test_delete_credential_not_found_admin(client):
    response = client.delete(
        "/agent/credentials/nonexistent",
        headers={"Authorization": "Bearer test_admin_secret"}
    )
    assert response.status_code == 404


def test_subtask_not_found(client, db):
    cred = AgentCredential(agent_id="test-agent", api_key="ak_testkey123")
    db.add(cred)
    db.commit()
    
    create_resp = client.post(
        "/agent/todos",
        headers={"Authorization": "Bearer ak_testkey123"},
        json={"title": "Complex task"}
    )
    todo_id = create_resp.json()["id"]
    
    response = client.put(
        f"/agent/todos/{todo_id}/subtasks/99999",
        headers={"Authorization": "Bearer ak_testkey123"},
        json={"title": "Does not exist"}
    )
    assert response.status_code == 404


def test_subtask_update_wrong_todo(client, db):
    cred1 = AgentCredential(agent_id="agent-1", api_key="ak_key1")
    cred2 = AgentCredential(agent_id="agent-2", api_key="ak_key2")
    db.add(cred1)
    db.add(cred2)
    db.commit()
    
    todo1_resp = client.post(
        "/agent/todos",
        headers={"Authorization": "Bearer ak_key1"},
        json={"title": "Agent 1 task"}
    )
    todo1_id = todo1_resp.json()["id"]
    
    subtask_resp = client.post(
        f"/agent/todos/{todo1_id}/subtasks",
        headers={"Authorization": "Bearer ak_key1"},
        json={"title": "Subtask", "order": 1}
    )
    subtask_id = subtask_resp.json()["id"]
    
    todo2_resp = client.post(
        "/agent/todos",
        headers={"Authorization": "Bearer ak_key2"},
        json={"title": "Agent 2 task"}
    )
    todo2_id = todo2_resp.json()["id"]
    
    response = client.put(
        f"/agent/todos/{todo2_id}/subtasks/{subtask_id}",
        headers={"Authorization": "Bearer ak_key2"},
        json={"title": "Hacked subtask"}
    )
    assert response.status_code == 404


def test_subtask_delete_wrong_todo(client, db):
    cred1 = AgentCredential(agent_id="agent-1", api_key="ak_key1")
    cred2 = AgentCredential(agent_id="agent-2", api_key="ak_key2")
    db.add(cred1)
    db.add(cred2)
    db.commit()
    
    todo1_resp = client.post(
        "/agent/todos",
        headers={"Authorization": "Bearer ak_key1"},
        json={"title": "Agent 1 task"}
    )
    todo1_id = todo1_resp.json()["id"]
    
    subtask_resp = client.post(
        f"/agent/todos/{todo1_id}/subtasks",
        headers={"Authorization": "Bearer ak_key1"},
        json={"title": "Subtask", "order": 1}
    )
    subtask_id = subtask_resp.json()["id"]
    
    todo2_resp = client.post(
        "/agent/todos",
        headers={"Authorization": "Bearer ak_key2"},
        json={"title": "Agent 2 task"}
    )
    todo2_id = todo2_resp.json()["id"]
    
    response = client.delete(
        f"/agent/todos/{todo2_id}/subtasks/{subtask_id}",
        headers={"Authorization": "Bearer ak_key2"}
    )
    assert response.status_code == 404


def test_subtask_mark_done_wrong_todo(client, db):
    cred1 = AgentCredential(agent_id="agent-1", api_key="ak_key1")
    cred2 = AgentCredential(agent_id="agent-2", api_key="ak_key2")
    db.add(cred1)
    db.add(cred2)
    db.commit()
    
    todo1_resp = client.post(
        "/agent/todos",
        headers={"Authorization": "Bearer ak_key1"},
        json={"title": "Agent 1 task"}
    )
    todo1_id = todo1_resp.json()["id"]
    
    subtask_resp = client.post(
        f"/agent/todos/{todo1_id}/subtasks",
        headers={"Authorization": "Bearer ak_key1"},
        json={"title": "Subtask", "order": 1}
    )
    subtask_id = subtask_resp.json()["id"]
    
    todo2_resp = client.post(
        "/agent/todos",
        headers={"Authorization": "Bearer ak_key2"},
        json={"title": "Agent 2 task"}
    )
    todo2_id = todo2_resp.json()["id"]
    
    response = client.post(
        f"/agent/todos/{todo2_id}/subtasks/{subtask_id}/done",
        headers={"Authorization": "Bearer ak_key2"}
    )
    assert response.status_code == 404
