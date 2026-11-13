# API Reference

**Base URL:** `http://localhost:8000/api/v1`

All endpoints return JSON. Authentication is via Bearer token (JWT) for dashboard operations or `X-Site-Key` header for widget/chat operations.

---

## Authentication

### Register

```http
POST /api/v1/auth/register
Content-Type: application/json
```

**Request Body:**

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| `email` | string | Yes | Valid email format |
| `password` | string | Yes | 8–128 characters |
| `full_name` | string | No | — |

**Response** `201 Created`:

```json
{
  "access_token": "eyJhbGciOi...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "John Doe",
    "is_active": true,
    "is_verified": false,
    "plan": "free",
    "created_at": "2025-01-01T00:00:00"
  }
}
```

**Errors:**
- `409 Conflict` — Email already registered
- `422 Unprocessable Entity` — Invalid email or password too short

---

### Login

```http
POST /api/v1/auth/login
Content-Type: application/json
```

**Request Body:**

| Field | Type | Required |
|-------|------|----------|
| `email` | string (email) | Yes |
| `password` | string | Yes |

**Response** `200 OK`: Same schema as Register response.

**Errors:**
- `401 Unauthorized` — Invalid credentials

---

### Get Current User

```http
GET /api/v1/auth/me
Authorization: Bearer <token>
```

**Response** `200 OK`:

```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "is_verified": false,
  "plan": "free",
  "created_at": "2025-01-01T00:00:00"
}
```

**Errors:**
- `401 Unauthorized` — Missing or invalid token

---

## Sites

All site endpoints require `Authorization: Bearer <token>`.

### Create Site

```http
POST /api/v1/sites/
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| `site_name` | string | Yes | 1–255 chars |
| `domain` | string | Yes | 1–512 chars |

**Response** `201 Created`:

```json
{
  "id": "uuid",
  "site_name": "My Website",
  "domain": "example.com",
  "site_key": "uuid (use this for widget auth)",
  "is_verified": false,
  "is_active": true,
  "model_provider": "openai",
  "model_name": "gpt-4o-mini",
  "system_prompt": "You are a helpful assistant...",
  "max_tokens": 1024,
  "temperature": 0.3,
  "widget_position": "bottom-right",
  "widget_color": "#6366f1",
  "widget_title": "AI Assistant",
  "widget_welcome_message": "Hello! How can I help you today?",
  "created_at": "2025-01-01T00:00:00"
}
```

**Errors:**
- `401 Unauthorized` — Not authenticated
- `403 Forbidden` — Site limit reached for plan
- `422 Unprocessable Entity` — Empty site name

**Plan Limits:**

| Plan | Max Sites |
|------|-----------|
| Free | 2 |
| Starter | 5 |
| Pro | 20 |
| Enterprise | 100 |

---

### List Sites

```http
GET /api/v1/sites/
Authorization: Bearer <token>
```

**Response** `200 OK`: Array of site objects (same schema as create response).

---

### Get Site

```http
GET /api/v1/sites/{site_id}
Authorization: Bearer <token>
```

**Response** `200 OK`: Single site object.

**Errors:**
- `404 Not Found` — Site doesn't exist or belongs to another user

---

### Update Site

```http
PATCH /api/v1/sites/{site_id}
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body** (all fields optional):

| Field | Type | Constraints |
|-------|------|-------------|
| `site_name` | string | — |
| `model_provider` | string | One of: `openai`, `nvidia_nim`, `openrouter`, `deepseek`, `ollama`, `llamacpp` |
| `model_name` | string | Valid model ID for the provider |
| `system_prompt` | string | Custom instructions for the chatbot |
| `max_tokens` | integer | 100–4096 |
| `temperature` | float | 0.0–2.0 |
| `widget_position` | string | `bottom-right`, `bottom-left`, `top-right`, `top-left` |
| `widget_color` | string | Hex color (e.g., `#6366f1`) |
| `widget_title` | string | Displayed in widget header |
| `widget_welcome_message` | string | First message shown to visitors |

**Response** `200 OK`: Updated site object.

---

### Delete Site

```http
DELETE /api/v1/sites/{site_id}
Authorization: Bearer <token>
```

**Response** `204 No Content`

---

### Verify Site

```http
POST /api/v1/sites/{site_id}/verify
Authorization: Bearer <token>
```

**Response** `200 OK`:

```json
{
  "message": "Site verified successfully",
  "site_key": "uuid"
}
```

> **Note:** In the MVP, verification is immediate. Production would verify DNS TXT records or meta tags.

---

## Documents

All document endpoints require `Authorization: Bearer <token>`.

### Upload Document

