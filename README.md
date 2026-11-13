








cd C:\Users\aranjan\Documents\Projects\makeWebsiteAIready\backend; .\venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload


cd C:\Users\aranjan\Documents\Projects\makeWebsiteAIready\frontend; npm run dev


cd C:\Users\aranjan\Documents\Projects\makeWebsiteAIready; python -m http.server 3000


cd C:\Users\aranjan\Documents\Projects\makeWebsiteAIready\widget; npm run build


get the data 
cd C:\Users\aranjan\Documents\Projects\makeWebsiteAIready\backend
.\venv\Scripts\python.exe _dbdump.py





# MakeWebsiteAIReady

MakeWebsiteAIReady lets a website owner add an AI chatbot to their website with one script tag.

The chatbot answers using only the files uploaded by that website owner. Each website has its own site key, database rows, vector collection, chat sessions, and uploaded files.

## Very Short Local URLs

When everything is running locally:

| What | URL |
| --- | --- |
| Backend API | http://localhost:8000 |
| API docs | http://localhost:8000/docs |
| Dashboard | http://localhost:5173 |
| Test website with widget | http://localhost:3000/examples/simple-website.html |

## Simple Flow

1. User registers or logs in on the dashboard.
2. User registers a website domain, for example `example.com` or local `localhost:3000`.
3. User sets the widget title, welcome message, color, position, model, and prompt.
4. User uploads files like CSV, PDF, images, text, and DOCX.
5. Backend extracts text from those files.
6. Backend splits the text into chunks.
7. Backend creates embeddings for those chunks.
8. Backend stores those chunks and embeddings in ChromaDB.
9. User copies the embed code from the dashboard.
10. User adds the script tag to their website.
11. Widget appears on the website.
12. Visitor asks a question.
13. Backend checks the site key and domain.
14. Backend searches the correct website's vector database.
15. Backend sends the best matching context to the selected LLM.
16. Visitor receives the answer.
17. Chat history stays in the same browser and domain.

Important: if the site is registered as `example.com`, the widget also works on `example.com/products` or `example.com/about`. It does not work on a different domain.

## Folders

| Folder | Meaning |
| --- | --- |
| `backend` | FastAPI API, database, document parsing, RAG, LLM calls |
| `frontend` | React dashboard where users manage sites and documents |
| `widget` | Small embeddable chatbot script |
| `examples` | Local HTML pages for testing the widget |
| `backend/uploads` | Uploaded files are stored here locally |
| `backend/chroma_data` | ChromaDB vector data is stored here locally |
| `backend/app.db` | SQLite database is stored here locally |

## One-Time Setup

Run these from the project root.

### 1. Backend setup

```powershell
py -3.14 -m venv backend\venv
Push-Location backend
.\venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env -ErrorAction SilentlyContinue
Pop-Location
```

If `py -3.14` does not work, use your installed Python:

```powershell
python -m venv backend\venv
```

### 2. Frontend setup

```powershell
Push-Location frontend
npm install
Pop-Location
```

### 3. Widget setup

```powershell
Push-Location widget
npm install
npm run build
Pop-Location
```

The widget build output is:

```text
widget/dist/chatbot-widget.js
```

## Run Everything Locally

Open 4 terminals, or run each command in its own terminal.

### Terminal 1: Backend API

Use this command from the project root. It sets absolute paths so the backend always uses `backend/app.db` and `backend/chroma_data`.

```powershell
$PROJECT = (Get-Location).Path
$env:DATABASE_URL = "sqlite:///$($PROJECT.Replace('\', '/'))/backend/app.db"
$env:CHROMA_PERSIST_DIR = "$($PROJECT.Replace('\', '/'))/backend/chroma_data"
& "$PROJECT\backend\venv\Scripts\python.exe" -m uvicorn app.main:app --app-dir "$PROJECT\backend" --host 0.0.0.0 --port 8000
```

Open:

```text
http://localhost:8000/docs
```

### Terminal 2: Dashboard

```powershell
Push-Location frontend
npm run dev
```

Open:

```text
http://localhost:5173
```

### Terminal 3: Widget Build Watch or Manual Build

For normal use, build once:

```powershell
Push-Location widget
npm run build
Pop-Location
```

