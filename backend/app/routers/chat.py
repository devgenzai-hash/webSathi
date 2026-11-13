from typing import Optional
from fastapi import APIRouter, Depends, Request, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.schemas import ChatHistoryResponse, ChatMessageResponse, ChatRequest, ChatResponse
from app.middleware.auth import validate_site_key, validate_widget_domain
from app.services.chat_service import process_chat_message
from app.models.models import ChatSession, Site

router = APIRouter(prefix="/chat", tags=["Chat (Widget)"])


@router.post("/", response_model=ChatResponse)
async def chat(
    request: Request,
    payload: ChatRequest,
    db: Session = Depends(get_db),
    site: Site = Depends(validate_site_key),
):
    """
    Public chat endpoint for the embeddable widget.
    Authenticated via X-Site-Key header (not user JWT).
    """
    validate_widget_domain(site, request, payload.page_url)
    result = await process_chat_message(
        db=db,
        site_id=site.id,
        message=payload.message,
        visitor_id=payload.visitor_id,
        session_id=payload.session_id,
    )
    return ChatResponse(**result)


@router.get("/config")
async def get_widget_config(
    request: Request,
    db: Session = Depends(get_db),
    site: Site = Depends(validate_site_key),
):
    """Get widget configuration for a site (called by widget on init)."""
    validate_widget_domain(site, request)
    return {
        "widget_position": site.widget_position,
        "widget_color": site.widget_color,
        "widget_title": site.widget_title,
        "widget_welcome_message": site.widget_welcome_message,
        "hide_branding": getattr(site, "hide_branding", False),
    }


@router.get("/history", response_model=ChatHistoryResponse)
async def get_chat_history(
    request: Request,
    visitor_id: str = Query(..., min_length=1, max_length=128),
    session_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    site: Site = Depends(validate_site_key),
):
    """Return persisted chat history for this browser visitor and site."""
    validate_widget_domain(site, request)

    query = db.query(ChatSession).filter(
        ChatSession.site_id == site.id,
        ChatSession.visitor_id == visitor_id,
    )

    if session_id:
        query = query.filter(ChatSession.id == session_id)

    session = query.order_by(ChatSession.last_message_at.desc()).first()
    if not session:
        return ChatHistoryResponse(session_id=None, messages=[])

    messages = sorted(session.messages, key=lambda message: message.created_at)
    return ChatHistoryResponse(
        session_id=session.id,
        messages=[ChatMessageResponse.model_validate(message) for message in messages],
    )
