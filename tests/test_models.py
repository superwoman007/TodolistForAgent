"""测试数据模型"""

import pytest
from todoagent.models import Task, Priority, Status


class TestTask:
    def test_create_task_defaults(self):
        task = Task("测试任务")
        assert task.title == "测试任务"
        assert task.priority == Priority.MEDIUM
        assert task.status == Status.PENDING
        assert task.tags == []
        assert task.due_date is None
        assert task.id is not None
        assert len(task.id) == 8

    def test_create_task_with_params(self):
        task = Task(
            "重要任务",
            priority="high",
            tags=["work", "urgent"],
            due_date="2026-03-15",
            description="这是一个重要任务",
        )
        assert task.title == "重要任务"
        assert task.priority == Priority.HIGH
        assert task.tags == ["work", "urgent"]
        assert task.due_date == "2026-03-15"
        assert task.description == "这是一个重要任务"

    def test_complete_task(self):
        task = Task("测试完成")
        task.complete()
        assert task.status == Status.COMPLETED
        assert task.completed_at is not None

    def test_start_task(self):
        task = Task("测试进行中")
        task.start()
        assert task.status == Status.IN_PROGRESS

    def test_to_dict(self):
        task = Task("字典测试", priority="low", tags=["test"])
        d = task.to_dict()
        assert d["title"] == "字典测试"
        assert d["priority"] == "low"
        assert d["status"] == "pending"
        assert d["tags"] == ["test"]

    def test_from_dict(self):
        data = {
            "id": "abc12345",
            "title": "从字典创建",
            "priority": "high",
            "status": "completed",
            "tags": ["restored"],
            "due_date": "2026-04-01",
            "description": "测试",
            "created_at": "2026-03-01T00:00:00",
            "updated_at": "2026-03-01T00:00:00",
            "completed_at": "2026-03-02T00:00:00",
        }
        task = Task.from_dict(data)
        assert task.id == "abc12345"
        assert task.title == "从字典创建"
        assert task.priority == Priority.HIGH
        assert task.status == Status.COMPLETED

    def test_is_overdue(self):
        # 过去的日期应该标记为过期
        task = Task("过期任务", due_date="2020-01-01")
        assert task.is_overdue is True

        # 未来的日期不应过期
        task2 = Task("未过期任务", due_date="2030-12-31")
        assert task2.is_overdue is False

        # 已完成的不算过期
        task3 = Task("已完成任务", due_date="2020-01-01")
        task3.complete()
        assert task3.is_overdue is False

    def test_repr(self):
        task = Task("repr测试")
        r = repr(task)
        assert "repr测试" in r
        assert "pending" in r
