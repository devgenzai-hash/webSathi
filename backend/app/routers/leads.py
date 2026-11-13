"""
Lead capture router — Phase 1.
POST /api/v1/chat/capture-lead     widget submits visitor email
GET  /sites/{site_id}/leads        dashboard views captured leads
"""
import httpx
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.middleware.auth import get_current_user, validate_site_key, validate_widget_domain
from app.models.models import LeadCapture, Site, User
from app.schemas.schemas import LeadCaptureRequest, LeadCaptureResponse

router = APIRouter(tags=["Leads"])


@router.post("/chat/capture-lead", response_model=LeadCaptureResponse, status_code=201)
async def capture_lead(
    request: Request,
    payload: LeadCaptureRequest,
    db: Session = Depends(get_db),
    site: Site = Depends(validate_site_key),
):
    """Called by the widget when the bot can't answer and the visitor leaves their email."""
    validate_widget_domain(site, request, payload.page_url)

    lead = LeadCapture(
        site_id=site.id,
        session_id=payload.session_id,
        visitor_id=payload.visitor_id,
        email=payload.email,
        question=payload.question,
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)

    # ── Phase 3: Fire Zapier / CRM webhook if configured ────────────────
    if settings.INTEGRATIONS_ENABLED and site.webhook_url:
        await _fire_webhook(site.webhook_url, lead)

    return LeadCaptureResponse.model_validate(lead)


@router.get("/sites/{site_id}/leads", response_model=List[LeadCaptureResponse])
def list_leads(
    site_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    site = db.query(Site).filter(Site.id == site_id, Site.user_id == current_user.id).first()
    if not site:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site not found")

    leads = (
        db.query(LeadCapture)
        .filter(LeadCapture.site_id == site_id)
        .order_by(LeadCapture.created_at.desc())
        .all()
    )
    return [LeadCaptureResponse.model_validate(l) for l in leads]


async def _fire_webhook(url: str, lead: LeadCapture) -> None:
    payload = {
        "event": "lead.captured",
        "email": lead.email,
        "question": lead.question,
        "visitor_id": lead.visitor_id,
        "site_id": lead.site_id,
        "created_at": lead.created_at.isoformat(),
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            await client.post(url, json=payload)
    except Exception:
        pass  # Webhook failure must not break the lead capture response