If you edit widget code and want automatic rebuilds:

```powershell
Push-Location widget
npm run dev
```

### Terminal 4: Local HTML Test Website

This serves the root folder so the HTML page can load `widget/dist/chatbot-widget.js`.

```powershell
python -m http.server 3000 --directory .
```

Open:

```text
http://localhost:3000/examples/simple-website.html
```

## What I Have Running Locally Now

These are running in this workspace right now:

| Service | Status |
| --- | --- |
| Backend | running on `http://localhost:8000` |
| Dashboard | running on `http://localhost:5173` |
| Static HTML test site | running on `http://localhost:3000` |
| Widget | built at `widget/dist/chatbot-widget.js` |

## Testing Version

Use this page for local testing:

```text
http://localhost:3000/examples/simple-website.html
```

That page has this kind of script tag:

```html
<script
  src="../widget/dist/chatbot-widget.js"
  data-site-key="YOUR_SITE_KEY"
  data-api-url="http://localhost:8000"
  data-position="bottom-right"
  data-color="#6366f1"
  data-title="Ask AI"
  data-welcome-message="Hi! Ask me anything about this website's docs."
></script>>
```

For local testing, the site in the dashboard must be registered as:

```text
localhost:3000
```

If the domain does not match, the backend will reject the widget request.

## Normal Local Test Steps

1. Start backend on `8000`.
2. Start dashboard on `5173`.
3. Start static server on `3000`.
4. Open `http://localhost:5173`.
5. Register or log in.
6. Create a site.
7. Use domain `localhost:3000` for the local HTML test page.
8. Upload a file, for example CSV, PDF, TXT, DOCX, PNG, JPG, or WebP.
9. Wait until document status is `ready`.
10. Open the embed tab and copy the site key.
11. Put the site key into `examples/simple-website.html` or use the dashboard embed code.
12. Open `http://localhost:3000/examples/simple-website.html`.
13. Click the chat bubble.
14. Ask a question about your uploaded file.

## Build Commands

### Backend syntax check

```powershell
Push-Location backend
.\venv\Scripts\python.exe -m compileall app
Pop-Location
```

### Frontend production build

```powershell
Push-Location frontend
npm run build
Pop-Location
```

### Widget production build

```powershell
Push-Location widget
npm run build
Pop-Location
```

## Run Backend Test Script

The test script talks to a running backend.

Start backend first, then run:

```powershell
Push-Location backend
.\venv\Scripts\python.exe tests\test_all.py
Pop-Location
```

Warning: the test script creates users/sites/docs in the current database. Use a separate test database if you do not want to touch your local data.

Example with a temporary test DB:

```powershell
$PROJECT = (Get-Location).Path
$env:DATABASE_URL = "sqlite:///$($PROJECT.Replace('\', '/'))/backend/test.db"
$env:CHROMA_PERSIST_DIR = "$($PROJECT.Replace('\', '/'))/backend/test_chroma_data"
& "$PROJECT\backend\venv\Scripts\python.exe" -m uvicorn app.main:app --app-dir "$PROJECT\backend" --host 0.0.0.0 --port 8000
```

## Where Data Is Stored Locally

| Data | Location |
| --- | --- |
| Users, sites, documents, chat sessions | `backend/app.db` |
| Uploaded original files | `backend/uploads` |
| Vector embeddings and chunks | `backend/chroma_data` |
| Widget browser chat history | browser `localStorage` |

The widget stores browser history with keys starting with:

```text
mwair:
```

The key includes the site key and domain, so history stays on the same domain but not across different client websites.

## How To See The SQLite Database

Use these commands from the project root.

### List tables

```powershell
Push-Location backend
.\venv\Scripts\python.exe -c "import sqlite3; db=sqlite3.connect('app.db'); print(db.execute(\"select name from sqlite_master where type='table'\").fetchall())"
Pop-Location
```

Important tables:

| Table | Meaning |
| --- | --- |
| `users` | Dashboard users |
| `sites` | Websites registered by users |
| `documents` | Uploaded files and processing status |
| `chat_sessions` | One chat session per visitor/site |
| `chat_messages` | User and assistant messages |
| `usage_logs` | Usage tracking |
| `api_keys` | API keys if used |

