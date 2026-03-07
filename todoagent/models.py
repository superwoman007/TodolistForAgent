"""数据模型定义"""

import uuid
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any


class Priority(str, Enum):
    """任务优先级"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Status(str, Enum):
    """任务状态"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class Task:
    """任务模型"""

    def __init__(
        self,
        title: str,
        priority: str = "medium",
        tags: Optional[List[str]] = None,
        due_date: Optional[str] = None,
        description: str = "",
        task_id: Optional[str] = None,
        status: str = "pending",
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
        completed_at: Optional[str] = None,
    ):
        self.id = task_id or uuid.uuid4().hex[:8]
        self.title = title
        self.description = description
        self.priority = Priority(priority)
        self.status = Status(status)
        self.tags = tags or []
        self.due_date = due_date
        self.created_at = created_at or datetime.now().isoformat()
        self.updated_at = updated_at or datetime.now().isoformat()
        self.completed_at = completed_at

    def complete(self):
        """标记任务为已完成"""
        self.status = Status.COMPLETED
        self.completed_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()

    def start(self):
        """标记任务为进行中"""
        self.status = Status.IN_PROGRESS
        self.updated_at = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority.value,
            "status": self.status.value,
            "tags": self.tags,
            "due_date": self.due_date,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "completed_at": self.completed_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """从字典创建任务"""
        return cls(
            title=data["title"],
            priority=data.get("priority", "medium"),
            tags=data.get("tags", []),
            due_date=data.get("due_date"),
            description=data.get("description", ""),
            task_id=data.get("id"),
            status=data.get("status", "pending"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            completed_at=data.get("completed_at"),
        )

    @property
    def is_overdue(self) -> bool:
        """检查任务是否过期"""
        if not self.due_date or self.status == Status.COMPLETED:
            return False
        try:
            due = datetime.fromisoformat(self.due_date)
            return datetime.now() > due
        except ValueError:
            return False

    def __repr__(self) -> str:
        return f"Task(id={self.id}, title='{self.title}', status={self.status.value}, priority={self.priority.value})"
