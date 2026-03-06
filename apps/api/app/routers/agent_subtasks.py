# 功能描述：Agent 待办子任务的 API 路由
# 参数说明：见各接口注释
# 返回值：标准 RESTful JSON 响应
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..db.session import get_session
from ..models.agent_subtask import AgentSubtask
from ..models.agent_todo import AgentTodo
from ..schemas.agent_subtask import AgentSubtaskCreate, AgentSubtaskUpdate, AgentSubtaskOut
from ..dependencies_agent import get_agent_id

router = APIRouter(prefix="/agent/todos/{todo_id}/subtasks", tags=["agent-subtasks"])


def _verify_todo_ownership(todo_id: int, agent_id: str, db: Session) -> AgentTodo:
    """验证待办是否属于当前 Agent"""
    todo = db.execute(
        select(AgentTodo)
        .where(AgentTodo.id == todo_id)
        .where(AgentTodo.agent_id == agent_id)
    ).scalar_one_or_none()
    if not todo:
        raise HTTPException(status_code=404, detail="Agent todo not found")
    return todo


@router.get("", response_model=list[AgentSubtaskOut])
def list_subtasks(
    todo_id: int,
    agent_id: str = Depends(get_agent_id),
    db: Session = Depends(get_session)
):
    """获取指定待办的子任务列表"""
    _verify_todo_ownership(todo_id, agent_id, db)
    return db.execute(
        select(AgentSubtask)
        .where(AgentSubtask.agent_todo_id == todo_id)
        .order_by(AgentSubtask.order, AgentSubtask.id)
    ).scalars().all()


@router.post("", response_model=AgentSubtaskOut, status_code=201)
def create_subtask(
    todo_id: int,
    req: AgentSubtaskCreate,
    agent_id: str = Depends(get_agent_id),
    db: Session = Depends(get_session)
):
    """为指定待办创建子任务"""
    _verify_todo_ownership(todo_id, agent_id, db)
    subtask = AgentSubtask(agent_todo_id=todo_id, **req.model_dump())
    db.add(subtask)
    db.commit()
    db.refresh(subtask)
    return subtask


@router.put("/{subtask_id}", response_model=AgentSubtaskOut)
def update_subtask(
    todo_id: int,
    subtask_id: int,
    req: AgentSubtaskUpdate,
    agent_id: str = Depends(get_agent_id),
    db: Session = Depends(get_session)
):
    """更新指定子任务"""
    _verify_todo_ownership(todo_id, agent_id, db)
    subtask = db.execute(
        select(AgentSubtask)
        .where(AgentSubtask.id == subtask_id)
        .where(AgentSubtask.agent_todo_id == todo_id)
    ).scalar_one_or_none()
    if not subtask:
        raise HTTPException(status_code=404, detail="Subtask not found")
    for k, v in req.model_dump(exclude_unset=True).items():
        setattr(subtask, k, v)
    db.add(subtask)
    db.commit()
    db.refresh(subtask)
    return subtask


@router.post("/{subtask_id}/done", response_model=AgentSubtaskOut)
def mark_subtask_done(
    todo_id: int,
    subtask_id: int,
    agent_id: str = Depends(get_agent_id),
    db: Session = Depends(get_session)
):
    """标记子任务为已完成"""
    _verify_todo_ownership(todo_id, agent_id, db)
    subtask = db.execute(
        select(AgentSubtask)
        .where(AgentSubtask.id == subtask_id)
        .where(AgentSubtask.agent_todo_id == todo_id)
    ).scalar_one_or_none()
    if not subtask:
        raise HTTPException(status_code=404, detail="Subtask not found")
    subtask.done = True
    db.add(subtask)
    db.commit()
    db.refresh(subtask)
    return subtask


@router.delete("/{subtask_id}", status_code=204)
def delete_subtask(
    todo_id: int,
    subtask_id: int,
    agent_id: str = Depends(get_agent_id),
    db: Session = Depends(get_session)
):
    """删除指定子任务"""
    _verify_todo_ownership(todo_id, agent_id, db)
    subtask = db.execute(
        select(AgentSubtask)
        .where(AgentSubtask.id == subtask_id)
        .where(AgentSubtask.agent_todo_id == todo_id)
    ).scalar_one_or_none()
    if not subtask:
        raise HTTPException(status_code=404, detail="Subtask not found")
    db.delete(subtask)
    db.commit()
    return None
