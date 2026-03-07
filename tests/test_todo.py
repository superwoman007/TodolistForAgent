"""测试核心 TodoList 逻辑"""

import os
import tempfile
import pytest

from todoagent.todo import TodoList


class TestTodoList:
    def setup_method(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self.tmp.close()
        self.todo = TodoList(storage_path=self.tmp.name)

    def teardown_method(self):
        if os.path.exists(self.tmp.name):
            os.unlink(self.tmp.name)

    def test_add_task(self):
        task = self.todo.add("新任务", priority="high", tags=["work"])
        assert task["title"] == "新任务"
        assert task["priority"] == "high"
        assert task["tags"] == ["work"]
        assert task["status"] == "pending"

    def test_get_task(self):
        added = self.todo.add("查找任务")
        found = self.todo.get(added["id"])
        assert found is not None
        assert found["title"] == "查找任务"

    def test_get_nonexistent_task(self):
        found = self.todo.get("nonexistent")
        assert found is None

    def test_list_all_tasks(self):
        self.todo.add("任务1")
        self.todo.add("任务2")
        self.todo.add("任务3")
        tasks = self.todo.list_tasks()
        assert len(tasks) == 3

    def test_list_filter_by_status(self):
        t1 = self.todo.add("待办任务")
        t2 = self.todo.add("完成任务")
        self.todo.complete(t2["id"])

        pending = self.todo.list_tasks(status="pending")
        assert len(pending) == 1
        assert pending[0]["title"] == "待办任务"

        completed = self.todo.list_tasks(status="completed")
        assert len(completed) == 1
        assert completed[0]["title"] == "完成任务"

    def test_list_filter_by_priority(self):
        self.todo.add("高优先级", priority="high")
        self.todo.add("低优先级", priority="low")

        high = self.todo.list_tasks(priority="high")
        assert len(high) == 1
        assert high[0]["title"] == "高优先级"

    def test_list_filter_by_tag(self):
        self.todo.add("工作任务", tags=["work"])
        self.todo.add("个人任务", tags=["personal"])

        work = self.todo.list_tasks(tag="work")
        assert len(work) == 1
        assert work[0]["title"] == "工作任务"

    def test_complete_task(self):
        task = self.todo.add("待完成")
        result = self.todo.complete(task["id"])
        assert result["status"] == "completed"
        assert result["completed_at"] is not None

    def test_complete_nonexistent(self):
        result = self.todo.complete("fake_id")
        assert result is None

    def test_start_task(self):
        task = self.todo.add("待开始")
        result = self.todo.start(task["id"])
        assert result["status"] == "in_progress"

    def test_update_task(self):
        task = self.todo.add("原始标题", priority="low")
        result = self.todo.update(task["id"], title="新标题", priority="high")
        assert result["title"] == "新标题"
        assert result["priority"] == "high"

    def test_update_nonexistent(self):
        result = self.todo.update("fake", title="不存在")
        assert result is None

    def test_remove_task(self):
        task = self.todo.add("待删除")
        assert self.todo.remove(task["id"]) is True
        assert self.todo.get(task["id"]) is None

    def test_remove_nonexistent(self):
        assert self.todo.remove("fake") is False

    def test_clear_completed(self):
        t1 = self.todo.add("任务1")
        t2 = self.todo.add("任务2")
        t3 = self.todo.add("任务3")
        self.todo.complete(t1["id"])
        self.todo.complete(t3["id"])

        removed = self.todo.clear_completed()
        assert removed == 2
        assert len(self.todo.list_tasks()) == 1
        assert self.todo.list_tasks()[0]["title"] == "任务2"

    def test_summary(self):
        self.todo.add("高优先级待办", priority="high")
        self.todo.add("中优先级待办", priority="medium")
        t3 = self.todo.add("低优先级完成", priority="low")
        self.todo.complete(t3["id"])

        s = self.todo.summary()
        assert s["total"] == 3
        assert s["pending"] == 2
        assert s["completed"] == 1
        assert s["priority"]["high"] == 1
        assert s["priority"]["medium"] == 1
        assert s["priority"]["low"] == 0  # 已完成不计

    def test_persistence(self):
        """测试数据持久化"""
        self.todo.add("持久化测试")
        # 重新加载
        todo2 = TodoList(storage_path=self.tmp.name)
        tasks = todo2.list_tasks()
        assert len(tasks) == 1
        assert tasks[0]["title"] == "持久化测试"
