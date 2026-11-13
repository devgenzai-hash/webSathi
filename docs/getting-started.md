# Getting Started

## Prerequisites

- **Python 3.11+** (3.12 or 3.14 also supported)
- **Node.js 18+** (for frontend and widget builds)
- **Git**
- At least one LLM API key (NVIDIA NIM, OpenAI, OpenRouter, or DeepSeek) — or Ollama for local models

---

## Quick Start (Development)

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/makeWebsiteAIReady.git
cd makeWebsiteAIReady
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\Activate.ps1

# Activate (Linux/macOS)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your keys
```

**Minimum required configuration:**

```env
SECRET_KEY=<generate-a-random-64-char-string>
DATABASE_URL=sqlite:///./app.db
NVIDIA_NIM_API_KEY=nvapi-your-key-here
```

### 4. Start the Backend

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`.  
Interactive docs at `http://localhost:8000/docs`.

### 5. Frontend Setup (Optional)

```bash
cd ../frontend
npm install
npm run dev
```

Dashboard available at `http://localhost:5173`.

### 6. Widget Build (Optional)

```bash
cd ../widget
npm install
npm run build
```

Output: `dist/chatbot-widget.js`

---

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | Yes | — | JWT signing secret (change in production!) |
| `ALGORITHM` | No | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `1440` | Token expiry (24 hours) |
| `DATABASE_URL` | No | `sqlite:///./app.db` | Database connection string |
| `CHROMA_PERSIST_DIR` | No | `./chroma_data` | ChromaDB storage directory |
| `OPENAI_API_KEY` | No | — | OpenAI API key |
| `NVIDIA_NIM_API_KEY` | No | — | NVIDIA NIM API key |
| `OPENROUTER_API_KEY` | No | — | OpenRouter API key |
| `DEEPSEEK_API_KEY` | No | — | DeepSeek API key |
| `OLLAMA_BASE_URL` | No | `http://localhost:11434` | Ollama server URL |
| `MAX_UPLOAD_SIZE_MB` | No | `50` | Max document upload size |
| `UPLOAD_DIR` | No | `./uploads` | File storage directory |
| `ALLOWED_ORIGINS` | No | `http://localhost:3000,http://localhost:5173` | CORS origins |
| `RATE_LIMIT_PER_MINUTE` | No | `60` | API rate limit |

---

## Docker Quick Start

```bash
# From project root
docker-compose up -d
```

This starts:
- Backend API on port `8000`
- Frontend dashboard on port `5173`

---

## Verifying Installation

```bash
# Check backend health
curl http://localhost:8000/health
# → {"status": "healthy"}

# Check API root
curl http://localhost:8000/
# → {"name": "MakeWebsiteAIReady", "version": "1.0.0", "status": "running"}
```

---

## First Steps After Setup

1. **Register** — `POST /api/v1/auth/register` with email and password
2. **Create a site** — `POST /api/v1/sites/` with your website name and domain
3. **Upload documents** — `POST /api/v1/sites/{id}/documents/` with PDF/TXT/DOCX files
4. **Get your site key** — from the site response or dashboard
5. **Embed the widget** — add the `<script>` tag to your website (see [Widget Integration](./widget-integration.md))
