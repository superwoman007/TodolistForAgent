# 功能描述：Agent 凭证管理 API 路由
# 参数说明：见各接口注释
# 返回值：标准 RESTful JSON 响应
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
import secrets
from ..db.session import get_session
from ..models.agent_credential import AgentCredential
from ..schemas.agent_credential import AgentCredentialCreate, AgentCredentialOut
from ..dependencies_agent import require_admin

router = APIRouter(prefix="/agent/credentials", tags=["agent-credentials"])


def _generate_api_key() -> str:
    """生成安全的 API Key"""
    return f"ak_{secrets.token_urlsafe(32)}"


@router.post("", response_model=AgentCredentialOut, status_code=201)
def create_credential(req: AgentCredentialCreate, db: Session = Depends(get_session)):
    """创建 Agent 凭证并生成 API Key"""
    # 检查 agent_id 是否已存在
    existing = db.execute(
        select(AgentCredential).where(AgentCredential.agent_id == req.agent_id)
    ).scalar_one_or_none()
    
    if existing:
        raise HTTPException(status_code=400, detail="Agent ID already exists")
    
    # 生成 API Key
    api_key = _generate_api_key()
    
    credential = AgentCredential(
        agent_id=req.agent_id,
        api_key=api_key,
        name=req.name
    )
    db.add(credential)
    db.commit()
    db.refresh(credential)
    return credential


@router.get("", response_model=list[AgentCredentialOut])
def list_credentials(db: Session = Depends(get_session), _: bool = Depends(require_admin)):
    """列出所有 Agent 凭证（管理接口，需 ADMIN_TOKEN）"""
    return db.execute(select(AgentCredential)).scalars().all()


@router.delete("/{agent_id}", status_code=204)
def delete_credential(agent_id: str, db: Session = Depends(get_session), _: bool = Depends(require_admin)):
    """删除 Agent 凭证（管理接口，需 ADMIN_TOKEN）"""
    credential = db.execute(
        select(AgentCredential).where(AgentCredential.agent_id == agent_id)
    ).scalar_one_or_none()
    
    if not credential:
        raise HTTPException(status_code=404, detail="Credential not found")
    
    db.delete(credential)
    db.commit()
    return None
