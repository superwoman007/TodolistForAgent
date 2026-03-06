from .session import Base, engine
from ..models.agent_credential import AgentCredential  # noqa: F401
from ..models.agent_todo import AgentTodo  # noqa: F401
from ..models.agent_subtask import AgentSubtask  # noqa: F401


# 功能描述：初始化数据库，创建所有模型对应的表
# 参数说明：无
# 返回值：无
def init_db() -> None:
    Base.metadata.create_all(bind=engine)
