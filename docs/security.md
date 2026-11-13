# Security

## Authentication & Authorization

### User Authentication (Dashboard)

- **Method:** JWT Bearer tokens
- **Hashing:** bcrypt (cost factor 12)
- **Token lifetime:** 24 hours (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`)
- **Algorithm:** HS256

```
Client → POST /auth/login → JWT Token
Client → GET /sites/ (Authorization: Bearer <jwt>) → Protected resource
```

### Widget Authentication (Public)

- **Method:** Site Key (`X-Site-Key` header)
- **Scope:** Per-site, only allows chat and config reading
- **Cannot:** Create/modify sites, upload documents, access other users' data

```
Widget → POST /chat/ (X-Site-Key: <uuid>) → Chat response
```

---

## Data Isolation

### Multi-Tenant Architecture

Every database query is scoped to the authenticated user:

```python
# Every site query includes user_id filter
site = db.query(Site).filter(
    Site.id == site_id,
    Site.user_id == current_user.id
).first()
```

**Security properties:**
- User A cannot see User B's sites, documents, or chat history
- Cross-user access returns `404 Not Found` (prevents enumeration)
- Vector store collections are isolated per-site (`site_{uuid}`)

### Verified in Tests

```
✓ User2 cannot see User1's sites
✓ User2 cannot access User1's site by ID
✓ User2 cannot upload to User1's site
✓ User2 cannot delete User1's documents
```

---

## Input Validation

### Pydantic Schemas (Request Validation)

| Field | Validation |
|-------|-----------|
| `email` | Valid email format (EmailStr) |
| `password` | 8–128 characters |
| `site_name` | 1–255 characters |
| `domain` | 1–512 characters |
| `message` | 1–4096 characters |
| `max_tokens` | 100–4096 |
| `temperature` | 0.0–2.0 |
| `visitor_id` | 1–128 characters |

### XSS Prevention

- Widget uses `textContent` (not `innerHTML`) for user messages
- Widget escapes HTML in configuration values:
  ```typescript
  private escapeHtml(text: string): string {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
  ```

### SQL Injection Prevention

- All queries use SQLAlchemy ORM parameterized queries
- No raw SQL strings
- Verified: SQL injection attempts in email field return `422`

---

## Chatbot Guardrails

The system prompt enforces strict boundaries:

1. **Context-only answers** — Never uses general knowledge
2. **Off-topic rejection** — Refuses unrelated questions
3. **Jailbreak resistance** — Redirects manipulation attempts
4. **Prompt hiding** — Never reveals system prompt or instructions
5. **No fabrication** — Explicitly states when information is unavailable

**Verified in Tests:**
```
✓ Guardrail - reject off-topic (hacking)
✓ Guardrail - reject jailbreak attempt
```

---

## Rate Limiting

Configured via `RATE_LIMIT_PER_MINUTE` (default: 60 requests/minute per IP).

---

## CORS Configuration

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins + ["*"],  # Widget from any origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

> **Production Note:** Replace `["*"]` with specific widget-hosting domains if possible. The wildcard is needed because the widget can be embedded on any customer's website.

---

## File Upload Security

| Check | Implementation |
|-------|---------------|
| File type whitelist | Only `.pdf`, `.docx`, `.txt`, `.csv`, `.png`, `.jpg`, `.jpeg` |
| File size limit | Configurable (default 50MB) |
| Filename sanitization | UUIDs used for storage paths |
| Directory traversal | Files stored in flat `uploads/` directory |

---

## Secrets Management

| Secret | Storage | Notes |
|--------|---------|-------|
| `SECRET_KEY` | `.env` file | JWT signing key |
| LLM API keys | `.env` file | Never exposed to frontend/widget |
| User passwords | Database | bcrypt hashed (never stored plaintext) |
| Site keys | Database | UUIDs, not derived from other data |

### Production Recommendations

- Use a secrets manager (AWS Secrets Manager, Azure Key Vault, HashiCorp Vault)
- Rotate `SECRET_KEY` periodically (invalidates all active JWTs)
- Rotate LLM API keys on a schedule
- Never commit `.env` to version control

---

## OWASP Top 10 Coverage

| Risk | Mitigation |
|------|-----------|
| A01: Broken Access Control | User-scoped queries, JWT validation, site-key isolation |
| A02: Cryptographic Failures | bcrypt for passwords, HS256 JWT, no plaintext secrets |
| A03: Injection | SQLAlchemy ORM (parameterized), Pydantic validation |
| A04: Insecure Design | Multi-tenant by design, principle of least privilege |
| A05: Security Misconfiguration | Environment-based config, production checklist |
| A06: Vulnerable Components | Pinned dependency versions in requirements.txt |
| A07: Auth Failures | Rate limiting, strong password requirements, token expiry |
| A08: Data Integrity | Input validation, type checking, file type whitelist |
| A09: Logging Failures | Request logging via uvicorn, usage_logs table |
| A10: SSRF | LLM API URLs are hardcoded per provider, not user-supplied |
