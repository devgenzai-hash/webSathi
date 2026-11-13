# LLM Providers

MakeWebsiteAIReady supports 6 LLM providers with 11 pre-configured models. Each site can independently choose its provider and model.

---

## Provider Architecture

All providers implement the same interface:

```python
class LLMProvider(ABC):
    async def generate(
        self,
        messages: List[dict],    # OpenAI-format messages
        max_tokens: int = 1024,
        temperature: float = 0.3,
    ) -> str:
        ...
```

The factory function routes to the correct provider:

```python
provider = get_llm_provider("nvidia_nim", "meta/llama-3.1-8b-instruct")
response = await provider.generate(messages=[...])
```

---

## Available Models

| Provider | Model ID | Display Name | Tier | Description |
|----------|----------|--------------|------|-------------|
| OpenAI | `gpt-4o-mini` | GPT-4o Mini | Starter | Fast and affordable |
| OpenAI | `gpt-4o` | GPT-4o | Pro | Most capable OpenAI model |
| NVIDIA NIM | `meta/llama-3.1-8b-instruct` | Llama 3.1 8B | Starter | Fast inference via NVIDIA NIM |
| NVIDIA NIM | `meta/llama-3.1-70b-instruct` | Llama 3.1 70B | Pro | Powerful open model |
| OpenRouter | `meta-llama/llama-3.1-8b-instruct:free` | Llama 3.1 8B (Free) | Free | Free tier via OpenRouter |
| OpenRouter | `anthropic/claude-3.5-sonnet` | Claude 3.5 Sonnet | Pro | Via OpenRouter |
| DeepSeek | `deepseek-chat` | DeepSeek Chat | Starter | Cost-effective |
| DeepSeek | `deepseek-reasoner` | DeepSeek Reasoner | Pro | Advanced reasoning |
| Ollama | `llama3.1` | Llama 3.1 (Local) | Free | Run locally |
| Ollama | `mistral` | Mistral (Local) | Free | Run locally |
| llama.cpp | `local` | Local Model | Free | Self-hosted inference |

---

## Provider Details

### OpenAI

```env
OPENAI_API_KEY=sk-...
```

- **Endpoint:** `https://api.openai.com/v1/chat/completions`
- **Timeout:** 60 seconds
- **Auth:** Bearer token

### NVIDIA NIM

```env
NVIDIA_NIM_API_KEY=nvapi-...
```

- **Endpoint:** `https://integrate.api.nvidia.com/v1/chat/completions`
- **Timeout:** 60 seconds
- **Auth:** Bearer token
- **Note:** Also used for embeddings (`/v1/embeddings` with `nvidia/nv-embedqa-e5-v5`)

### OpenRouter

```env
OPENROUTER_API_KEY=sk-or-v1-...
```

- **Endpoint:** `https://openrouter.ai/api/v1/chat/completions`
- **Timeout:** 60 seconds
- **Auth:** Bearer token + `HTTP-Referer` header
- **Note:** Provides access to models from multiple providers via one API

### DeepSeek

```env
DEEPSEEK_API_KEY=sk-...
```

- **Endpoint:** `https://api.deepseek.com/v1/chat/completions`
- **Timeout:** 60 seconds
- **Auth:** Bearer token

### Ollama (Local)

```env
OLLAMA_BASE_URL=http://localhost:11434
```

- **Endpoint:** `http://localhost:11434/api/chat`
- **Timeout:** 120 seconds (local inference can be slow)
- **Auth:** None (local network)
- **Setup:** Install Ollama, then `ollama pull llama3.1`

### llama.cpp (Self-Hosted)

- **Endpoint:** `http://localhost:8080/v1/chat/completions` (configurable)
- **Timeout:** 120 seconds
- **Auth:** None
- **Setup:** Run llama.cpp server with your GGUF model

---

## Configuring a Site's Model

Via API:

```http
PATCH /api/v1/sites/{site_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "model_provider": "nvidia_nim",
  "model_name": "meta/llama-3.1-8b-instruct",
  "temperature": 0.3,
  "max_tokens": 1024
}
```

Via Dashboard: Navigate to Site Detail → Model Configuration section.

---

## Pricing Tiers

| Tier | Models Available | Typical Cost |
|------|-----------------|--------------|
| **Free** | Ollama, llama.cpp, OpenRouter free models | $0 |
| **Starter** | GPT-4o-mini, Llama 3.1 8B, DeepSeek Chat | Low |
| **Pro** | GPT-4o, Llama 3.1 70B, Claude 3.5 Sonnet, DeepSeek Reasoner | Medium |
| **Enterprise** | All models + priority support | Custom |

---

## Adding a New Provider

1. Create a new class extending `LLMProvider` in `backend/app/services/llm_service.py`
2. Implement the `generate()` method
3. Add to `PROVIDER_MAP` dictionary
4. Add models to `AVAILABLE_MODELS` list
5. Add the API key to `.env` and `config.py`

```python
class MyProvider(LLMProvider):
    def __init__(self, api_key=None, model="my-model"):
        self.api_key = api_key or settings.MY_API_KEY
        self.model = model

    async def generate(self, messages, max_tokens=1024, temperature=0.3):
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.myprovider.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"model": self.model, "messages": messages, ...},
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]

# Add to PROVIDER_MAP
PROVIDER_MAP["my_provider"] = MyProvider
```
