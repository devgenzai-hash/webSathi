# Deployment Guide

---

## Docker Compose (Recommended)

The simplest way to deploy the full stack:

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    env_file:
      - ./backend/.env
    volumes:
      - ./backend/uploads:/app/uploads
      - ./backend/chroma_data:/app/chroma_data
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "5173:80"
    depends_on:
      - backend
    restart: unless-stopped
```

```bash
docker-compose up -d
```

---

## Backend Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# System dependencies (for PDF/OCR)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Frontend Dockerfile

```dockerfile
# Build stage
FROM node:18-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

---

## Production Checklist

### Security

- [ ] Change `SECRET_KEY` to a random 64+ character string
- [ ] Set `ALLOWED_ORIGINS` to your actual domains (remove `*`)
- [ ] Use HTTPS (via reverse proxy/load balancer)
- [ ] Switch from SQLite to PostgreSQL
- [ ] Set strong `ACCESS_TOKEN_EXPIRE_MINUTES` (e.g., 60 for production)
- [ ] Enable rate limiting
- [ ] Remove `"*"` from CORS origins

### Database

- [ ] Switch to PostgreSQL: `DATABASE_URL=postgresql://user:pass@host:5432/dbname`
- [ ] Set up database backups
- [ ] Run migrations (SQLAlchemy creates tables on first startup)

### Storage

- [ ] Use persistent volume for `uploads/` directory
- [ ] Use persistent volume for `chroma_data/` directory
- [ ] Consider S3/Azure Blob for document storage at scale

### Monitoring

- [ ] Add application logging (structured JSON)
- [ ] Set up health check endpoint monitoring (`/health`)
- [ ] Monitor LLM API response times and errors
- [ ] Track usage_logs table for billing

---

## Cloud Deployment Options

### AWS (ECS/Fargate)

```
┌─────────────┐     ┌──────────────┐     ┌───────────┐
│  CloudFront │────▶│   ALB        │────▶│  ECS      │
│  (CDN)      │     │  (HTTPS)     │     │  Fargate  │
└─────────────┘     └──────────────┘     └─────┬─────┘
                                               │
                                    ┌──────────┼──────────┐
                                    ▼          ▼          ▼
                               ┌────────┐ ┌────────┐ ┌────────┐
                               │  RDS   │ │  EFS   │ │  S3    │
                               │(Postgres)│ │(ChromaDB)│ │(Files) │
                               └────────┘ └────────┘ └────────┘
```

### Azure (App Service)

- Backend: Azure App Service (Python)
- Database: Azure Database for PostgreSQL
- Storage: Azure Blob Storage
- Frontend: Azure Static Web Apps

### Self-Hosted (VPS)

```bash
# On your VPS (Ubuntu)
sudo apt install docker.io docker-compose
git clone https://github.com/your-org/makeWebsiteAIReady.git
cd makeWebsiteAIReady

# Configure
cp backend/.env.example backend/.env
nano backend/.env  # Add your API keys

# Deploy
docker-compose up -d

# Set up Nginx reverse proxy with Let's Encrypt
sudo apt install certbot python3-certbot-nginx
```

---

## Nginx Reverse Proxy (Production)

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name api.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 443 ssl;
    server_name app.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/app.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/app.yourdomain.com/privkey.pem;

    root /var/www/frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
    }
}
```

---

## Scaling Considerations

| Component | Scaling Strategy |
|-----------|-----------------|
| Backend API | Horizontal (multiple uvicorn workers or containers) |
| Database | Vertical (larger instance) → Read replicas |
| ChromaDB | Persistent volume, consider Pinecone/Weaviate for >1M vectors |
| File Storage | Object storage (S3/Blob) for multi-instance setups |
| Widget CDN | Serve `chatbot-widget.js` from CDN (CloudFront/Cloudflare) |
