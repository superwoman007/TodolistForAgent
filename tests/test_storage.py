"""测试持久化存储"""

import os
import json
import tempfile
import pytest

from todoagent.storage import Storage
from todoagent.models import Task


class TestStorage:
    def setup_method(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self.tmp.close()
        self.storage = Storage(storage_path=self.tmp.name)

    def teardown_method(self):
        if os.path.exists(self.tmp.name):
            os.unlink(self.tmp.name)

    def test_load_empty(self):
        os.unlink(self.tmp.name)
        tasks = self.storage.load()
        assert tasks == []

    def test_save_and_load(self):
        tasks = [
            Task("任务一", priority="high"),
            Task("任务二", priority="low", tags=["test"]),
        ]
        self.storage.save(tasks)

        loaded = self.storage.load()
        assert len(loaded) == 2
        assert loaded[0].title == "任务一"
        assert loaded[1].title == "任务二"
        assert loaded[1].tags == ["test"]

    def test_load_corrupted_json(self):
        with open(self.tmp.name, "w") as f:
            f.write("not valid json{{{")
        tasks = self.storage.load()
        assert tasks == []

    def test_clear(self):
        tasks = [Task("临时任务")]
        self.storage.save(tasks)
        assert os.path.exists(self.tmp.name)

        self.storage.clear()
        assert not os.path.exists(self.tmp.name)
