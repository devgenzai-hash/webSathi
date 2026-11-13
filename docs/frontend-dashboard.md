# Frontend Dashboard

The dashboard is a React 18 single-page application for managing sites, documents, and chatbot configuration.

---

## Technology Stack

| Library | Version | Purpose |
|---------|---------|---------|
| React | 18.3 | UI framework |
| React Router | 6.26 | Client-side routing |
| Vite | 5.4 | Build tool & dev server |
| TailwindCSS | 3.4 | Utility-first CSS |
| Axios | 1.7 | HTTP client |
| Lucide React | 0.436 | Icon library |
| TypeScript | 5.5 | Type safety |

---

## Page Routes

| Route | Component | Auth Required | Description |
|-------|-----------|---------------|-------------|
| `/login` | `Login.tsx` | No | Email/password login form |
| `/register` | `Register.tsx` | No | Account registration |
| `/` | `Dashboard.tsx` | Yes | Site listing & management |
| `/sites/:id` | `SiteDetail.tsx` | Yes | Site configuration & documents |
| `/pricing` | `Pricing.tsx` | No | Plan comparison |

---

## Authentication Flow

```
Login/Register → JWT stored in localStorage → Axios interceptor adds Bearer header
```

- Token stored: `localStorage.setItem('token', access_token)`
- Protected routes check for token presence, redirect to `/login` if missing
- API service adds `Authorization: Bearer <token>` to all requests automatically

---

## Pages Overview

### Dashboard (`/`)

- Lists all sites for the current user
- "Create New Site" button (with plan limit enforcement)
- Quick actions: view site, copy site key, delete site
- Shows site status (verified/unverified)

### Site Detail (`/sites/:id`)

**4 configuration sections:**

1. **General Settings** — Site name, domain, verification status
2. **Model Configuration** — Provider selector, model selector, temperature slider, max tokens
3. **Document Management** — Upload files, view document list, delete documents
4. **Widget Customization** — Position, color, title, welcome message, live embed code preview

**Embed Code Generator:**

```html
<script 
  src="https://your-domain.com/widget/chatbot-widget.js"
  data-site-key="auto-filled-from-site"
  data-api-url="http://localhost:8000"
  data-position="bottom-right"
  data-color="#6366f1"
></script>
```

### Login (`/login`)

- Email + password form
- "Don't have an account?" link to register
- Error display for invalid credentials

### Register (`/register`)

- Email + password + optional full name
- Password minimum 8 characters
- Auto-login on successful registration

### Pricing (`/pricing`)

| Plan | Sites | Price | Features |
|------|-------|-------|----------|
| Free | 2 | $0/mo | Basic models, 100 messages/day |
| Starter | 5 | $29/mo | GPT-4o-mini, NVIDIA NIM, 1000 msg/day |
| Pro | 20 | $99/mo | All models, 10000 msg/day, priority |
| Enterprise | 100 | Custom | Dedicated support, SLA, custom models |

---

## API Service Layer

All API calls go through a centralized Axios instance:

```typescript
// frontend/src/services/api.ts
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
});

// Automatically attach JWT token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

---

## Development

```bash
cd frontend
npm install
npm run dev      # → http://localhost:5173
npm run build    # → dist/ (production build)
npm run preview  # Serve production build locally
```

### Project Structure

```
frontend/
├── index.html
├── package.json
├── vite.config.ts
├── tsconfig.json
├── tailwind.config.js
├── postcss.config.js
├── public/
└── src/
    ├── main.tsx          # Entry point
    ├── App.tsx           # Router setup
    ├── index.css         # Tailwind imports
    ├── components/
    │   └── Layout.tsx    # Shared layout wrapper
    ├── pages/
    │   ├── Dashboard.tsx
    │   ├── Login.tsx
    │   ├── Register.tsx
    │   ├── SiteDetail.tsx
    │   └── Pricing.tsx
    └── services/
        └── api.ts        # Axios API client
```

---

## Production Build

```bash
npm run build
```

Output in `dist/` — serve with Nginx or any static file server:

```nginx
server {
    listen 80;
    root /usr/share/nginx/html;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://backend:8000;
    }
}
```
