---
title: TeamFlow Backend API
emoji: 🚀
colorFrom: blue
colorTo: indigo
sdk: docker
sdk_version: "3.13"
app_file: app/main.py
app_port: 7860
pinned: false
license: mit
---

# TeamFlow Backend API

FastAPI backend for TeamFlow Phase 2 - Full-Stack Agency CRM.

## Features

- RESTful API with FastAPI
- JWT Authentication
- PostgreSQL Database (Neon)
- Task & Project Management
- Time Tracking
- Analytics Dashboard
- CORS Enabled for Vercel Frontend

## API Documentation

Once running, visit:
- Swagger UI: `https://your-space-name.hf.space/docs`
- ReDoc: `https://your-space-name.hf.space/redoc`
- Health Check: `https://your-space-name.hf.space/health`

## Environment Variables

Configure these in your Space Settings:

```bash
# Required
DATABASE_URL=postgresql://user:pass@ep-xyz.aws.neon.tech/teamflow?sslmode=require
SECRET_KEY=your-super-secret-jwt-key-at-least-32-chars

# Optional
ENVIRONMENT=production
FRONTEND_URL=https://your-vercel-app.vercel.app
```

## Setup Instructions

### Local Development

```bash
# Install dependencies
uv sync

# Run development server
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Deployment

This Space is configured for Docker deployment. The backend will:

1. Start on port 7860 (HuggingFace Spaces default)
2. Serve API at `/api/v1/*` endpoints
3. Expose health check at `/health`
4. Auto-start with Docker CMD

## Database Setup

1. Create a free [Neon PostgreSQL database](https://neon.tech)
2. Copy your connection string
3. Set `DATABASE_URL` in Space Settings
4. Run migrations (auto-applied on startup)

## Frontend Integration

Your Vercel frontend should set:

```env
NEXT_PUBLIC_API_URL=https://your-space-name.hf.space
```

## Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app --cov-report=html
```
