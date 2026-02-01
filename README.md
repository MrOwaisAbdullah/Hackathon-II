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

### The Evolution: Five Phases

| Phase | Name | Technology | Status | Directory |
|-------|------|------------|--------|-----------|
| 1 | Console CLI | Python 3.13+, Typer, Rich | ✅ Complete | `001-console-task-distribution/` |
| 2 | Full-Stack Web CRM | Next.js 16, FastAPI, PostgreSQL | ✅ Complete | `teamflow-web/` |
| 3 | AI Chatbot Integration | OpenAI ChatKit, Agents SDK, MCP | ✅ Complete | `teamflow-web/` |
| 4 | Local Kubernetes | Docker, Minikube, Helm, kubectl-ai | ✅ Complete | `helm/teamflow/` |
| 5 | Cloud Deployment | Dapr, Kafka, Oracle OKE, CI/CD | ✅ Complete | `teamflow-web/` |

---

## Features Matrix

| Feature | Phase 1: CLI | Phase 2: Web CRM | Phase 3: AI Chat | Phase 4: K8s | Phase 5: Cloud |
|---------|--------------|------------------|------------------|--------------|----------------|
| **Task Management** | Command-line CRUD | Web UI with drag-drop | Voice + AI chat | ✅ Containerized | ✅ Microservices |
| **Team Collaboration** | User assignment | Multi-tenant agencies | AI auto-assignment | ✅ K8s services | ✅ Event-driven |
| **Project Management** | Simple grouping | Full project lifecycle | AI recommendations | ✅ HA deployment | ✅ Auto-scaling |
| **Time Tracking** | ❌ | ✅ Billable hours | ✅ Voice logging | ✅ | ✅ |
| **Analytics Dashboard** | ❌ | ✅ Real-time charts | ✅ Predictive insights | ✅ | ✅ |
| **Voice Input** | ❌ | ❌ | ✅ Web Speech API | ✅ | ✅ |
| **AI Recommendations** | ❌ | ❌ | ✅ Smart assignee | ✅ | ✅ |
| **RAG Knowledge Base** | ❌ | ❌ | ✅ Qdrant vector DB | ✅ | ✅ |
| **Real-time Updates** | ❌ | ❌ | ❌ | ❌ | ✅ WebSocket |
| **Recurring Tasks** | ❌ | ❌ | ❌ | ❌ | ✅ Dapr cron |
| **Reminders** | ❌ | ❌ | ❌ | ❌ | ✅ SendGrid |
| **Auto-scaling** | ❌ | ❌ | ❌ | ❌ | ✅ HPA |
| **TLS Certificates** | ❌ | ❌ | ❌ | ❌ | ✅ Let's Encrypt |

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

## Phase 4: Local Kubernetes (helm/teamflow/)

Container-based deployment with Docker, Minikube, and Helm for cloud-native development.

**Features:**
- **Multi-stage Docker builds** for optimized image sizes
- **Helm charts** with environment-agnostic templates
- **kubectl-ai** integration for natural-language K8s operations
- **Health probes** (liveness/readiness) for pod monitoring
- **Resource limits** for CPU/memory management
- **Local testing** before cloud deployment

**Tech Stack:**
- Container Runtime: Docker Desktop
- Local Cluster: Minikube (4 CPUs, 6GB RAM)
- Package Manager: Helm 3.x
- AI Operations: kubectl-ai, Docker Gordon, Kagent

---

## Phase 5: Advanced Cloud Deployment (teamflow-web/)

Event-driven microservices architecture with Dapr, Kafka, and production cloud deployment.

**Features:**
- **Event-Driven Architecture:** Dapr pub/sub with Kafka/Redpanda
- **Recurring Tasks:** Automated task generation with customizable schedules
- **Due Date Reminders:** SendGrid email notifications (15m, 1h, 1d, 1w before)
- **Real-time Updates:** WebSocket live task synchronization
- **Microservices:** Notification, Recurring Task, Realtime Sync services
- **Auto-scaling:** Horizontal Pod Autoscaler (HPA)
- **TLS Certificates:** Automated Let's Encrypt via cert-manager
- **CI/CD Pipeline:** GitHub Actions with staging/production environments

