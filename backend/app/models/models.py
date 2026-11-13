import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, Integer, ForeignKey, Text, Float, JSON
from sqlalchemy.orm import relationship
from app.database import Base


def generate_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    plan = Column(String, default="free")  # free, starter, pro, enterprise
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    sites = relationship("Site", back_populates="owner", cascade="all, delete-orphan")
    api_keys = relationship("ApiKey", back_populates="user", cascade="all, delete-orphan")


class Site(Base):
    __tablename__ = "sites"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    site_name = Column(String, nullable=False)
    domain = Column(String, nullable=False)
    site_key = Column(String, unique=True, nullable=False, default=generate_uuid)
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Chatbot settings
    model_provider = Column(String, default="openai")  # openai, nvidia_nim, openrouter, deepseek, ollama
    model_name = Column(String, default="gpt-4o-mini")
    system_prompt = Column(Text, default="You are a helpful assistant. Only answer questions based on the provided context. If the answer is not in the context, say 'I don't have information about that.'")
    max_tokens = Column(Integer, default=1024)
    temperature = Column(Float, default=0.3)
    
    # Widget settings
    widget_position = Column(String, default="bottom-right")
    widget_color = Column(String, default="#6366f1")
    widget_title = Column(String, default="AI Assistant")
    widget_welcome_message = Column(String, default="Hello! How can I help you today?")

    # Phase 2 — Billing & branding
    hide_branding = Column(Boolean, default=False)
    monthly_query_limit = Column(Integer, default=50)  # enforced only when BILLING_ENABLED=true
    user_openai_key = Column(String, nullable=True)    # BYOK — overrides global OPENAI_API_KEY

    # Phase 3 — Crawler & integrations
    recrawl_interval_hours = Column(Integer, default=0)  # 0 = manual only
    webhook_url = Column(String, nullable=True)          # Zapier / CRM webhook on lead capture

    # Phase 3 — A/B prompt testing
    ab_testing_enabled = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    owner = relationship("User", back_populates="sites")
    documents = relationship("Document", back_populates="site", cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSession", back_populates="site", cascade="all, delete-orphan")


class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=generate_uuid)
    site_id = Column(String, ForeignKey("sites.id"), nullable=False)
    filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)  # pdf, docx, txt, csv, image
    file_size = Column(Integer, nullable=False)
    file_path = Column(String, nullable=False)
    chunk_count = Column(Integer, default=0)
    status = Column(String, default="processing")  # processing, ready, failed
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    site = relationship("Site", back_populates="documents")


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(String, primary_key=True, default=generate_uuid)
    site_id = Column(String, ForeignKey("sites.id"), nullable=False)
    visitor_id = Column(String, nullable=False)  # Anonymous visitor identifier
    created_at = Column(DateTime, default=datetime.utcnow)
    last_message_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    site = relationship("Site", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String, primary_key=True, default=generate_uuid)
    session_id = Column(String, ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(String, nullable=False)  # user, assistant
    content = Column(Text, nullable=False)
    tokens_used = Column(Integer, default=0)
    # Quality tracking
    was_answered = Column(Boolean, default=True)
    confidence = Column(String, default="high")    # high / medium / low
    sentiment = Column(String, default="neutral")  # positive / neutral / negative
    prompt_variant_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    session = relationship("ChatSession", back_populates="messages")


class ApiKey(Base):
    __tablename__ = "api_keys"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    key_hash = Column(String, nullable=False)
    key_prefix = Column(String, nullable=False)  # First 8 chars for identification
    name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    last_used_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="api_keys")


class UsageLog(Base):
    __tablename__ = "usage_logs"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    site_id = Column(String, ForeignKey("sites.id"), nullable=False)
    action = Column(String, nullable=False)  # chat, upload, embed
    tokens_input = Column(Integer, default=0)
    tokens_output = Column(Integer, default=0)
    model_used = Column(String, nullable=True)
    cost = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)


# ─── Phase 1: Web Crawler ────────────────────────────────────────────

class CrawlJob(Base):
    __tablename__ = "crawl_jobs"

    id = Column(String, primary_key=True, default=generate_uuid)
    site_id = Column(String, ForeignKey("sites.id"), nullable=False)
    root_url = Column(String, nullable=False)
    status = Column(String, default="pending")  # pending / running / done / failed
    pages_crawled = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    site = relationship("Site")


# ─── Phase 1: Email / Lead Capture ──────────────────────────────────

class LeadCapture(Base):
    __tablename__ = "lead_captures"

    id = Column(String, primary_key=True, default=generate_uuid)
    site_id = Column(String, ForeignKey("sites.id"), nullable=False)
    session_id = Column(String, nullable=True)
    visitor_id = Column(String, nullable=False)
    email = Column(String, nullable=False)
    question = Column(Text, nullable=True)   # the question the bot couldn't answer
    created_at = Column(DateTime, default=datetime.utcnow)

    site = relationship("Site")


# ─── Phase 3: A/B Prompt Variants ───────────────────────────────────

class PromptVariant(Base):
    __tablename__ = "prompt_variants"

    id = Column(String, primary_key=True, default=generate_uuid)
    site_id = Column(String, ForeignKey("sites.id"), nullable=False)
    name = Column(String, nullable=False)
    system_prompt = Column(Text, nullable=False)
    is_control = Column(Boolean, default=False)   # the baseline variant
    is_active = Column(Boolean, default=True)
    total_chats = Column(Integer, default=0)
    answered_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    site = relationship("Site")


# ─── Phase 4: Audit Logs ────────────────────────────────────────────

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    site_id = Column(String, nullable=True)
    action = Column(String, nullable=False)   # e.g. "site.create", "document.upload"
    detail = Column(Text, nullable=True)
    ip_address = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
