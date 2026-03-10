import pytest
from fastapi.testclient import TestClient
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

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