### See users

```powershell
Push-Location backend
.\venv\Scripts\python.exe -c "import sqlite3; db=sqlite3.connect('app.db'); [print(row) for row in db.execute('select id,email,plan,created_at from users')]"
Pop-Location
```

### See sites and site keys

```powershell
Push-Location backend
.\venv\Scripts\python.exe -c "import sqlite3; db=sqlite3.connect('app.db'); [print(row) for row in db.execute('select id,site_name,domain,site_key,is_active from sites')]"
Pop-Location
```

### See uploaded documents

```powershell
Push-Location backend
.\venv\Scripts\python.exe -c "import sqlite3; db=sqlite3.connect('app.db'); [print(row) for row in db.execute('select id,site_id,filename,file_type,status,chunk_count,error_message from documents')]"
Pop-Location
```

### See chat history

```powershell
Push-Location backend
.\venv\Scripts\python.exe -c "import sqlite3; db=sqlite3.connect('app.db'); [print(row) for row in db.execute('select id,site_id,visitor_id,created_at,last_message_at from chat_sessions')]"
.\venv\Scripts\python.exe -c "import sqlite3; db=sqlite3.connect('app.db'); [print(row) for row in db.execute('select session_id,role,content,created_at from chat_messages order by created_at desc limit 20')]"
Pop-Location
```

### See table columns

Replace `documents` with any table name.

```powershell
Push-Location backend
.\venv\Scripts\python.exe -c "import sqlite3; db=sqlite3.connect('app.db'); [print(row) for row in db.execute('pragma table_info(documents)')]"
Pop-Location
```

## How To See Vector DB Data And Embeddings

ChromaDB data is in:

```text
backend/chroma_data
```

Each site gets its own Chroma collection. That keeps customer data separate.

First get a `site_id` from the `sites` table:

```powershell
Push-Location backend
.\venv\Scripts\python.exe -c "import sqlite3; db=sqlite3.connect('app.db'); [print(row) for row in db.execute('select id,site_name,domain from sites')]"
Pop-Location
```

Then inspect that site's vector collection. Replace `PASTE_SITE_ID_HERE`.

```powershell
Push-Location backend
.\venv\Scripts\python.exe -c "from app.services.rag_service import get_collection_for_site; site_id='PASTE_SITE_ID_HERE'; c=get_collection_for_site(site_id); print('chunks:', c.count()); print(c.peek(3))"
Pop-Location
```

What you will see:

| Field | Meaning |
| --- | --- |
| `ids` | Chroma chunk IDs |
| `documents` | Text chunks extracted from uploaded files |
| `metadatas` | Site ID, document ID, chunk number |
| `embeddings` | Number vectors used for search |

## How Embeddings Are Created

The code is in:

```text
backend/app/services/rag_service.py
```

Simple flow:

1. User uploads a file.
2. `document_service.py` saves the file.
3. `rag_service.py` extracts text.
4. Text is split into chunks.
5. Each chunk gets an embedding vector.
6. Chunks and embeddings are saved in ChromaDB.

Supported file types:

| Type | Notes |
| --- | --- |
| PDF | Text extraction with PyPDF2 |
| DOCX | Text extraction with python-docx |
| TXT | Plain text |
| CSV | Treated as text |
| PNG/JPG/WebP | OCR with pytesseract if installed |

Embedding provider behavior:

| If this is set | Embedding model used |
| --- | --- |
| `NVIDIA_NIM_API_KEY` | `nvidia/nv-embedqa-e5-v5` |
| otherwise `OPENAI_API_KEY` | `text-embedding-3-small` |
| no embedding key | local fallback embedding for testing |

The fallback embedding is useful for local testing. For production, use a real embedding API.

## How To Change The LLM

You can change the LLM from the dashboard:

1. Open `http://localhost:5173`.
2. Log in.
3. Open a site.
4. Go to Settings.
5. Choose model/provider.
6. Save by leaving the field or selecting an option.

Supported providers are in:

```text
backend/app/services/llm_service.py
```

Current providers:

