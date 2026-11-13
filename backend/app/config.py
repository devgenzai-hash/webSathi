from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    # App
    APP_NAME: str = "MakeWebsiteAIReady"
    DEBUG: bool = False
    
    # Auth
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    
    # Vector DB
    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "./chroma_data")
    
    # LLM Providers
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    NVIDIA_NIM_API_KEY: Optional[str] = os.getenv("NVIDIA_NIM_API_KEY")
    OPENROUTER_API_KEY: Optional[str] = os.getenv("OPENROUTER_API_KEY")
    DEEPSEEK_API_KEY: Optional[str] = os.getenv("DEEPSEEK_API_KEY")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    # Embedding
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    
    # Upload
    MAX_UPLOAD_SIZE_MB: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "50"))
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    
    # CORS
    ALLOWED_ORIGINS: str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173")
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))

    # Debugging. Keep false in production because it prints user questions and RAG context.
    DEBUG_LLM_PAYLOADS: bool = os.getenv("DEBUG_LLM_PAYLOADS", "false").lower() == "true"

    # ── Phase 2: Billing toggle ──────────────────────────────────────
    # Set to true only when Stripe is wired up. When false, limits are not enforced.
    BILLING_ENABLED: bool = os.getenv("BILLING_ENABLED", "false").lower() == "true"

    # ── Phase 3: Integrations toggle ────────────────────────────────
    # Set to true to enable Zapier/webhook firing on lead capture.
    INTEGRATIONS_ENABLED: bool = os.getenv("INTEGRATIONS_ENABLED", "false").lower() == "true"

    # ── Phase 1: Web crawler ─────────────────────────────────────────
    CRAWLER_MAX_PAGES: int = int(os.getenv("CRAWLER_MAX_PAGES", "100"))
    CRAWLER_MAX_DEPTH: int = int(os.getenv("CRAWLER_MAX_DEPTH", "5"))

    # ── Phase 4: Language detection ──────────────────────────────────
    LANGUAGE_DETECTION_ENABLED: bool = os.getenv("LANGUAGE_DETECTION_ENABLED", "true").lower() == "true"
    
    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    class Config:
        env_file = ".env"


settings = Settings()
