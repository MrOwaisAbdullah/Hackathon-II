# TeamFlow - Agency Task Management CRM

Phase 2: Full-Stack Web Application

## Overview

TeamFlow is a task management CRM built for creative agencies. It provides team collaboration, project tracking, time logging, and profitability analytics in a unified interface.

## Tech Stack

### Backend
- **Python 3.13+** with FastAPI
- **SQLModel** + PostgreSQL (Neon)
- **JWT Authentication** + Better Auth
- **Alembic** for migrations

### Frontend
- **Next.js 16** (App Router)
- **TypeScript 5.7+**
- **Motion.dev** (Framer Motion 11)
- **dnd-kit** for drag-and-drop
- **Better Auth React**

## Quick Start

### Prerequisites
- Python 3.13+
- Node.js 20+
- PostgreSQL 15+ (or [Neon](https://neon.tech) account)

### 1. Clone and Setup

```bash
# Navigate to project
cd teamflow-web

# Backend setup
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e ".[dev]"
cp ../.env.example .env
# Edit .env with your DATABASE_URL and secrets

# Frontend setup
cd ../frontend
npm install
cp ../.env.example .env.local
```

### 2. Database Setup

```bash
# From backend directory
cd backend
alembic upgrade head
```

### 3. Start Services

```bash
# Terminal 1: Backend
cd backend
uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev
```

### 4. Access

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Project Structure

```
teamflow-web/
├── backend/          # FastAPI application
│   ├── app/          # Source code
│   ├── tests/        # Test suites
│   └── alembic/      # Database migrations
├── frontend/         # Next.js application
│   ├── src/          # Source code
│   ├── e2e/          # E2E tests
│   └── public/       # Static assets
└── README.md         # This file
```

## Development

### Backend Testing
```bash
cd backend
pytest --cov=app
```

### Frontend Testing
```bash
cd frontend
npm run test:e2e
```

### Code Quality
```bash
# Backend
cd backend
ruff check .
mypy app/

# Frontend
cd frontend
npm run lint
npx tsc --noEmit
```

## Architecture Highlights

### Multi-Tenancy
- Agency-scoped data isolation
- JWT tokens include `agency_id`
- All queries filtered by tenant

### Animation-First
- Motion.dev for smooth transitions
- dnd-kit physics for drag interactions
- 60fps performance targets
- Spring animations for natural feel

### Real-Time Updates
- 10-second polling for dashboard
- Manual refresh button
- Optimistic UI updates
- Network loss handling

## Deployment

### Backend
```bash
cd backend
# Set production environment variables
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
npm run build
npm start
```

## Documentation

- [Backend README](./backend/README.md)
- [Frontend README](./frontend/README.md)
- [API Documentation](http://localhost:8000/docs) (when running)

## License

MIT

## Support

For issues or questions, please open a GitHub issue.