| Provider value | Example model |
| --- | --- |
| `openai` | `gpt-4o-mini` |
| `nvidia_nim` | `meta/llama-3.1-8b-instruct` |
| `openrouter` | `meta-llama/llama-3.1-8b-instruct:free` |
| `deepseek` | `deepseek-chat` |
| `ollama` | `llama3.1` |
| `llamacpp` | `local` |

Add keys in `backend/.env`:

```env
OPENAI_API_KEY=your_key_here
NVIDIA_NIM_API_KEY=your_key_here
OPENROUTER_API_KEY=your_key_here
DEEPSEEK_API_KEY=your_key_here
OLLAMA_BASE_URL=http://localhost:11434
```

Restart the backend after changing `.env`.

## How To Debug What Goes To The LLM

Set this in `backend/.env`:

```env
DEBUG_LLM_PAYLOADS=true
```

Restart backend.

Then ask a question in the widget. The backend terminal will print:

- site ID
- provider
- model
- system prompt
- RAG context chunks
- user message
- recent chat history
- max tokens
- temperature

Turn it off when done:

```env
DEBUG_LLM_PAYLOADS=false
```

Do not use `DEBUG_LLM_PAYLOADS=true` in production. It prints user data and uploaded document context.

## How To Debug RAG Search

### Check if document processed

```powershell
Push-Location backend
.\venv\Scripts\python.exe -c "import sqlite3; db=sqlite3.connect('app.db'); [print(row) for row in db.execute('select filename,status,chunk_count,error_message from documents')]"
Pop-Location
```

Good result:

```text
status = ready
chunk_count > 0
```

Bad result:

```text
status = failed
error_message has the reason
```

### Check if chunks exist in Chroma

```powershell
Push-Location backend
.\venv\Scripts\python.exe -c "from app.services.rag_service import get_collection_for_site; site_id='PASTE_SITE_ID_HERE'; c=get_collection_for_site(site_id); print(c.count()); print(c.peek(1))"
Pop-Location
```

If count is `0`, no searchable chunks exist for that site.

## How To Debug Widget Problems

### Widget does not show

Check these:

1. Did you build the widget?

```powershell
Push-Location widget
npm run build
Pop-Location
```

2. Is the script URL correct?

Local:

```html
<script src="../widget/dist/chatbot-widget.js" data-site-key="YOUR_SITE_KEY" data-api-url="http://localhost:8000"></script>
```

Production:

```html
<script src="https://your-cdn.com/chatbot-widget.js" data-site-key="YOUR_SITE_KEY"></script>
```

3. Is the site registered with the same domain where the widget loads?

For local HTML testing, use:

```text
localhost:3000
```

### Widget says invalid site key

Your `data-site-key` is wrong, or the backend is using the wrong database.

Make sure backend was started with this style of command:

```powershell
$PROJECT = (Get-Location).Path
$env:DATABASE_URL = "sqlite:///$($PROJECT.Replace('\', '/'))/backend/app.db"
$env:CHROMA_PERSIST_DIR = "$($PROJECT.Replace('\', '/'))/backend/chroma_data"
& "$PROJECT\backend\venv\Scripts\python.exe" -m uvicorn app.main:app --app-dir "$PROJECT\backend" --host 0.0.0.0 --port 8000
```

### Widget says domain not authorized

The site key is valid, but the domain does not match.

Example:

| Registered domain | Widget page | Works? |
| --- | --- | --- |
| `localhost:3000` | `http://localhost:3000/examples/simple-website.html` | yes |
| `localhost:3000` | `http://localhost:5173` | no |
| `example.com` | `https://example.com/pricing` | yes |
| `example.com` | `https://other.com` | no |

### Widget chat history vanished

History is per browser, per site key, per domain. It is stored in browser localStorage.

If you open another browser, another device, incognito mode, or clear site data, history starts new.

### Chat says it has no information

Check:

1. Did you upload documents?
2. Is document status `ready`?
3. Is `chunk_count` more than `0`?
4. Is the question related to the uploaded docs?
5. Did the site key point to the same site that owns those docs?

## How To Stop Servers

Find the process:

```powershell
netstat -ano | findstr ":8000"
netstat -ano | findstr ":5173"
netstat -ano | findstr ":3000"
```

Stop by PID:

```powershell
Stop-Process -Id PASTE_PID_HERE -Force
```

