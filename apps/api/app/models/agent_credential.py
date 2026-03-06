# 功能描述：Agent 凭证管理模型
# 参数说明：无
# 返回值：SQLAlchemy ORM 模型类
from sqlalchemy import Column, String, DateTime, func
from ..db.session import Base


class AgentCredential(Base):
    __tablename__ = "agent_credentials"

    agent_id = Column(String(255), primary_key=True, index=True)
    api_key = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=True)  # Agent 名称（可选）
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_used_at = Column(DateTime(timezone=True), nullable=True)
