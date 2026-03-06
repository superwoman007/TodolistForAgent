# 功能描述：Agent 待办事项的请求/响应数据模型
# 参数说明：见各字段注释
# 返回值：Pydantic 模型
from pydantic import BaseModel
from datetime import datetime


class AgentTodoCreate(BaseModel):
    title: str
    description: str | None = None
    priority: str = "normal"
    due_at: datetime | None = None
    repeat_rule: str = "none"


class AgentTodoUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    priority: str | None = None
    due_at: datetime | None = None
    repeat_rule: str | None = None
    status: str | None = None


class AgentTodoDone(BaseModel):
    result: str | None = None


class AgentTodoOut(BaseModel):
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

    class Config:
        from_attributes = True


class AgentTodoStats(BaseModel):
    pending: int
    done: int
    failed: int
    overdue: int
    total: int