**Microservices Architecture:**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           NGINX Ingress Controller                          │
│                    (TLS Termination, WebSocket Proxy, Sticky Sessions)       │
└───────────────────────────┬─────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────────────────────────┐
│   Frontend   │   │   Backend    │   │      Realtime Sync Service       │
│  (Next.js)   │   │  (FastAPI)   │   │         (WebSocket)              │
│              │   │              │   │                                   │
│  + Dapr      │   │  + Dapr      │   │  NO DAPR (WebSocket unsupported)  │
│  Sidecar     │◄──┤  Sidecar     │   │                                   │
└──────┬───────┘   └──────┬───────┘   └──────────────────────────────────┘
       │                  │
       │                  ▼
       │        ┌──────────────────────┐
       │        │   Dapr Sidecar       │
       │        │                      │
       │        │  ┌────────────────┐  │
       │        │  │  Pub/Sub       │  │
       │        │  │  (Kafka)       │  │
       │        │  └───────┬────────┘  │
       │        └──────────┼───────────┘
       │                   │
       │                   ▼
       │        ┌──────────────────────────────────────────────────────────┐
       │        │              Kafka / Redpanda Cluster                    │
       │        │  ┌─────────────┬─────────────┬─────────────┬───────────┐ │
       │        │  │task-events  │  reminders  │task-updates │time-logged│ │
       │        │  └─────────────┴─────────────┴─────────────┴───────────┘ │
       │        └──────────────────────┬───────────────────────────────────┘
       │                               │
       │                               ▼
       │        ┌──────────────────────────────────────────────────────────┐
       │        │                      Microservices                        │
       │        │  ┌─────────────────┬─────────────────┬─────────────────┐ │
       │        │  │  Notification   │  Recurring Task │  State Store    │ │
       │        │  │    Service      │    Service      │  (PostgreSQL)   │ │
       │        │  │                 │                 │                 │ │
       │        │  │  + Dapr         │  + Dapr         │  + Dapr         │ │
       │        │  │  Sidecar        │  Sidecar        │  Sidecar        │ │
       │        │  └─────────────────┴─────────────────┴─────────────────┘ │
       │        └──────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                       External Services                                   │
│  ┌──────────────┬──────────────┬──────────────┬──────────────────────┐  │
│  │   Neon DB    │   SendGrid   │   Oracle OKE │    GitHub Actions     │  │
│  │ (PostgreSQL) │   (Email)    │  (K8s Cluster)│     (CI/CD)          │  │
│  └──────────────┴──────────────┴──────────────┴──────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────┘
```

**Dapr Components:**
| Component | Type | Purpose |
|-----------|------|---------|
| `kafka-pubsub` | Pub/Sub | Event streaming (task-events, reminders, task-updates) |
| `state-postgresql` | State | Distributed state management |
| `secretstores.kubernetes` | Secrets | Kubernetes secret integration |
| `bindings.cron` | Bindings | Scheduled recurring task generation |

**Kafka Topics:**
| Topic | Purpose | Subscribers |
|-------|---------|-------------|
| `task-events` | Task CRUD events | Notification Service, Realtime Sync |
| `reminders` | Due date reminders | Notification Service |
| `task-updates` | Real-time changes | Realtime Sync Service |
| `time-logged` | Time tracking events | Analytics Service |

**Deployment Environments:**
| Environment | Cluster | Purpose | URL |
|-------------|---------|---------|-----|
| Local | Minikube | Development | `teamflow.local` |
| Staging | Minikube/OKE | Pre-production | `staging.teamflow.example.com` |
| Production | Oracle OKE Always Free | Live | `teamflow.example.com` |

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
Local K8s: Docker + Minikube + Helm
Cloud (Phase 5): Oracle OKE Always Free
Event Streaming: Kafka/Redpanda
Distributed Runtime: Dapr 1.14.0
TLS Certificates: Let's Encrypt (cert-manager)
Email: SendGrid
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

### Phase 4: Local Kubernetes
See [Local Kubernetes Deployment](#local-kubernetes-deployment) section below.

### Phase 5: Cloud Deployment

**Prerequisites:**
- Oracle Cloud account with OKE Always Free tier
- GitHub Container Registry (GHCR) access
- Domain name configured for production

**Quick Deploy to Oracle OKE:**
```bash
# 1. Build and push images to GHCR
docker build -t ghcr.io/YOUR_USERNAME/teamflow-backend:latest teamflow-web/backend/
docker build -t ghcr.io/YOUR_USERNAME/teamflow-frontend:latest teamflow-web/frontend/
docker push ghcr.io/YOUR_USERNAME/teamflow-backend:latest
docker push ghcr.io/YOUR_USERNAME/teamflow-frontend:latest

