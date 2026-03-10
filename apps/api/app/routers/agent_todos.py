# 功能描述：Agent 待办事项的 API 路由
# 参数说明：见各接口注释
# 返回值：标准 RESTful JSON 响应
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, func as sa_func, case
from datetime import datetime, timezone, timedelta
import calendar
from ..db.session import get_session
from ..models.agent_todo import AgentTodo
from ..schemas.agent_todo import (
    AgentTodoCreate,
    AgentTodoUpdate,
    AgentTodoDone,
    AgentTodoOut,
    AgentTodoStats,
)
from ..dependencies_agent import get_agent_id

router = APIRouter(prefix="/agent/todos", tags=["agent-todos"])

PRIORITY_WEIGHT = case(
    (AgentTodo.priority == "urgent", 4),
    (AgentTodo.priority == "high", 3),
    (AgentTodo.priority == "normal", 2),
    (AgentTodo.priority == "low", 1),
    else_=0
)


def _add_months(dt: datetime, months: int) -> datetime:
    """Add months to a datetime, handling end-of-month edge cases.
    
    If the resulting month has fewer days than the original day,
    the day is clamped to the last day of the month.
    """
    tz = dt.tzinfo
    dt_naive = dt.replace(tzinfo=None)
    year = dt_naive.year + (dt_naive.month - 1 + months) // 12
    month = (dt_naive.month - 1 + months) % 12 + 1
    
    max_day = calendar.monthrange(year, month)[1]
    day = min(dt_naive.day, max_day)
    
    result = dt_naive.replace(year=year, month=month, day=day)
    if tz is not None:
        result = result.replace(tzinfo=tz)
    return result


def _next_due(current_due: datetime, rule: str) -> datetime | None:
    """根据重复规则计算下一次执行时间"""
    if current_due is None:
        return None
    tz = current_due.tzinfo
    if rule == "daily":
        new_due = current_due + timedelta(days=1)
    elif rule == "weekly":
        new_due = current_due + timedelta(weeks=1)
    elif rule == "monthly":
        new_due = _add_months(current_due, 1)
    else:
        return None
    if tz is not None:
        new_due = new_due.replace(tzinfo=tz)
    return new_due


# ── 查询待办列表 ──────────────────────────────────────────
@router.get("", response_model=list[AgentTodoOut])
def list_agent_todos(
    agent_id: str = Depends(get_agent_id),
    status: str = Query("pending", description="pending / done / failed / all"),
    due_before: str | None = Query(None, description="ISO datetime 或 'now'，筛选到期任务"),
    priority: str | None = Query(None, description="low / normal / high / urgent"),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_session),
):
    stmt = select(AgentTodo).where(AgentTodo.agent_id == agent_id)

    if status != "all":
        stmt = stmt.where(AgentTodo.status == status)

    if due_before:
        if due_before.lower() == "now":
            cutoff = datetime.now(timezone.utc)
        else:
            cutoff = datetime.fromisoformat(due_before)
        stmt = stmt.where(AgentTodo.due_at <= cutoff)

    if priority:
        stmt = stmt.where(AgentTodo.priority == priority)

    stmt = stmt.order_by(AgentTodo.due_at.asc().nullslast(), AgentTodo.created_at.desc())
    stmt = stmt.limit(limit)
    return db.execute(stmt).scalars().all()


# ── 获取到期待执行任务（巡检接口） ───────────────────────────
@router.get("/check", response_model=list[AgentTodoOut])
def check_due_todos(
    agent_id: str = Depends(get_agent_id),
    db: Session = Depends(get_session)
):
    now = datetime.now(timezone.utc)
    stmt = (
        select(AgentTodo)
        .where(AgentTodo.agent_id == agent_id)
        .where(AgentTodo.status == "pending")
        .where(AgentTodo.due_at <= now)
        .order_by(PRIORITY_WEIGHT.desc(), AgentTodo.due_at.asc())
    )
    return db.execute(stmt).scalars().all()


# ── 统计信息 ──────────────────────────────────────────────
@router.get("/stats", response_model=AgentTodoStats)
def get_stats(
    agent_id: str = Depends(get_agent_id),
    db: Session = Depends(get_session)
):
    now = datetime.now(timezone.utc)

    total = db.execute(
        select(sa_func.count(AgentTodo.id)).where(AgentTodo.agent_id == agent_id)
    ).scalar() or 0
    pending = db.execute(
        select(sa_func.count(AgentTodo.id))
        .where(AgentTodo.agent_id == agent_id)
        .where(AgentTodo.status == "pending")
    ).scalar() or 0
    done = db.execute(
        select(sa_func.count(AgentTodo.id))
        .where(AgentTodo.agent_id == agent_id)
        .where(AgentTodo.status == "done")
    ).scalar() or 0
    failed = db.execute(
        select(sa_func.count(AgentTodo.id))
        .where(AgentTodo.agent_id == agent_id)
        .where(AgentTodo.status == "failed")
    ).scalar() or 0
    overdue = db.execute(
        select(sa_func.count(AgentTodo.id))
        .where(AgentTodo.agent_id == agent_id)
        .where(AgentTodo.status == "pending")
        .where(AgentTodo.due_at <= now)
    ).scalar() or 0

    return AgentTodoStats(
        pending=pending, done=done, failed=failed, overdue=overdue, total=total
    )


