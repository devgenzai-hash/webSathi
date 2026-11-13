# MakeWebsiteAIReady — Documentation

> **AI Chatbot-as-a-Service Platform**  
> Add an intelligent, document-aware chatbot to any website in under 5 minutes.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Getting Started](./getting-started.md)
- [API Reference](./api-reference.md)
- [Widget Integration](./widget-integration.md)
- [Frontend Dashboard](./frontend-dashboard.md)
- [LLM Providers](./llm-providers.md)
- [RAG Pipeline](./rag-pipeline.md)
- [Database Schema](./database-schema.md)
- [Deployment](./deployment.md)
- [Security](./security.md)

---

## Overview

MakeWebsiteAIReady is a complete platform that enables website owners to embed an AI-powered chatbot that answers visitor questions **exclusively from their uploaded documentation**. It combines:

- **Retrieval-Augmented Generation (RAG)** — documents are chunked, embedded, and stored in a vector database for semantic search
- **Multi-Provider LLM Support** — OpenAI, NVIDIA NIM, OpenRouter, DeepSeek, Ollama, llama.cpp
- **Strong Guardrails** — the chatbot refuses off-topic questions, jailbreak attempts, and never fabricates information
- **Multi-Tenant Architecture** — complete data isolation between users and sites
- **Embeddable Widget** — a single `<script>` tag adds the chatbot to any website

### Key Features

| Feature | Description |
|---------|-------------|
| Document Upload | PDF, DOCX, TXT, CSV, images (with OCR) |
| RAG Pipeline | Chunking → Embedding → Vector Search → Reranking |
| 6 LLM Providers | 11 models across free, starter, pro, enterprise tiers |
| Widget | Vanilla JS, zero dependencies, customizable appearance |
| Dashboard | React SPA for site management and configuration |
| Plans | Free (2 sites), Starter (5), Pro (20), Enterprise (100) |
| Security | JWT auth, site-key widget auth, data isolation, guardrails |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Layer                              │
├─────────────────┬───────────────────────┬───────────────────────┤
│  React Dashboard│   Widget (embedded)   │   Direct API calls    │
│  (JWT Auth)     │   (Site-Key Auth)     │                       │
└────────┬────────┴───────────┬───────────┴───────────┬───────────┘
         │                    │                       │
         ▼                    ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Backend (Port 8000)                   │
├─────────────────────────────────────────────────────────────────┤
│  /api/v1/auth/*       — User registration & login (JWT)         │
│  /api/v1/sites/*      — Site CRUD (authenticated)               │
│  /api/v1/sites/*/documents/* — Document upload (authenticated)  │
│  /api/v1/chat/*       — Widget chat (site-key authenticated)    │
│  /api/v1/models/*     — Available models listing                │
└────────┬────────────────────┬───────────────────────┬───────────┘
         │                    │                       │
         ▼                    ▼                       ▼
┌──────────────┐   ┌──────────────────┐   ┌───────────────────────┐
│   SQLite /   │   │    ChromaDB      │   │   LLM Providers       │
│  PostgreSQL  │   │  (Vector Store)  │   │  (OpenAI, NVIDIA,     │
│              │   │                  │   │   DeepSeek, Ollama...) │
└──────────────┘   └──────────────────┘   └───────────────────────┘
```

### Technology Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11+, FastAPI, SQLAlchemy, Pydantic v2 |
| Vector DB | ChromaDB (per-site collection isolation) |
| Auth | JWT (python-jose) + bcrypt password hashing |
| LLM Client | httpx async HTTP client |
| Frontend | React 18, Vite, TailwindCSS, React Router v6 |
| Widget | TypeScript, Rollup (IIFE bundle) |
| Deployment | Docker Compose, Nginx |
