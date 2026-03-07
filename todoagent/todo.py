"""核心 TodoList 逻辑"""

from datetime import datetime
from typing import List, Optional, Dict, Any

from .models import Task, Priority, Status
from .storage import Storage


class TodoList:
    """Agent 任务管理器"""

    def __init__(self, storage_path: Optional[str] = None):
        self.storage = Storage(storage_path)
        self._tasks: List[Task] = self.storage.load()

    def _save(self):
        """持久化保存"""
        self.storage.save(self._tasks)

    def add(
        self,
        title: str,
        priority: str = "medium",
        tags: Optional[List[str]] = None,
        due_date: Optional[str] = None,
        description: str = "",
    ) -> Dict[str, Any]:
        """添加新任务"""
        task = Task(
            title=title,
            priority=priority,
            tags=tags,
            due_date=due_date,
            description=description,
        )
        self._tasks.append(task)
        self._save()
        return task.to_dict()

    def get(self, task_id: str) -> Optional[Dict[str, Any]]:
        """根据 ID 获取任务"""
        for task in self._tasks:
            if task.id == task_id:
                return task.to_dict()
        return None

    def list_tasks(
        self,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        tag: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """列出任务，支持筛选"""
        result = self._tasks

        if status:
            result = [t for t in result if t.status.value == status]

        if priority:
            result = [t for t in result if t.priority.value == priority]

        if tag:
            result = [t for t in result if tag in t.tags]

        return [t.to_dict() for t in result]

    def complete(self, task_id: str) -> Optional[Dict[str, Any]]:
        """标记任务完成"""
        for task in self._tasks:
            if task.id == task_id:
                task.complete()
                self._save()
                return task.to_dict()
        return None

    def start(self, task_id: str) -> Optional[Dict[str, Any]]:
        """标记任务为进行中"""
        for task in self._tasks:
            if task.id == task_id:
                task.start()
                self._save()
                return task.to_dict()
        return None

    def update(
        self,
        task_id: str,
        title: Optional[str] = None,
        priority: Optional[str] = None,
        tags: Optional[List[str]] = None,
        due_date: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """更新任务"""
        for task in self._tasks:
            if task.id == task_id:
                if title is not None:
                    task.title = title
                if priority is not None:
                    task.priority = Priority(priority)
                if tags is not None:
                    task.tags = tags
                if due_date is not None:
                    task.due_date = due_date
                if description is not None:
                    task.description = description
                task.updated_at = datetime.now().isoformat()
                self._save()
                return task.to_dict()
        return None

    def remove(self, task_id: str) -> bool:
        """删除任务"""
        for i, task in enumerate(self._tasks):
            if task.id == task_id:
                self._tasks.pop(i)
                self._save()
                return True
        return False

    def clear_completed(self) -> int:
        """清除所有已完成任务，返回清除数量"""
        original_count = len(self._tasks)
        self._tasks = [t for t in self._tasks if t.status != Status.COMPLETED]
        removed = original_count - len(self._tasks)
        if removed > 0:
            self._save()
        return removed

    def summary(self) -> Dict[str, Any]:
        """获取任务摘要统计"""
        total = len(self._tasks)
        pending = sum(1 for t in self._tasks if t.status == Status.PENDING)
        in_progress = sum(1 for t in self._tasks if t.status == Status.IN_PROGRESS)
        completed = sum(1 for t in self._tasks if t.status == Status.COMPLETED)
        overdue = sum(1 for t in self._tasks if t.is_overdue)

        priority_counts = {
            "high": sum(1 for t in self._tasks if t.priority == Priority.HIGH and t.status != Status.COMPLETED),
            "medium": sum(1 for t in self._tasks if t.priority == Priority.MEDIUM and t.status != Status.COMPLETED),
            "low": sum(1 for t in self._tasks if t.priority == Priority.LOW and t.status != Status.COMPLETED),
        }

        return {
            "total": total,
            "pending": pending,
            "in_progress": in_progress,
            "completed": completed,
            "overdue": overdue,
            "priority": priority_counts,
        }