```http
POST /api/v1/sites/{site_id}/documents/
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Form Data:**

| Field | Type | Constraints |
|-------|------|-------------|
| `file` | file | Max 50MB. Supported: `.pdf`, `.docx`, `.txt`, `.csv`, `.png`, `.jpg`, `.jpeg` |

**Response** `201 Created`:

```json
{
  "id": "uuid",
  "site_id": "uuid",
  "filename": "product-guide.pdf",
  "file_type": "pdf",
  "file_size": 245760,
  "chunk_count": 24,
  "status": "ready",
  "error_message": null,
  "created_at": "2025-01-01T00:00:00"
}
```

**Processing Pipeline:**
1. File is saved to disk
2. Text is extracted (PDF → PyPDF2, DOCX → python-docx, Images → Tesseract OCR)
3. Text is chunked (1000 chars, 200 overlap via `RecursiveCharacterTextSplitter`)
4. Chunks are embedded (NVIDIA NIM API or fallback hash-based embeddings)
5. Embeddings are stored in ChromaDB (collection: `site_{site_id}`)

**Errors:**
- `400 Bad Request` — Unsupported file type
- `404 Not Found` — Site not found or belongs to another user

---

### List Documents

```http
GET /api/v1/sites/{site_id}/documents/
Authorization: Bearer <token>
```

**Response** `200 OK`: Array of document objects.

---

### Delete Document

```http
DELETE /api/v1/sites/{site_id}/documents/{document_id}
Authorization: Bearer <token>
```

**Response** `204 No Content`

Deletes the document record, the file from disk, and its embeddings from ChromaDB.

---

## Chat (Widget/Public)

Chat endpoints use **site-key authentication** (not user JWT). The site key is passed in the `X-Site-Key` header.

### Send Message

```http
POST /api/v1/chat/
X-Site-Key: <site-key>
Content-Type: application/json
```

**Request Body:**

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| `message` | string | Yes | 1–4096 chars |
| `visitor_id` | string | Yes | 1–128 chars (anonymous identifier) |
| `session_id` | string | No | Pass to continue existing conversation |

**Response** `200 OK`:

```json
{
  "response": "Based on the documentation, the return policy allows...",
  "session_id": "uuid",
  "sources": ["product-guide.pdf"]
}
```

**Processing Pipeline:**
1. Retrieve relevant chunks from ChromaDB (top 8)
2. Rerank chunks for relevance (top 4)
3. Build context + guardrail system prompt
4. Include last 6 messages for conversation continuity
5. Call configured LLM provider
6. Return response with session ID for follow-ups

**Errors:**
- `401 Unauthorized` — Missing or invalid site key
- `422 Unprocessable Entity` — Empty or too-long message

---

### Get Widget Config

```http
GET /api/v1/chat/config
X-Site-Key: <site-key>
```

**Response** `200 OK`:

```json
{
  "widget_position": "bottom-right",
  "widget_color": "#6366f1",
  "widget_title": "AI Assistant",
  "widget_welcome_message": "Hello! How can I help you today?"
}
```

---

## Models

Public endpoints (no authentication required).

### List Models

```http
GET /api/v1/models/
```

**Response** `200 OK`:

```json
{
  "models": [
    {
      "provider": "openai",
      "model_id": "gpt-4o-mini",
      "display_name": "GPT-4o Mini",
      "description": "Fast and affordable",
      "pricing_tier": "starter"
    },
    {
      "provider": "nvidia_nim",
      "model_id": "meta/llama-3.1-8b-instruct",
      "display_name": "Llama 3.1 8B (NVIDIA)",
      "description": "Fast inference via NVIDIA NIM",
      "pricing_tier": "starter"
    }
    // ... 11 total models
  ]
}
```

### List Providers

```http
GET /api/v1/models/providers
```

**Response** `200 OK`:

```json
{
  "providers": [
    {"id": "openai", "name": "OpenAI", "description": "GPT-4o, GPT-4o-mini"},
    {"id": "nvidia_nim", "name": "NVIDIA NIM", "description": "Fast inference for open models"},
    {"id": "openrouter", "name": "OpenRouter", "description": "Access multiple models via one API"},
    {"id": "deepseek", "name": "DeepSeek", "description": "Cost-effective AI models"},
    {"id": "ollama", "name": "Ollama", "description": "Run models locally"},
    {"id": "llamacpp", "name": "llama.cpp", "description": "Self-hosted inference"}
  ]
}
```

---

## Health Check

```http
GET /health
```

**Response:** `{"status": "healthy"}`

---

## Error Response Format

All errors follow this structure:

```json
{
  "detail": "Human-readable error message"
}
```

| Status Code | Meaning |
|-------------|---------|
| 400 | Bad Request (invalid input) |
| 401 | Unauthorized (missing/invalid credentials) |
| 403 | Forbidden (authenticated but not allowed) |
| 404 | Not Found (resource doesn't exist or access denied) |
| 409 | Conflict (duplicate resource) |
| 422 | Unprocessable Entity (validation failed) |
| 500 | Internal Server Error |
