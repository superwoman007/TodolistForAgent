# 功能描述：Agent 凭证的请求/响应数据模型
# 参数说明：见各字段注释
# 返回值：Pydantic 模型
from pydantic import BaseModel, field_validator, ConfigDict
from datetime import datetime


class AgentCredentialCreate(BaseModel):
    agent_id: str
    name: str | None = None

    @field_validator("agent_id")
    @classmethod
    def agent_id_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("agent_id cannot be empty")
        return v.strip()


class AgentCredentialOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    agent_id: str
    api_key: str
    name: str | None
    created_at: datetime | None = None
    last_used_at: datetime | None = None
