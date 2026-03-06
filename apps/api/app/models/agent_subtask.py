# 功能描述：Agent 待办子任务数据库模型
# 参数说明：无
# 返回值：SQLAlchemy ORM 模型类
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from ..db.session import Base


class AgentSubtask(Base):
    __tablename__ = "agent_subtasks"

    id = Column(Integer, primary_key=True, index=True)
    agent_todo_id = Column(Integer, ForeignKey("agent_todos.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)  # 子任务执行说明
    done = Column(Boolean, default=False)
    order = Column(Integer, default=0)

    # 关系：父任务
    parent = relationship("AgentTodo", backref="subtasks")