# 2. Create GHCR credentials secret
kubectl create secret docker-registry ghcr-credentials \
  --docker-server=ghcr.io \
  --docker-username=YOUR_USERNAME \
  --docker-password=YOUR_TOKEN \
  --namespace=teamflow-production

# 3. Install Dapr on cluster
dapr init -k --runtime-version 1.14.0

# 4. Deploy Kafka/Redpanda
helm install redpanda redpanda/redpanda -n kafka --create-namespace

# 5. Deploy TeamFlow via Helm
helm install teamflow ./helm/teamflow \
  --namespace teamflow-production \
  --create-namespace \
  --values helm/teamflow/values-production.yaml

# 6. Verify deployment
kubectl get pods -n teamflow-production
kubectl get ingress -n teamflow-production
```

**See Also:**
- [DEPLOYMENT-TROUBLESHOOTING.md](./docs/DEPLOYMENT-TROUBLESHOOTING.md) - Common issues and solutions
- [EXTERNAL-SERVICES-SETUP.md](./docs/EXTERNAL-SERVICES-SETUP.md) - External service configuration

---

## Deployment Links

| Service | URL | Status |
|---------|-----|--------|
| **Frontend** | [teamflow-crm.vercel.app](https://teamflow-crm.vercel.app) | ✅ Live |
| **Backend** | [hf.space/spaces/mrowais/...](https://huggingface.co/spaces/mrowais/teamflow-backend) | ✅ Live |
| **Demo Video** | [YouTube: TeamFlow Demo](https://youtube.com) | 🎬 Watch |

---

## Local Kubernetes Deployment

**NEW: Deploy TeamFlow locally with Docker, Minikube, and Helm!**

For a complete cloud-native development experience, you can now run the entire TeamFlow stack locally using Kubernetes. Perfect for development, testing, and learning cloud-native patterns.

### Prerequisites

| Software | Purpose | Installation Check |
|----------|---------|-------------------|
| **Docker Desktop** | Container runtime | `docker --version` |
| **Minikube** | Local K8s cluster | `~/.local/bin/minikube version` |
| **Helm** | K8s package manager | `~/.local/bin/helm version` |
| **WSL2** | Linux environment (Windows) | `wsl --version` |

### Quick Start

**1. Start Minikube**
```bash
~/.local/bin/minikube start --driver=docker --cpus=4 --memory=6000
```

**2. Build Docker Images**
```bash
# Frontend
docker.exe build --no-cache --build-arg NEXT_PUBLIC_API_URL="" \
  -t teamflow/frontend:minikube \
  -f teamflow-web/frontend/Dockerfile \
  teamflow-web/frontend/

# Backend
docker.exe build --no-cache \
  -t teamflow/backend:latest \
  -f teamflow-web/backend/Dockerfile \
  teamflow-web/backend/