# ── 创建待办 ──────────────────────────────────────────────
@router.post("", response_model=AgentTodoOut, status_code=201)
def create_agent_todo(
    req: AgentTodoCreate,
    agent_id: str = Depends(get_agent_id),
    db: Session = Depends(get_session)
):
    todo = AgentTodo(agent_id=agent_id, **req.model_dump())
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo


# ── 获取待办详情 ──────────────────────────────────────────
@router.get("/{todo_id}", response_model=AgentTodoOut)
def get_agent_todo(
    todo_id: int,
    agent_id: str = Depends(get_agent_id),
    db: Session = Depends(get_session)
):
    todo = db.execute(
        select(AgentTodo)
        .where(AgentTodo.id == todo_id)
        .where(AgentTodo.agent_id == agent_id)
    ).scalar_one_or_none()
    if not todo:
        raise HTTPException(status_code=404, detail="Agent todo not found")
    return todo


# ── 更新待办 ──────────────────────────────────────────────
@router.put("/{todo_id}", response_model=AgentTodoOut)
def update_agent_todo(
    todo_id: int,
    req: AgentTodoUpdate,
    agent_id: str = Depends(get_agent_id),
    db: Session = Depends(get_session)
):
    todo = db.execute(
        select(AgentTodo)
        .where(AgentTodo.id == todo_id)
        .where(AgentTodo.agent_id == agent_id)
    ).scalar_one_or_none()
    if not todo:
        raise HTTPException(status_code=404, detail="Agent todo not found")
    for k, v in req.model_dump(exclude_unset=True).items():
        setattr(todo, k, v)
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo


# ── 标记完成 ──────────────────────────────────────────────
@router.post("/{todo_id}/done", response_model=AgentTodoOut)
def mark_done(
    todo_id: int,
    req: AgentTodoDone,
    agent_id: str = Depends(get_agent_id),
    db: Session = Depends(get_session)
):
    todo = db.execute(
        select(AgentTodo)
        .where(AgentTodo.id == todo_id)
        .where(AgentTodo.agent_id == agent_id)
    ).scalar_one_or_none()
    if not todo:
        raise HTTPException(status_code=404, detail="Agent todo not found")

    now = datetime.now(timezone.utc)
    todo.status = "done"
    todo.completed_at = now
    todo.last_run_at = now
    if req.result:
        todo.result = req.result

    # 如果是重复任务，创建下一个周期的任务
    if todo.repeat_rule and todo.repeat_rule != "none" and todo.due_at:
        next_due = _next_due(todo.due_at, todo.repeat_rule)
        if next_due:
            next_todo = AgentTodo(
                agent_id=agent_id,
                title=todo.title,
                description=todo.description,
                priority=todo.priority,
                due_at=next_due,
                repeat_rule=todo.repeat_rule,
                status="pending",
            )
            db.add(next_todo)

    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo


# ── 标记失败 ──────────────────────────────────────────────
@router.post("/{todo_id}/fail", response_model=AgentTodoOut)
def mark_failed(
    todo_id: int,
    req: AgentTodoDone,
    agent_id: str = Depends(get_agent_id),
    db: Session = Depends(get_session)
):
    todo = db.execute(
        select(AgentTodo)
        .where(AgentTodo.id == todo_id)
        .where(AgentTodo.agent_id == agent_id)
    ).scalar_one_or_none()
    if not todo:
        raise HTTPException(status_code=404, detail="Agent todo not found")

    now = datetime.now(timezone.utc)
    todo.status = "failed"
    todo.last_run_at = now
    if req.result:
        todo.result = req.result

    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo


# ── 删除待办 ──────────────────────────────────────────────
@router.delete("/{todo_id}", status_code=204)
def delete_agent_todo(
    todo_id: int,
    agent_id: str = Depends(get_agent_id),
    db: Session = Depends(get_session)
):
    todo = db.execute(
        select(AgentTodo)
        .where(AgentTodo.id == todo_id)
        .where(AgentTodo.agent_id == agent_id)
    ).scalar_one_or_none()
    if not todo:
        raise HTTPException(status_code=404, detail="Agent todo not found")
    db.delete(todo)
    db.commit()
    return None
