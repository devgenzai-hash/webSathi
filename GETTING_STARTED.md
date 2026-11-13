# Getting Started — Complete Beginner Guide

This guide gets you from zero to a working AI chatbot on a local test page.
No prior knowledge needed. Just follow each step in order.

---

## What This Project Does

You run a local server. You log into a dashboard. You upload a document (PDF, CSV, TXT, etc.).
The AI chatbot learns from that document. You add one `<script>` tag to any webpage.
Visitors on that page can now ask questions and get answers from your document.

---

## Step 0 — What You Need Installed First

Before anything else, check that these are installed on your computer.

### Check Python

Open PowerShell and run:

```powershell
python --version
```

You need Python 3.9 or newer. If you see an error, download Python from https://python.org/downloads and install it. Tick the box that says **Add Python to PATH** during install.

### Check Node.js

```powershell
node --version
npm --version
```

You need Node 18 or newer. If you see an error, download Node from https://nodejs.org and install it.

### Check Git (optional, only needed if you cloned the repo)

```powershell
git --version
```

---

## Step 1 — One-Time Setup

You only do this once. After this you just run the servers.

Open PowerShell. Go to the project folder first:

```powershell
cd C:\Users\YourName\Documents\Projects\makeWebsiteAIready
```

Replace `YourName` with your actual Windows username.

### 1a — Set Up the Backend

```powershell
python -m venv backend\venv
Push-Location backend
.\venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env -ErrorAction SilentlyContinue
Pop-Location
```

This creates a Python virtual environment and installs all backend libraries.
It takes a few minutes the first time.

If `python` does not work, try `py` instead:

```powershell
py -m venv backend\venv
```

### 1b — Create the .env File

The backend needs a `.env` file with settings. A template was copied in the step above.
Open `backend\.env` in Notepad and check it. For local testing you do not need to change anything.

If you want a real LLM (not just fallback), add your API key:

```
OPENAI_API_KEY=sk-your-key-here
```

Save and close.

### 1c — Set Up the Frontend Dashboard

```powershell
Push-Location frontend
npm install
Pop-Location
```

### 1d — Set Up the Widget

```powershell
Push-Location widget
npm install
npm run build
Pop-Location
```

The widget build creates `widget\dist\chatbot-widget.js`. That file is the chat bubble that appears on websites.

---

## Step 2 — Run Everything

Every time you want to use this project, open **4 PowerShell windows** and run one command in each.

### Window 1 — Backend API

This is the brain. It handles logins, documents, chat, and the AI.

```powershell
cd C:\Users\YourName\Documents\Projects\makeWebsiteAIready

$PROJECT = (Get-Location).Path
$env:DATABASE_URL = "sqlite:///$($PROJECT.Replace('\', '/'))/backend/app.db"
$env:CHROMA_PERSIST_DIR = "$($PROJECT.Replace('\', '/'))/backend/chroma_data"
& "$PROJECT\backend\venv\Scripts\python.exe" -m uvicorn app.main:app --app-dir "$PROJECT\backend" --host 0.0.0.0 --port 8000
```

Leave this running. You should see:

```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

> **Why so many lines?** The `$PROJECT` lines set absolute file paths so the backend always finds the right database no matter which folder you run it from.

### Window 2 — Dashboard

This is the website where you manage your sites and upload documents.

```powershell
cd C:\Users\YourName\Documents\Projects\makeWebsiteAIready
Push-Location frontend
npm run dev
```

Leave this running. You should see:

```
VITE ready in ...ms
➜  Local:   http://localhost:5173/
```

### Window 3 — Widget Build (only if you edit widget code)

If you are not editing the widget, skip this window. The widget was already built in Step 1d.

If you do edit widget code, run this to auto-rebuild on save:

```powershell
cd C:\Users\YourName\Documents\Projects\makeWebsiteAIready
Push-Location widget
npm run dev
```

### Window 4 — Local Test Website

This serves the example HTML page so you can test the widget in a browser.

```powershell
cd C:\Users\YourName\Documents\Projects\makeWebsiteAIready
python -m http.server 3000 --directory .
```

Leave this running. You should see:

```
Serving HTTP on :: port 3000
```

---

## Step 3 — Check Everything Is Running

Open a new PowerShell window and run:

```powershell
netstat -ano | findstr ":8000 :5173 :3000"
```

You should see `LISTENING` next to all three ports. If one is missing, go back and start that window.

Also open this URL in your browser to confirm the backend is alive:

```
http://localhost:8000/health
```

You should see:

```json
{"status": "ok", "version": "1.0.0"}
```

---

## Step 4 — First Time: Create an Account

1. Open your browser and go to: `http://localhost:5173`
2. Click **Register**.
3. Enter any email and password. This is a local account, not a real email service.
4. You are now logged in to the dashboard.

---

## Step 5 — Register Your Website

1. On the dashboard, click **New Site** or **Add Site**.
2. Give it a name, for example `My Test Site`.
3. In the **Domain** field, enter exactly:
   ```
   localhost:3000
   ```
   This tells the backend to only allow the widget when it is loaded from `localhost:3000`.
4. Save the site.
5. You will see a **Site Key** — a long code like `48adb390-3239-4d44-b7c6-d1fac788f373`. Copy it.

---

## Step 6 — Upload a Document