```

**3. Load Images into Minikube**
```bash
docker.exe save teamflow/frontend:minikube teamflow/backend:latest | \
  (eval "$(minikube docker-env)" && docker load)
```

**4. Deploy with Helm**
```bash
# Create namespace
~/.local/bin/kubectl create namespace teamflow --dry-run=client -o yaml | \
  ~/.local/bin/kubectl apply -f -

# Deploy
~/.local/bin/helm install teamflow ./helm/teamflow --namespace teamflow
```

**5. Access the Application**
```bash
~/.local/bin/minikube service teamflow-frontend -n teamflow
```

Then open the URL shown in your browser (e.g., `http://127.0.0.1:46615`).

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Your Browser                            │
│                  http://127.0.0.1:46615/                       │
└──────────────────────┬──────────────────────────────────────┘
                       │ Minikube Service Tunnel
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  Frontend Pod (Next.js)                                      │
│  → Port: 3000                                               │
│  → Replicas: 2                                              │
│  → API Proxy: /api/[...path]/route.ts                       │
└──────────────────────────┬────────────────────────────────┘
                           │ /api/v1/* (internal K8s DNS)
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Backend Pod (FastAPI)                                     │
│  → Port: 8000                                              │
│  → Replicas: 2                                             │
│  → MCP Server: /mcp/*                                      │
└──────────────────────────┬────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Neon PostgreSQL (External Cloud Database)                    │
└─────────────────────────────────────────────────────────────┘
```

### Common Commands

```bash
# Check pod status
~/.local/bin/kubectl get pods -n teamflow

# View logs
~/.local/bin/kubectl logs -f deployment/teamflow-backend -n teamflow

# Restart services
~/.local/bin/kubectl rollout restart deployment teamflow-frontend -n teamflow

# Scale replicas
~/.local/bin/kubectl scale deployment teamflow-backend -n teamflow --replicas=3

# Stop Minikube
~/.local/bin/minikube stop
```

### For Complete Documentation

See [LOCAL-DEV-GUIDE.md](./LOCAL-DEV-GUIDE.md) for:
- Detailed setup instructions
- Development workflow
- Troubleshooting guide
- All kubectl/Helm commands
- AIOps tools (kubectl-ai, Docker Gordon, Kagent)

---

## Project Structure

```
Hackathon II/
├── 001-console-task-distribution/    # Phase 1: CLI application
│   ├── src/                          # Source code
│   ├── tests/                        # Unit tests
│   └── pyproject.toml                # Python project config
│
├── teamflow-web/                     # Phase 2, 3 & 5: Full-stack + AI + Cloud
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
│   │   │   │   ├── chat/             # ChatKit integration
│   │   │   │   ├── tasks/            # Task components (Phase 5)
│   │   │   │   └── notifications/    # Reminder settings (Phase 5)
│   │   │   ├── hooks/                # React hooks
│   │   │   │   ├── useRealtimeTasks.ts  # Real-time updates (Phase 5)
│   │   │   │   └── useTaskEvents.ts     # WebSocket events (Phase 5)
│   │   │   ├── services/
│   │   │   │   └── websocket.ts      # WebSocket client (Phase 5)
│   │   │   └── lib/                  # Utilities, API clients
│   │   ├── public/                   # Static assets
│   │   └── package.json
│   │
│   ├── backend/                      # FastAPI application
│   │   ├── app/
│   │   │   ├── api/endpoints/        # Auth, tasks, projects
│   │   │   ├── chatkit/              # MCP server (21 tools)
│   │   │   ├── dapr/                 # Dapr integration (Phase 5)
│   │   │   ├── models/               # SQLModel schemas
│   │   │   ├── services/             # Business logic
│   │   │   │   ├── event_publisher.py      # Event publishing (Phase 5)
│   │   │   │   ├── recurrence_calculator.py # Recurring tasks (Phase 5)
│   │   │   │   ├── reminder_scheduler.py    # Reminders (Phase 5)
│   │   │   │   └── task_service.py         # Task CRUD
│   │   │   └── main.py               # FastAPI entry
│   │   ├── microservices/            # Phase 5: Event-driven microservices
│   │   │   ├── notification_service/    # SendGrid email notifications
│   │   │   ├── recurring_task_service/  # Recurring task generation
│   │   │   └── realtime_sync_service/   # WebSocket real-time sync
│   │   ├── alembic/                  # Database migrations
│   │   ├── tests/                    # Pytest tests
│   │   ├── Dockerfile                # Container image
│   │   └── pyproject.toml
│   │
│   └── README.md                     # Web-specific docs
│
├── helm/                             # Phase 4 & 5: Kubernetes Helm charts
│   └── teamflow/
│       ├── Chart.yaml                # Chart metadata
│       ├── values.yaml               # Configuration (gitignored)
│       ├── values-staging.yaml       # Staging environment
│       ├── values-production.yaml    # Production environment
│       ├── charts/                   # Sub-charts for microservices
│       │   ├── notification-service/
│       │   ├── recurring-task-service/
│       │   └── realtime-sync-service/
│       └── templates/                # K8s resource templates
│           ├── deployment.yaml       # Deployments
│           ├── service.yaml          # Services
│           ├── ingress.yaml          # Ingress with WebSocket support
│           ├── configmap.yaml        # ConfigMaps
│           └── _helpers.tpl          # Template helpers
│
├── dapr-components/                  # Phase 5: Dapr component configurations
│   ├── kafka-pubsub.yaml             # Pub/Sub component
│   ├── state-postgresql.yaml         # State store
│   └── secret-kubernetes.yaml        # Secret store
│
├── k8s/                              # Phase 5: Additional K8s manifests
│   ├── redpanda/                     # Kafka/Redpanda deployment
│   └── cert-manager/                 # TLS certificate management
│
├── docs/                             # Phase 5: Documentation
│   ├── DEPLOYMENT-TROUBLESHOOTING.md # Common deployment issues
│   ├── AIOPS-COMMANDS-USED.md        # AI operations documentation
│   └── EXTERNAL-SERVICES-SETUP.md    # External service configuration
│
├── specs/                            # Feature specifications
│   ├── 001-console-task-distribution/
│   ├── 002-fullstack-web-crm/
│   ├── 001-ai-chatbot/
│   └── 005-advanced-cloud-deployment/ # Phase 5 spec
│
├── .claude/                          # Claude Code configuration
│   ├── skills/                       # Reusable agent skills
│   ├── commands/                     # Slash commands
│   └── agents/                       # Subagent definitions
│
├── social-media-posts/               # LinkedIn announcements
├── .github/workflows/                # CI/CD pipelines
│   └── phase5-cloud-deploy.yml       # Phase 5 CI/CD
├── LOCAL-DEV-GUIDE.md                # Local K8s deployment guide
├── README_DEPLOYMENT.md              # Deployment documentation
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
- [Docker](https://www.docker.com/) - Container runtime
- [Kubernetes](https://kubernetes.io/) - Container orchestration
- [Helm](https://helm.sh/) - Kubernetes package manager
- [Minikube](https://minikube.sigs.k8s.io/) - Local K8s cluster
- [Dapr](https://dapr.io) - Distributed application runtime
- [Redpanda](https://redpanda.com) - Kafka-compatible event streaming
- [Oracle OKE](https://www.oracle.com/cloud/) - Kubernetes cloud hosting
- [cert-manager](https://cert-manager.io) - TLS certificate automation
- [SendGrid](https://sendgrid.com) - Email delivery
- [kubectl-ai](https://github.com/kubectl-ai/kubectl-ai) - AI-assisted K8s operations

---

**Built with ❤️ using Next.js 16, FastAPI, Docker, Kubernetes, and modern AI technologies**
