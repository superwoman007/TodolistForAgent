# 功能描述：Agent 待办事项的请求/响应数据模型
# 参数说明：见各字段注释
# 返回值：Pydantic 模型
from pydantic import BaseModel, field_validator, ConfigDict
from datetime import datetime
from typing import Literal


PRIORITY_VALUES = Literal["low", "normal", "high", "urgent"]
STATUS_VALUES = Literal["pending", "done", "failed"]
REPEAT_RULE_VALUES = Literal["none", "daily", "weekly", "monthly"]


class AgentTodoCreate(BaseModel):
    title: str
    description: str | None = None
    priority: PRIORITY_VALUES = "normal"
    due_at: datetime | None = None
    repeat_rule: REPEAT_RULE_VALUES = "none"

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("title cannot be empty")
        return v.strip()


class AgentTodoUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    priority: PRIORITY_VALUES | None = None
    due_at: datetime | None = None
    repeat_rule: REPEAT_RULE_VALUES | None = None
    status: STATUS_VALUES | None = None

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            raise ValueError("title cannot be empty")
        return v.strip() if v else v


class AgentTodoDone(BaseModel):
    result: str | None = None


class AgentTodoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    title: str
    description: str | None
    status: str
    priority: str
    due_at: datetime | None
    repeat_rule: str
    last_run_at: datetime | None
    completed_at: datetime | None
    result: str | None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class AgentTodoStats(BaseModel):
    pending: int
    done: int
    failed: int
    overdue: int
    total: int
