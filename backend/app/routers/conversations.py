"""
Conversation logs router — Phase 1.
GET /sites/{site_id}/conversations              list sessions with summary
GET /sites/{site_id}/conversations/{session}    full session with messages
GET /sites/{site_id}/unanswered                 questions bot couldn't answer
GET /sites/{site_id}/usage                      monthly usage stats
"""
from datetime import date
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.models import ChatMessage, ChatSession, Document, Site, User
from app.schemas.schemas import (
    ConversationDetail,
    ConversationSummary,
    UnansweredQuestion,
    UsageStats,
    ChatMessageResponse,
)

router = APIRouter(tags=["Conversations"])


@router.get("/sites/{site_id}/conversations", response_model=List[ConversationSummary])
def list_conversations(
    site_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    site = db.query(Site).filter(Site.id == site_id, Site.user_id == current_user.id).first()
    if not site:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site not found")

    sessions = (
        db.query(ChatSession)
        .filter(ChatSession.site_id == site_id)
        .order_by(ChatSession.last_message_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    result = []
    for s in sessions:
        msgs = s.messages or []
        has_unanswered = any(
            not getattr(m, "was_answered", True) for m in msgs if m.role == "assistant"
        )
        has_negative = any(
            getattr(m, "sentiment", "neutral") == "negative" for m in msgs if m.role == "user"
        )
        result.append(
            ConversationSummary(
                session_id=s.id,
                visitor_id=s.visitor_id,
                message_count=len(msgs),
                last_message_at=s.last_message_at,
                has_unanswered=has_unanswered,
                has_negative_sentiment=has_negative,
            )
        )
    return result


@router.get("/sites/{site_id}/conversations/{session_id}", response_model=ConversationDetail)
def get_conversation(
    site_id: str,
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    site = db.query(Site).filter(Site.id == site_id, Site.user_id == current_user.id).first()
    if not site:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site not found")

    session = db.query(ChatSession).filter(
        ChatSession.id == session_id, ChatSession.site_id == site_id
    ).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    msgs = sorted(session.messages, key=lambda m: m.created_at)
    return ConversationDetail(
        session_id=session.id,
        visitor_id=session.visitor_id,
        messages=[ChatMessageResponse.model_validate(m) for m in msgs],
        created_at=session.created_at,
        last_message_at=session.last_message_at,
    )


@router.get("/sites/{site_id}/unanswered", response_model=List[UnansweredQuestion])
def list_unanswered(
    site_id: str,
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    site = db.query(Site).filter(Site.id == site_id, Site.user_id == current_user.id).first()
    if not site:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site not found")

    # Find assistant messages flagged as unanswered, then pair with the preceding user message
    unanswered_sessions = (
        db.query(ChatMessage)
        .join(ChatSession, ChatMessage.session_id == ChatSession.id)
        .filter(
            ChatSession.site_id == site_id,
            ChatMessage.role == "assistant",
            ChatMessage.was_answered == False,
        )
        .order_by(ChatMessage.created_at.desc())
        .limit(limit)
        .all()
    )

    result = []
    for msg in unanswered_sessions:
        # Find the user message just before this one
        user_msg = (
            db.query(ChatMessage)
            .filter(
                ChatMessage.session_id == msg.session_id,
                ChatMessage.role == "user",
                ChatMessage.created_at < msg.created_at,
            )
            .order_by(ChatMessage.created_at.desc())
            .first()
        )
        if user_msg:
            result.append(
                UnansweredQuestion(
                    message_id=msg.id,
                    session_id=msg.session_id,
                    visitor_id=msg.session.visitor_id,
                    question=user_msg.content,
                    created_at=user_msg.created_at,
                )
            )
    return result


@router.get("/sites/{site_id}/usage", response_model=UsageStats)
def get_usage(
    site_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    site = db.query(Site).filter(Site.id == site_id, Site.user_id == current_user.id).first()
    if not site:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site not found")

    month_start = date.today().replace(day=1)

    total_messages = (
        db.query(ChatMessage)
        .join(ChatSession, ChatMessage.session_id == ChatSession.id)
        .filter(ChatSession.site_id == site_id)
        .count()
    )
    monthly_queries = (
        db.query(ChatMessage)
        .join(ChatSession, ChatMessage.session_id == ChatSession.id)
        .filter(
            ChatSession.site_id == site_id,
            ChatMessage.role == "user",
            ChatMessage.created_at >= month_start,
        )
        .count()
    )
    total_docs = db.query(Document).filter(Document.site_id == site_id).count()

    return UsageStats(
        total_messages=total_messages,
        total_documents=total_docs,
        total_tokens_used=0,
        monthly_query_count=monthly_queries,
        monthly_query_limit=site.monthly_query_limit or 50,
        billing_enabled=settings.BILLING_ENABLED,
        period=str(month_start),
    )
