"""
Audit log router — Phase 4.
GET /sites/{site_id}/audit   view audit trail for a site
GET /audit                   view all audit entries for current user
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.models import AuditLog, Site, User
from app.schemas.schemas import AuditLogResponse

router = APIRouter(tags=["Audit"])


@router.get("/sites/{site_id}/audit", response_model=List[AuditLogResponse])
def get_site_audit(
    site_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    site = db.query(Site).filter(Site.id == site_id, Site.user_id == current_user.id).first()
    if not site:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site not found")

    logs = (
        db.query(AuditLog)
        .filter(AuditLog.site_id == site_id)
        .order_by(AuditLog.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [AuditLogResponse.model_validate(log) for log in logs]


@router.get("/audit", response_model=List[AuditLogResponse])
def get_user_audit(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    logs = (
        db.query(AuditLog)
        .filter(AuditLog.user_id == current_user.id)
        .order_by(AuditLog.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [AuditLogResponse.model_validate(log) for log in logs]
