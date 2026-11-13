from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


# ─── Auth Schemas ───────────────────────────────────────────

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: Optional[str]
    is_active: bool
    is_verified: bool
    plan: str
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ─── Site Schemas ───────────────────────────────────────────

class SiteCreate(BaseModel):
    site_name: str = Field(..., min_length=1, max_length=255)
    domain: str = Field(..., min_length=1, max_length=512)


class SiteUpdate(BaseModel):
    site_name: Optional[str] = None
    domain: Optional[str] = None
    model_provider: Optional[str] = None
    model_name: Optional[str] = None
    system_prompt: Optional[str] = None
    max_tokens: Optional[int] = Field(None, ge=100, le=4096)
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    widget_position: Optional[str] = None
    widget_color: Optional[str] = None
    widget_title: Optional[str] = None
    widget_welcome_message: Optional[str] = None
    # Phase 2
    hide_branding: Optional[bool] = None
    monthly_query_limit: Optional[int] = Field(None, ge=1, le=100000)
    user_openai_key: Optional[str] = None
    # Phase 3
    recrawl_interval_hours: Optional[int] = Field(None, ge=0, le=8760)
    webhook_url: Optional[str] = Field(None, max_length=2048)
    ab_testing_enabled: Optional[bool] = None


class SiteResponse(BaseModel):
    id: str
    site_name: str
    domain: str
    site_key: str
    is_verified: bool
    is_active: bool
    model_provider: str
    model_name: str
    system_prompt: str
    max_tokens: int
    temperature: float
    widget_position: str
    widget_color: str
    widget_title: str
    widget_welcome_message: str
    # Phase 2
    hide_branding: bool = False
    monthly_query_limit: int = 50
    user_openai_key: Optional[str] = None
    # Phase 3
    recrawl_interval_hours: int = 0
    webhook_url: Optional[str] = None
    ab_testing_enabled: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Document Schemas ───────────────────────────────────────

class DocumentResponse(BaseModel):
    id: str
    site_id: str
    filename: str
    file_type: str
    file_size: int
    chunk_count: int
    status: str
    error_message: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Chat Schemas ───────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4096)
    session_id: Optional[str] = None
    visitor_id: str = Field(..., min_length=1, max_length=128)
    page_url: Optional[str] = Field(None, max_length=2048)


class ChatResponse(BaseModel):
    response: str
    session_id: str
    sources: list[str] = []
    confidence: str = "high"   # high / medium / low — used by widget for email capture


class ChatMessageResponse(BaseModel):
    id: str
    role: str
    content: str
    was_answered: bool = True
    confidence: str = "high"
    sentiment: str = "neutral"
    created_at: datetime

    class Config:
        from_attributes = True


class ChatHistoryResponse(BaseModel):
    session_id: Optional[str] = None
    messages: list[ChatMessageResponse] = Field(default_factory=list)


# ─── Conversation logs ──────────────────────────────────────

class ConversationSummary(BaseModel):
    session_id: str
    visitor_id: str
    message_count: int
    last_message_at: datetime
    has_unanswered: bool = False
    has_negative_sentiment: bool = False

    class Config:
        from_attributes = True


class ConversationDetail(BaseModel):
    session_id: str
    visitor_id: str
    messages: List[ChatMessageResponse]
    created_at: datetime
    last_message_at: datetime

    class Config:
        from_attributes = True


# ─── Unanswered questions ───────────────────────────────────

class UnansweredQuestion(BaseModel):
    message_id: str
    session_id: str
    visitor_id: str
    question: str
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Lead capture ───────────────────────────────────────────

class LeadCaptureRequest(BaseModel):
    email: EmailStr
    visitor_id: str = Field(..., min_length=1, max_length=128)
    session_id: Optional[str] = None
    question: Optional[str] = Field(None, max_length=4096)
    page_url: Optional[str] = Field(None, max_length=2048)


class LeadCaptureResponse(BaseModel):
    id: str
    site_id: str
    visitor_id: str
    email: str
    question: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Web crawler ────────────────────────────────────────────

class CrawlRequest(BaseModel):
    url: str = Field(..., min_length=8, max_length=2048)


class CrawlJobResponse(BaseModel):
    id: str
    site_id: str
    root_url: str
    status: str
    pages_crawled: int
    error_message: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


# ─── A/B Prompt variants ────────────────────────────────────

class PromptVariantCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    system_prompt: str = Field(..., min_length=1)
    is_control: bool = False


class PromptVariantUpdate(BaseModel):
    name: Optional[str] = None
    system_prompt: Optional[str] = None
    is_active: Optional[bool] = None
    is_control: Optional[bool] = None


class PromptVariantResponse(BaseModel):
    id: str
    site_id: str
    name: str
    system_prompt: str
    is_control: bool
    is_active: bool
    total_chats: int
    answered_count: int
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Audit logs ─────────────────────────────────────────────

class AuditLogResponse(BaseModel):
    id: str
    user_id: Optional[str]
    site_id: Optional[str]
    action: str
    detail: Optional[str]
    ip_address: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Model Schemas ──────────────────────────────────────────

class ModelOption(BaseModel):
    provider: str
    model_id: str
    display_name: str
    description: str
    pricing_tier: str  # free, starter, pro, enterprise


# ─── Usage Schemas ──────────────────────────────────────────

class UsageStats(BaseModel):
    total_messages: int
    total_documents: int
    total_tokens_used: int
    monthly_query_count: int
    monthly_query_limit: int
    billing_enabled: bool
    period: str
