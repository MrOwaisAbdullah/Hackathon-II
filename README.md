# TeamFlow CRM

[![CI/CD](https://github.com/MrOwaisAbdullah/Teamflow/actions/workflows/deploy.yml/badge.svg)](https://github.com/MrOwaisAbdullah/Teamflow/actions/workflows/deploy.yml)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/MrOwaisAbdullah/Teamflow/blob/main/LICENSE)
[![Next.js](https://img.shields.io/badge/Next.js-16-black)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)](https://fastapi.tiangolo.com/)
[![AI/ML](https://img.shields.io/badge/AI-OpenAI-orange)](https://openai.com/)

**From Console CLI to AI-Powered Agency Management**

TeamFlow CRM is a multi-phase evolution project for Hackathon II - transforming from a simple console task distribution tool into a full-stack, AI-powered agency management system with voice input, intelligent recommendations, and real-time collaboration.

---

## Project Overview

TeamFlow is **NOT a basic todo app**. It's a comprehensive **team task management system designed specifically for creative agencies**:

- **Multi-tenancy** with complete agency data isolation
- **Drag-and-drop Kanban board** for intuitive task management
- **Time tracking** with profitability analytics
- **AI-powered workflow automation** via 21+ MCP tools
- **Voice input support** for hands-free task creation
- **Real-time analytics** dashboard for project insights

### The Evolution: Three Phases

| Phase | Name | Technology | Status | Directory |
|-------|------|------------|--------|-----------|
| 1 | Console CLI | Python 3.13+, Typer, Rich | ✅ Complete | `001-console-task-distribution/` |
| 2 | Full-Stack Web CRM | Next.js 16, FastAPI, PostgreSQL | ✅ Complete | `teamflow-web/` |
| 3 | AI Chatbot Integration | OpenAI ChatKit, Agents SDK, MCP | ✅ Complete | `teamflow-web/` |

---

## Features Matrix

| Feature | Phase 1: CLI | Phase 2: Web CRM | Phase 3: AI Chat |
|---------|--------------|------------------|------------------|
| **Task Management** | Command-line CRUD | Web UI with drag-drop | Voice + AI chat |
| **Team Collaboration** | User assignment | Multi-tenant agencies | AI auto-assignment |
| **Project Management** | Simple grouping | Full project lifecycle | AI recommendations |
| **Time Tracking** | ❌ | ✅ Billable hours | ✅ Voice logging |
| **Analytics Dashboard** | ❌ | ✅ Real-time charts | ✅ Predictive insights |
| **Voice Input** | ❌ | ❌ | ✅ Web Speech API |
| **AI Recommendations** | ❌ | ❌ | ✅ Smart assignee |
| **RAG Knowledge Base** | ❌ | ❌ | ✅ Qdrant vector DB |

---

## Phase 1: Console CLI (001-console-task-distribution)

A rich terminal interface for task distribution with Python 3.13+, Typer CLI framework, and Pydantic validation.

**Features:**
- Task CRUD operations with rich terminal UI
- User management with role assignment
- Team assignment and workload tracking
- Persistent in-memory storage
- Colorful, interactive console output

**Quick Start:**
```bash
cd 001-console-task-distribution
pip install -e .
teamflow
```

---

## Phase 2: Full-Stack Web CRM (teamflow-web/)

Modern web application built with Next.js 16 and FastAPI for complete agency management.

**Features:**
- **Kanban Task Board:** Drag-and-drop with dnd-kit physics
- **Project Management:** Status tracking, team assignments, deadlines
- **Time Tracking:** Billable hours, project profitability
- **Analytics Dashboard:** Real-time stats, animated charts
- **Multi-tenancy:** Agency-scoped data isolation
- **Responsive Design:** Mobile-friendly with dark mode

**Tech Stack:**
- Frontend: Next.js 16, TypeScript, Tailwind CSS, Motion.dev
- Backend: FastAPI, SQLModel, PostgreSQL (Neon)
- Auth: JWT tokens with agency-scoped sessions

---

## Phase 3: AI Chatbot Integration (teamflow-web/)

AI-powered assistant with 21+ MCP tools, RAG knowledge base, and voice input support.

**Features:**
- **ChatWidget:** Floating AI assistant with streaming responses
- **21 MCP Tools:** Task/project/time management, analytics, recommendations
- **Voice Input:** Web Speech API for hands-free task creation
- **RAG Pipeline:** Qdrant vector DB for semantic document search
- **Multi-Model AI:** Gemini 2.0 Flash with GPT-5 fallback
- **Fullscreen Mode:** Dedicated chat interface at `/chat`
- **Multi-Language:** English + Urdu support

**AI Architecture:**
- OpenAI Agents SDK with custom agent implementation
- FastMCP server for tool integration
- OpenRouter API with automatic fallback
- Streaming NDJSON responses for real-time chat

---

## Tech Stack Summary

### Frontend
```yaml
Framework: Next.js 16 (App Router, Turbopack)
Language: TypeScript 5.7+
Styling: Tailwind CSS
Animations: Motion.dev (Framer Motion 11)
State: Zustand, React Query
Drag & Drop: @dnd-kit
Auth: Better Auth React
AI: OpenAI ChatKit React
```

### Backend
```yaml
Framework: FastAPI 0.115+
Language: Python 3.13+
ORM: SQLModel (SQLAlchemy 2.0 async)
Database: PostgreSQL (Neon Serverless)
Auth: JWT tokens
AI: OpenAI Agents SDK, OpenRouter, GPT-5
Vector DB: Qdrant (for RAG)
MCP: FastMCP server framework
```

### Deployment
```yaml
Frontend: Vercel (auto-deploy from main)
Backend: HuggingFace Spaces (Docker SDK)
Database: Neon PostgreSQL (free tier)
CI/CD: GitHub Actions
```

---

## Quick Start

### Prerequisites
- Node.js 20+
- Python 3.13+
- PostgreSQL database (or Neon free tier)

### Clone Repository
```bash
git clone https://github.com/MrOwaisAbdullah/Teamflow.git
cd "Hackathon II"

# Checkout specific phase branches
git checkout 001-console-task-distribution  # Phase 1: Console CLI
git checkout 002-fullstack-web-crm          # Phase 2: Web CRM
git checkout 001-ai-chatbot                 # Phase 3: AI Integration
```

### Phase 1: Console CLI
```bash
cd 001-console-task-distribution
pip install -e .
teamflow
```

### Phase 2: Web CRM
```bash
# Backend
cd teamflow-web/backend
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd teamflow-web/frontend
npm install
cp .env.example .env.local
npm run dev
```

Visit http://localhost:3000

### Phase 3: AI Chatbot
Navigate to `/chat` in the web app or click the floating chat widget.

---

## Deployment Links

| Service | URL | Status |
|---------|-----|--------|
| **Frontend** | [teamflow-crm.vercel.app](https://teamflow-crm.vercel.app) | ✅ Live |
| **Backend** | [hf.space/spaces/mrowais/...](https://huggingface.co/spaces/mrowais/teamflow-backend) | ✅ Live |
| **Demo Video** | [YouTube: TeamFlow Demo](https://youtube.com) | 🎬 Watch |

---

## Project Structure

```
Hackathon II/
├── 001-console-task-distribution/    # Phase 1: CLI application
│   ├── src/                          # Source code
│   ├── tests/                        # Unit tests
│   └── pyproject.toml                # Python project config
│
├── teamflow-web/                     # Phase 2 & 3: Full-stack + AI
│   ├── frontend/                     # Next.js 16 application
│   │   ├── src/
│   │   │   ├── app/                  # App Router pages
│   │   │   │   ├── (main)/           # Dashboard pages
│   │   │   │   ├── (marketing)/      # Landing & pricing
│   │   │   │   └── chat/             # AI chatbot page
│   │   │   ├── components/
│   │   │   │   ├── ui/               # shadcn/ui components
│   │   │   │   ├── dashboard/        # Dashboard widgets
│   │   │   │   ├── board/            # Kanban board
│   │   │   │   └── chat/             # ChatKit integration
│   │   │   └── lib/                  # Utilities, API clients
│   │   ├── public/                   # Static assets
│   │   └── package.json
│   │
│   ├── backend/                      # FastAPI application
│   │   ├── app/
│   │   │   ├── api/endpoints/        # Auth, tasks, projects
│   │   │   ├── chatkit/              # MCP server (21 tools)
│   │   │   ├── models/               # SQLModel schemas
│   │   │   ├── services/             # Business logic
│   │   │   └── main.py               # FastAPI entry
│   │   ├── alembic/                  # Database migrations
│   │   ├── tests/                    # Pytest tests
│   │   ├── Dockerfile                # HuggingFace deployment
│   │   └── pyproject.toml
│   │
│   └── README.md                     # Web-specific docs
│
├── specs/                            # Feature specifications
│   ├── 001-console-task-distribution/
│   ├── 002-fullstack-web-crm/
│   └── 001-ai-chatbot/
│
├── social-media-posts/               # LinkedIn announcements
├── .github/workflows/                # CI/CD pipelines
└── README.md                         # This file
```

---

## Development Highlights

### Spec-Driven Development (SDD)
- Feature specifications in `specs/` directory
- ADR (Architecture Decision Records) for significant decisions
- PHR (Prompt History Records) for all AI interactions
- Test-driven approach with Playwright E2E and Pytest

### Production Deployment Challenges
- **CORS Issues:** Resolved with proper frontend/backend configuration
- **MCP Integration:** Custom server implementation with 21 tools
- **AI Rate Limiting:** Automatic fallback from OpenRouter to OpenAI
- **Voice Input:** Web Speech API integration with language detection
- **Real-time Streaming:** NDJSON protocol for chat responses

### Animation-First Design
- Motion.dev for 60fps transitions
- Physics-based drag with dnd-kit
- Celebration animations on task completion
- Smooth page transitions with AnimatePresence

---

## Environment Variables

### Backend (.env)
```env
DATABASE_URL=postgresql://user:pass@ep-xyz.aws.neon.tech/teamflow?sslmode=require
SECRET_KEY=your-super-secret-jwt-key-at-least-32-chars
OPENAI_API_KEY=sk-...
ENVIRONMENT=development
FRONTEND_URL=http://localhost:3000
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_CHATKIT_DOMAIN_KEY=your-registered-domain
```

---

## Hackathon Submission Strategy

To support multi-phase hackathon submissions within a single repository:

1. **Development:** Work continues on `main` or feature branches
2. **Phase Branches:** Each phase has its own feature branch:
   - `001-console-task-distribution` - Phase 1: Console CLI
   - `002-fullstack-web-crm` - Phase 2: Full-Stack Web CRM
   - `001-ai-chatbot` - Phase 3: AI Chatbot Integration
3. **Submit:** Provide the GitHub branch URL for judging
4. **Continue:** Switch to next branch for continued development

**Available Branches:**
```bash
# List all branches
git branch -a

# Checkout a specific phase
git checkout 001-console-task-distribution
git checkout 002-fullstack-web-crm
git checkout 001-ai-chatbot
```

---

## API Documentation

When running the backend locally:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

---

## Testing

### Backend Tests
```bash
cd teamflow-web/backend
pytest --cov=app --cov-report=html
```

### Frontend E2E Tests
```bash
cd teamflow-web/frontend
npm run test:e2e
```

---

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## License

MIT © 2025 Owais Abdullah

---

## Credits & Technologies

**Built for Hackathon II by Owais Abdullah**

**Powered by:**
- [Next.js](https://nextjs.org/) - React framework
- [FastAPI](https://fastapi.tiangolo.com/) - Python web framework
- [OpenAI](https://openai.com/) - AI/ML capabilities
- [Neon](https://neon.tech) - Serverless PostgreSQL
- [Vercel](https://vercel.com) - Frontend deployment
- [HuggingFace](https://huggingface.co) - Backend hosting

---

**Built with ❤️ using Next.js 16, FastAPI, and modern AI technologies**