1. Click on your site in the dashboard.
2. Go to **Documents**.
3. Click **Upload**.
4. Pick a file — CSV, PDF, TXT, or DOCX all work.
5. Wait. The status will change from `processing` to `ready`.
6. When it says `ready` and shows a chunk count (e.g. `6 chunks`), the document is searchable.

> **What is a chunk?** The backend splits your document into small pieces called chunks. Each chunk gets an embedding (a number vector). When someone asks a question, the backend finds the most relevant chunks and gives them to the AI.

---

## Step 7 — Put the Widget on the Test Page

1. In the dashboard, go to your site and click **Embed**.
2. Copy the embed code. It looks like this:

```html
<script
  src="http://localhost:3000/widget/dist/chatbot-widget.js"
  data-site-key="YOUR_SITE_KEY_HERE"
  data-api-url="http://localhost:8000"
></script>
```

3. Open `examples\simple-website.html` in a text editor.
4. Find the `<script ...>` tag near the bottom.
5. Replace `data-site-key` value with your actual site key.
6. Save the file.

---

## Step 8 — Test the Widget

1. Open: `http://localhost:3000/examples/simple-website.html`
2. A chat bubble appears in the bottom right corner.
3. Click it.
4. Ask a question about your uploaded document.
5. The AI should answer based on your document.

---

## What Each URL Is For

| URL | What it is |
| --- | --- |
| `http://localhost:8000` | Backend API |
| `http://localhost:8000/docs` | Auto-generated API documentation |
| `http://localhost:8000/health` | Quick health check |
| `http://localhost:5173` | Dashboard — manage sites, upload docs, get embed code |
| `http://localhost:3000/examples/simple-website.html` | Test page for the widget |

---

## Common Problems and Fixes

### Widget does not show up

- Did you build the widget? Run: `Push-Location widget; npm run build`
- Is the site key in the HTML correct?
- Is port 3000 running the Python server (not something else)?

Check what is on port 3000:

```powershell
netstat -ano | findstr ":3000"
```

Find the PID, then check the process:

```powershell
Get-Process -Id THE_PID_HERE
```

If it says `node` instead of `python`, kill it and restart the Python server:

```powershell
Stop-Process -Id THE_PID_HERE -Force
python -m http.server 3000 --directory .
```

### Widget says "domain not authorized"

The domain registered on the site must match where the page loads.

- If the HTML page is at `http://localhost:3000/...` → register the site as `localhost:3000`
- If the HTML page is at `http://localhost:5173/...` → register the site as `localhost:5173`

### Document stays on "processing" or shows "failed"

- Check the document error in the dashboard or database:

```powershell
Push-Location backend
.\venv\Scripts\python.exe -c "import sqlite3; db=sqlite3.connect('app.db'); [print(row) for row in db.execute('select filename,status,chunk_count,error_message from documents')]"
Pop-Location
```

- If the error says `No process is on the other end of the pipe`, restart the backend and try uploading again. This is a Windows ChromaDB glitch that auto-recovers on retry.

### Backend uses wrong database

Always start the backend with the full `$PROJECT` command from Step 2, Window 1.
Never just run `uvicorn app.main:app` on its own — it will use the wrong database path.

### Port already in use

```powershell
netstat -ano | findstr ":8000"
Stop-Process -Id THE_PID -Force
```

---

## How to Stop Everything

Press `Ctrl+C` in each terminal window.

Or find and kill by port:

```powershell
# Find PID
netstat -ano | findstr ":8000"
# Kill it
Stop-Process -Id THE_PID -Force
```

---

## Folder Map

```
makeWebsiteAIready/
│
├── backend/          ← Python API (FastAPI). This is the server.
│   ├── app/          ← Application code
│   ├── venv/         ← Python packages (created in Step 1)
│   ├── app.db        ← SQLite database (created automatically)
│   ├── chroma_data/  ← Vector database for document search
│   ├── uploads/      ← Uploaded files are saved here
│   ├── .env          ← Your API keys and settings
│   └── requirements.txt
│
├── frontend/         ← React dashboard (the admin UI)
│   ├── src/          ← Dashboard source code
│   └── node_modules/ ← Installed packages (after npm install)
│
├── widget/           ← The embeddable chat bubble
│   ├── src/          ← Widget source code
│   └── dist/         ← Built widget JS (after npm run build)
│       └── chatbot-widget.js  ← THIS is what you put on websites
│
└── examples/
    └── simple-website.html  ← Local test page
```

---

## Quick-Start Cheat Sheet

Every day when you want to use the project, open 4 PowerShell windows and run:

**Window 1 (backend):**
```powershell
cd C:\PATH\TO\makeWebsiteAIready
$PROJECT = (Get-Location).Path
$env:DATABASE_URL = "sqlite:///$($PROJECT.Replace('\', '/'))/backend/app.db"
$env:CHROMA_PERSIST_DIR = "$($PROJECT.Replace('\', '/'))/backend/chroma_data"
& "$PROJECT\backend\venv\Scripts\python.exe" -m uvicorn app.main:app --app-dir "$PROJECT\backend" --host 0.0.0.0 --port 8000
```

**Window 2 (dashboard):**
```powershell
cd C:\PATH\TO\makeWebsiteAIready
Push-Location frontend; npm run dev
```

**Window 3 (test site):**
```powershell
cd C:\PATH\TO\makeWebsiteAIready
python -m http.server 3000 --directory .
```

Then open `http://localhost:5173` and `http://localhost:3000/examples/simple-website.html`.
