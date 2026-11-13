import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import init_db
from app.routers import auth, sites, documents, chat, models
from app.routers import crawl, conversations, leads, audit, variants


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize resources on startup."""
    # Create upload directory
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    # Initialize database tables
    init_db()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description="AI Chatbot-as-a-Service Platform API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS - allow widget and frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins + ["*"],  # Widget can come from any origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Register routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(sites.router, prefix="/api/v1")
app.include_router(documents.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(models.router, prefix="/api/v1")
# Phase 1
app.include_router(crawl.router, prefix="/api/v1")
app.include_router(conversations.router, prefix="/api/v1")
app.include_router(leads.router, prefix="/api/v1")
# Phase 3
app.include_router(variants.router, prefix="/api/v1")
# Phase 4
app.include_router(audit.router, prefix="/api/v1")


@app.get("/")
def root():
    return {"name": settings.APP_NAME, "version": "1.0.0", "status": "running"}


@app.get("/health")
def health():
    return {"status": "ok", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