## Deployment In Simple Words

In production you need these pieces:

1. Backend API server, for example `https://api.yourdomain.com`.
2. Database, preferably PostgreSQL instead of local SQLite.
3. Persistent ChromaDB storage or a hosted vector DB.
4. Persistent upload storage, for example S3, Azure Blob, or mounted disk.
5. Frontend dashboard, for example `https://app.yourdomain.com`.
6. Widget JS file hosted on CDN, for example `https://cdn.yourdomain.com/chatbot-widget.js`.
7. Real LLM and embedding API keys.
8. HTTPS everywhere.

### Production backend env example

```env
SECRET_KEY=use-a-long-random-secret
DATABASE_URL=postgresql://user:password@host:5432/makewebsiteaiready
CHROMA_PERSIST_DIR=/data/chroma_data
UPLOAD_DIR=/data/uploads
ALLOWED_ORIGINS=https://app.yourdomain.com,https://yourdomain.com
OPENAI_API_KEY=your_key
NVIDIA_NIM_API_KEY=your_key
OPENROUTER_API_KEY=your_key
DEEPSEEK_API_KEY=your_key
DEBUG_LLM_PAYLOADS=false
```

### Production frontend build

Set these before building the dashboard if you want generated embed code to use your real CDN/API URLs:

```env
VITE_WIDGET_URL=https://cdn.yourdomain.com/chatbot-widget.js
VITE_WIDGET_API_URL=https://api.yourdomain.com
```

Then build:

```powershell
Push-Location frontend
npm run build
Pop-Location
```

Upload `frontend/dist` to your frontend host.

### Production widget build

```powershell
Push-Location widget
npm run build
Pop-Location
```

Upload this file to your CDN:

```text
widget/dist/chatbot-widget.js
```

Production embed code looks like:

```html
<script
  src="https://cdn.yourdomain.com/chatbot-widget.js"
  data-site-key="SITE_KEY_FROM_DASHBOARD"
></script>
```

The widget will call your production API if the dashboard generated `data-api-url`, or if the widget default API URL is changed before publishing.

## Production Request Flow

1. Visitor opens client's website.
2. Website loads CDN widget JS.
3. Widget sends `X-Site-Key` and current page/domain to backend.
4. Backend checks site key.
5. Backend checks registered domain.
6. Backend finds this site's Chroma collection.
7. Backend retrieves relevant chunks.
8. Backend adds recent chat history.
9. Backend sends prompt + context to selected LLM.
10. Backend saves user and assistant messages.
11. Widget shows answer and stores browser history.

## Important Security Notes

- Site key is public. It is allowed to be visible in browser HTML.
- Domain validation protects the public site key from being used on random websites.
- Each site has a separate vector collection.
- Chat history is separated by site, visitor ID, and domain.
- Do not enable `DEBUG_LLM_PAYLOADS` in production.
- Do not commit real API keys.
- Use HTTPS in production.

## Current Tech Stack

- Backend: FastAPI, SQLAlchemy, SQLite locally, ChromaDB, LangChain text splitters
- Frontend: React, TypeScript, Vite, TailwindCSS
- Widget: Vanilla TypeScript, Rollup
- Files: PDF, DOCX, TXT, CSV, image OCR
- LLMs: OpenAI, NVIDIA NIM, OpenRouter, DeepSeek, Ollama, llama.cpp

## If You Are Lost

Start with only these commands:

```powershell
# terminal 1
$PROJECT = (Get-Location).Path
$env:DATABASE_URL = "sqlite:///$($PROJECT.Replace('\', '/'))/backend/app.db"
$env:CHROMA_PERSIST_DIR = "$($PROJECT.Replace('\', '/'))/backend/chroma_data"
& "$PROJECT\backend\venv\Scripts\python.exe" -m uvicorn app.main:app --app-dir "$PROJECT\backend" --host 0.0.0.0 --port 8000
```

```powershell
# terminal 2
Push-Location frontend
npm run dev
```

```powershell
# terminal 3
Push-Location widget
npm run build
Pop-Location
python -m http.server 3000 --directory .
```

Then open:

```text
http://localhost:5173
http://localhost:3000/examples/simple-website.html
```
