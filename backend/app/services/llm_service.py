from typing import Optional, List
import httpx
from abc import ABC, abstractmethod

from app.config import settings


class LLMProvider(ABC):
    """Base class for LLM providers."""
    
    @abstractmethod
    async def generate(
        self,
        messages: List[dict],
        max_tokens: int = 1024,
        temperature: float = 0.3,
    ) -> str:
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI API provider."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model
        self.base_url = "https://api.openai.com/v1"
    
    async def generate(self, messages: List[dict], max_tokens: int = 1024, temperature: float = 0.3) -> str:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json={
                    "model": self.model,
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]


class NvidiaNIMProvider(LLMProvider):
    """NVIDIA NIM API provider."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "meta/llama-3.1-8b-instruct"):
        self.api_key = api_key or settings.NVIDIA_NIM_API_KEY
        self.model = model
        self.base_url = "https://integrate.api.nvidia.com/v1"
    
    async def generate(self, messages: List[dict], max_tokens: int = 1024, temperature: float = 0.3) -> str:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json={
                    "model": self.model,
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]


class OpenRouterProvider(LLMProvider):
    """OpenRouter API provider."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "meta-llama/llama-3.1-8b-instruct:free"):
        self.api_key = api_key or settings.OPENROUTER_API_KEY
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1"
    
    async def generate(self, messages: List[dict], max_tokens: int = 1024, temperature: float = 0.3) -> str:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://makewebsiteaiready.com",
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]


class DeepSeekProvider(LLMProvider):
    """DeepSeek API provider."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "deepseek-chat"):
        self.api_key = api_key or settings.DEEPSEEK_API_KEY
        self.model = model
        self.base_url = "https://api.deepseek.com/v1"
    
    async def generate(self, messages: List[dict], max_tokens: int = 1024, temperature: float = 0.3) -> str:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json={
                    "model": self.model,
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]


class OllamaProvider(LLMProvider):
    """Ollama local provider."""
    
    def __init__(self, base_url: Optional[str] = None, model: str = "llama3.1"):
        self.base_url = base_url or settings.OLLAMA_BASE_URL
        self.model = model
    
    async def generate(self, messages: List[dict], max_tokens: int = 1024, temperature: float = 0.3) -> str:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "num_predict": max_tokens,
                        "temperature": temperature,
                    },
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["message"]["content"]


class LlamaCppProvider(LLMProvider):
    """llama.cpp server provider (OpenAI-compatible API)."""
    
    def __init__(self, base_url: str = "http://localhost:8080", model: str = "local"):
        self.base_url = base_url
        self.model = model
    
    async def generate(self, messages: List[dict], max_tokens: int = 1024, temperature: float = 0.3) -> str:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/v1/chat/completions",
                json={
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]


# ─── Provider Factory ───────────────────────────────────────

PROVIDER_MAP = {
    "openai": OpenAIProvider,
    "nvidia_nim": NvidiaNIMProvider,
    "openrouter": OpenRouterProvider,
    "deepseek": DeepSeekProvider,
    "ollama": OllamaProvider,
    "llamacpp": LlamaCppProvider,
}

# Available models per provider
AVAILABLE_MODELS = [
    {"provider": "openai", "model_id": "gpt-4o-mini", "display_name": "GPT-4o Mini", "description": "Fast and affordable", "pricing_tier": "starter"},
    {"provider": "openai", "model_id": "gpt-4o", "display_name": "GPT-4o", "description": "Most capable OpenAI model", "pricing_tier": "pro"},
    {"provider": "nvidia_nim", "model_id": "meta/llama-3.1-8b-instruct", "display_name": "Llama 3.1 8B (NVIDIA)", "description": "Fast inference via NVIDIA NIM", "pricing_tier": "starter"},
    {"provider": "nvidia_nim", "model_id": "meta/llama-3.1-70b-instruct", "display_name": "Llama 3.1 70B (NVIDIA)", "description": "Powerful open model", "pricing_tier": "pro"},
    {"provider": "openrouter", "model_id": "meta-llama/llama-3.1-8b-instruct:free", "display_name": "Llama 3.1 8B (Free)", "description": "Free tier via OpenRouter", "pricing_tier": "free"},
    {"provider": "openrouter", "model_id": "anthropic/claude-3.5-sonnet", "display_name": "Claude 3.5 Sonnet", "description": "Via OpenRouter", "pricing_tier": "pro"},
    {"provider": "deepseek", "model_id": "deepseek-chat", "display_name": "DeepSeek Chat", "description": "Cost-effective Chinese AI", "pricing_tier": "starter"},
    {"provider": "deepseek", "model_id": "deepseek-reasoner", "display_name": "DeepSeek Reasoner", "description": "Advanced reasoning", "pricing_tier": "pro"},
    {"provider": "ollama", "model_id": "llama3.1", "display_name": "Llama 3.1 (Local)", "description": "Run locally via Ollama", "pricing_tier": "free"},
    {"provider": "ollama", "model_id": "mistral", "display_name": "Mistral (Local)", "description": "Run locally via Ollama", "pricing_tier": "free"},
    {"provider": "llamacpp", "model_id": "local", "display_name": "Local Model (llama.cpp)", "description": "Self-hosted via llama.cpp", "pricing_tier": "free"},
]


def get_llm_provider(provider_name: str, model_name: str, api_key: Optional[str] = None) -> LLMProvider:
    """Factory to get the right LLM provider instance. Pass api_key for BYOK support."""
    provider_class = PROVIDER_MAP.get(provider_name)
    if not provider_class:
        raise ValueError(f"Unknown provider: {provider_name}. Available: {list(PROVIDER_MAP.keys())}")
    if api_key:
        return provider_class(api_key=api_key, model=model_name)
    return provider_class(model=model_name)
