"""
Audit log service — write a structured entry for every state-changing action.
Phase 4 feature.
"""
from typing import Optional
from sqlalchemy.orm import Session
from app.models.models import AuditLog


def log_action(
    db: Session,
    action: str,
    user_id: Optional[str] = None,
    site_id: Optional[str] = None,
    detail: Optional[str] = None,
    ip_address: Optional[str] = None,
) -> None:
    entry = AuditLog(
        user_id=user_id,
        site_id=site_id,
        action=action,
        detail=detail,
        ip_address=ip_address,
    )
    db.add(entry)
    db.commit()
