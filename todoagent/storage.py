"""持久化存储模块"""

import json
import os
from typing import List, Dict, Any, Optional
from pathlib import Path

from .models import Task


DEFAULT_STORAGE_DIR = os.path.expanduser("~/.todoagent")
DEFAULT_STORAGE_FILE = "tasks.json"


class Storage:
    """JSON 文件存储"""

    def __init__(self, storage_path: Optional[str] = None):
        if storage_path:
            self.storage_path = Path(storage_path)
        else:
            self.storage_path = Path(DEFAULT_STORAGE_DIR) / DEFAULT_STORAGE_FILE

        # 确保存储目录存在
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> List[Task]:
        """加载所有任务"""
        if not self.storage_path.exists():
            return []

        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return [Task.from_dict(item) for item in data]
        except (json.JSONDecodeError, KeyError):
            return []

    def save(self, tasks: List[Task]) -> None:
        """保存所有任务"""
        data = [task.to_dict() for task in tasks]
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def clear(self) -> None:
        """清除存储文件"""
        if self.storage_path.exists():
            self.storage_path.unlink()
