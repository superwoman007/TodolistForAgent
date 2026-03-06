# 功能描述：Agent 凭证的请求/响应数据模型
# 参数说明：见各字段注释
# 返回值：Pydantic 模型
from pydantic import BaseModel
from datetime import datetime


class AgentCredentialCreate(BaseModel):
    agent_id: str
    name: str | None = None


class AgentCredentialOut(BaseModel):
    agent_id: str
    api_key: str
    name: str | None
    created_at: datetime | None = None
    last_used_at: datetime | None = None

    class Config:
        from_attributes = True
