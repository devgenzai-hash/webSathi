# Database Schema

The application uses SQLAlchemy ORM with SQLite (development) or PostgreSQL (production).

---

## Entity Relationship Diagram

```mermaid
erDiagram
    User ||--o{ Site : owns
    User ||--o{ ApiKey : has
    Site ||--o{ Document : contains
    Site ||--o{ ChatSession : has
    ChatSession ||--o{ ChatMessage : contains
    Site ||--o{ UsageLog : tracks

    User {
        string id PK
        string email UK
        string hashed_password
        string full_name
        boolean is_active
        boolean is_verified
        string plan
        datetime created_at
        datetime updated_at
    }

    Site {
        string id PK
        string user_id FK
        string site_name
        string domain
        string site_key UK
        boolean is_verified
        boolean is_active
        string model_provider
        string model_name
        text system_prompt
        integer max_tokens
        float temperature
        string widget_position
        string widget_color
        string widget_title
        string widget_welcome_message
        datetime created_at
        datetime updated_at
    }

    Document {
        string id PK
        string site_id FK
        string filename
        string file_type
        integer file_size
        string file_path
        integer chunk_count
        string status
        text error_message
        datetime created_at
    }

    ChatSession {
        string id PK
        string site_id FK
        string visitor_id
        datetime created_at
        datetime last_message_at
    }

    ChatMessage {
        string id PK
        string session_id FK
        string role
        text content
        integer tokens_used
        datetime created_at
    }

    ApiKey {
        string id PK
        string user_id FK
        string key_hash
        string key_prefix
        string name
        boolean is_active
        datetime last_used_at
        datetime created_at
    }

    UsageLog {
        string id PK
        string user_id FK
        string site_id FK
        string action
        integer tokens_input
        integer tokens_output
        string model_used
        float cost
        datetime created_at
    }
```

---

## Tables Detail

### `users`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | VARCHAR | PK, UUID | Unique user identifier |
| `email` | VARCHAR | UNIQUE, NOT NULL, INDEXED | Login email |
| `hashed_password` | VARCHAR | NOT NULL | bcrypt hash |
| `full_name` | VARCHAR | NULLABLE | Display name |
| `is_active` | BOOLEAN | DEFAULT true | Account active status |
| `is_verified` | BOOLEAN | DEFAULT false | Email verified |
| `plan` | VARCHAR | DEFAULT "free" | `free`, `starter`, `pro`, `enterprise` |
| `created_at` | DATETIME | DEFAULT now() | — |
| `updated_at` | DATETIME | DEFAULT now() | Auto-updated |

### `sites`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | VARCHAR | PK, UUID | Site identifier |
| `user_id` | VARCHAR | FK → users.id | Owner |
| `site_name` | VARCHAR | NOT NULL | Display name |
| `domain` | VARCHAR | NOT NULL | Website domain |
| `site_key` | VARCHAR | UNIQUE, NOT NULL, UUID | Widget authentication key |
| `is_verified` | BOOLEAN | DEFAULT false | Domain ownership verified |
| `is_active` | BOOLEAN | DEFAULT true | Site enabled |
| `model_provider` | VARCHAR | DEFAULT "openai" | LLM provider ID |
| `model_name` | VARCHAR | DEFAULT "gpt-4o-mini" | Model identifier |
| `system_prompt` | TEXT | Has default | Custom chatbot instructions |
| `max_tokens` | INTEGER | DEFAULT 1024 | Max response tokens |
| `temperature` | FLOAT | DEFAULT 0.3 | LLM temperature |
| `widget_position` | VARCHAR | DEFAULT "bottom-right" | Widget placement |
| `widget_color` | VARCHAR | DEFAULT "#6366f1" | Brand color |
| `widget_title` | VARCHAR | DEFAULT "AI Assistant" | Widget header |
| `widget_welcome_message` | VARCHAR | Has default | Greeting message |
| `created_at` | DATETIME | DEFAULT now() | — |
| `updated_at` | DATETIME | DEFAULT now() | — |

### `documents`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | VARCHAR | PK, UUID | Document identifier |
| `site_id` | VARCHAR | FK → sites.id | Parent site |
| `filename` | VARCHAR | NOT NULL | Original filename |
| `file_type` | VARCHAR | NOT NULL | `pdf`, `docx`, `txt`, `csv`, `image` |
| `file_size` | INTEGER | NOT NULL | Size in bytes |
| `file_path` | VARCHAR | NOT NULL | Storage path on disk |
| `chunk_count` | INTEGER | DEFAULT 0 | Number of text chunks created |
| `status` | VARCHAR | DEFAULT "processing" | `processing`, `ready`, `failed` |
| `error_message` | TEXT | NULLABLE | Error details if failed |
| `created_at` | DATETIME | DEFAULT now() | — |

### `chat_sessions`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | VARCHAR | PK, UUID | Session identifier |
| `site_id` | VARCHAR | FK → sites.id | Parent site |
| `visitor_id` | VARCHAR | NOT NULL | Anonymous visitor identifier |
| `created_at` | DATETIME | DEFAULT now() | — |
| `last_message_at` | DATETIME | DEFAULT now() | Last activity |

### `chat_messages`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | VARCHAR | PK, UUID | Message identifier |
| `session_id` | VARCHAR | FK → chat_sessions.id | Parent session |
| `role` | VARCHAR | NOT NULL | `user` or `assistant` |
| `content` | TEXT | NOT NULL | Message text |
| `tokens_used` | INTEGER | DEFAULT 0 | Tokens consumed |
| `created_at` | DATETIME | DEFAULT now() | — |

### `api_keys`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | VARCHAR | PK, UUID | Key identifier |
| `user_id` | VARCHAR | FK → users.id | Owner |
| `key_hash` | VARCHAR | NOT NULL | Hashed API key |
| `key_prefix` | VARCHAR | NOT NULL | First 8 chars for display |
| `name` | VARCHAR | NOT NULL | User-assigned label |
| `is_active` | BOOLEAN | DEFAULT true | Key enabled |
| `last_used_at` | DATETIME | NULLABLE | Last usage timestamp |
| `created_at` | DATETIME | DEFAULT now() | — |

### `usage_logs`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | VARCHAR | PK, UUID | Log entry identifier |
| `user_id` | VARCHAR | FK → users.id | User |
| `site_id` | VARCHAR | FK → sites.id | Site |
| `action` | VARCHAR | NOT NULL | `chat`, `upload`, `embed` |
| `tokens_input` | INTEGER | DEFAULT 0 | Input tokens |
| `tokens_output` | INTEGER | DEFAULT 0 | Output tokens |
| `model_used` | VARCHAR | NULLABLE | Model identifier |
| `cost` | FLOAT | DEFAULT 0.0 | Estimated cost |
| `created_at` | DATETIME | DEFAULT now() | — |

---

## Cascade Deletions

- Deleting a **User** → deletes all their Sites, ApiKeys
- Deleting a **Site** → deletes all its Documents, ChatSessions
- Deleting a **ChatSession** → deletes all its ChatMessages

---

## Data Isolation

Each query is scoped to the authenticated user:

```python
# Users can only see their own sites
site = db.query(Site).filter(
    Site.id == site_id,
    Site.user_id == current_user.id  # Always filtered by owner
).first()
```

Cross-user access returns `404 Not Found` (not `403`) to avoid information leakage.

---

## Switching to PostgreSQL

Update `DATABASE_URL` in `.env`:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/makewebsiteaiready
```

Install the driver:

```bash
pip install psycopg2-binary
```

The ORM models are fully compatible with PostgreSQL without code changes.
