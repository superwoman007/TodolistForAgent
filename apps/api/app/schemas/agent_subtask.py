# 功能描述：Agent 子任务的请求/响应数据模型
# 参数说明：见各字段注释
# 返回值：Pydantic 模型
from pydantic import BaseModel, ConfigDict


class AgentSubtaskCreate(BaseModel):
    title: str
    description: str | None = None
    order: int = 0


class AgentSubtaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    done: bool | None = None
    order: int | None = None


class AgentSubtaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    agent_todo_id: int
    title: str
    description: str | None
    done: bool
    order: int
