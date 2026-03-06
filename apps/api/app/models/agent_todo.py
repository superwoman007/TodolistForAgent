# 功能描述：Agent 待办事项数据库模型
# 参数说明：无
# 返回值：SQLAlchemy ORM 模型类
from sqlalchemy import Column, Integer, String, Text, DateTime, func
from ..db.session import Base


class AgentTodo(Base):
    __tablename__ = "agent_todos"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(String(255), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)           # 执行指令说明
    status = Column(String(50), default="pending", index=True)  # pending / done / failed
    priority = Column(String(50), default="normal", index=True) # low / normal / high / urgent
    due_at = Column(DateTime(timezone=True), nullable=True, index=True)
    repeat_rule = Column(String(64), default="none")    # none / daily / weekly / monthly / cron表达式
    last_run_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    result = Column(Text, nullable=True)                # 执行结果记录
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
