# 功能描述：Agent 认证依赖注入
# 参数说明：从 Authorization header 提取 API Key
# 返回值：认证后的 agent_id
from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from .db.session import get_session
from .models.agent_credential import AgentCredential


def get_agent_id(
    authorization: str | None = Header(None),
    db: Session = Depends(get_session),
) -> str:
    """从 Authorization header 验证 API Key 并返回 agent_id"""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 支持 "Bearer <api_key>" 格式
    parts = authorization.split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        api_key = parts[1]
    else:
        api_key = authorization

    # 验证 API Key
    credential = db.query(AgentCredential).filter(
        AgentCredential.api_key == api_key
    ).first()

    if not credential:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 更新最后使用时间
    credential.last_used_at = datetime.now(timezone.utc)
    db.add(credential)
    db.commit()

    return credential.agent_id
