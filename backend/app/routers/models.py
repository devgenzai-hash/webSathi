from fastapi import APIRouter
from app.services.llm_service import AVAILABLE_MODELS

router = APIRouter(prefix="/models", tags=["Models"])


@router.get("/")
def list_available_models():
    """List all available LLM models and their pricing tiers."""
    return {"models": AVAILABLE_MODELS}


@router.get("/providers")
def list_providers():
    """List available LLM providers."""
    return {
        "providers": [
            {"id": "openai", "name": "OpenAI", "description": "GPT-4o, GPT-4o-mini"},
            {"id": "nvidia_nim", "name": "NVIDIA NIM", "description": "Fast inference for open models"},
            {"id": "openrouter", "name": "OpenRouter", "description": "Access multiple models via one API"},
            {"id": "deepseek", "name": "DeepSeek", "description": "Cost-effective AI models"},
            {"id": "ollama", "name": "Ollama", "description": "Run models locally"},
            {"id": "llamacpp", "name": "llama.cpp", "description": "Self-hosted inference"},
        ]
    }
