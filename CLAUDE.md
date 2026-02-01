# Claude Code Rules - TeamFlow Hackathon

This file is the primary instruction set for Claude Code agents working on the TeamFlow project.

You are an expert AI assistant specializing in **Spec-Driven Development (SDD)** and **Cloud-Native Deployment**. Your primary goal is to work with the developer to build and deploy the TeamFlow application across all hackathon phases.

---

## Before ANY Work: Context First

**STOP. Before executing, complete this protocol:**

1. **Identify work type**: 
   - **Application** (frontend/backend code)
   - **Infrastructure** (Docker, K8s, Helm, Dapr)
   - **AI/Agent** (MCP, OpenAI Agents, ChatKit)
   - **Skills** (creating reusable agent skills)

2. **For infrastructure/deployment work**, read these files FIRST:
   - `phase 4-5 plan.md` → Deployment requirements, architecture
   - `CLOUD-NATIVE-LEARNING-GUIDE.md` → Technology concepts
   - `CLAUDE-SKILLS-GUIDE.md` → How to create/use skills

3. **Determine phase**:
   - Phase I: Console CLI (Python, Typer)
   - Phase II: Full-Stack Web (Next.js, FastAPI, Neon DB)
   - Phase III: AI Chatbot (OpenAI Agents, MCP, ChatKit)
   - **Phase IV: Local Kubernetes** (Docker, Minikube, Helm, kubectl-ai, Gordon)
   - **Phase V: Cloud Deploy** (Dapr, Kafka, AKS/GKE, CI/CD)

4. **State your understanding** and get user confirmation before proceeding

**Why this matters**: Skipping context causes wrong implementations and wasted iterations.

---

## Critical Rules

1. **Investigate before acting** - NEVER edit files you haven't read
2. **Parallel tool calls** - Run independent operations simultaneously
3. **Default to action** - Implement rather than suggest
4. **Skills over repetition** - Pattern recurs 2+? Create a skill
5. **Absolute paths for subagents** - Never let agents infer directories
6. **Use existing skills FIRST** - Check `.claude/skills/` before implementing

---

## Available Skills (USE THESE FIRST!)

**ALWAYS check existing skills BEFORE any implementation.**

### Cloud-Native & Deployment Skills
| Skill | Location | Use When |
|-------|----------|----------|
| `deployment-engineer` | `.claude/skills/deployment-engineer/` | CI/CD, Docker, K8s, HuggingFace deployment |
| `cli-deployment` | `.claude/skills/cli-deployment/` | CLI app deployment patterns |
| `cloud-native-blueprints` | `.claude/skills/cloud-native-blueprints/` | K8s, Helm, Dapr, Kafka patterns |

### AI & Agent Development Skills
| Skill | Location | Use When |
|-------|----------|----------|
| `openai-agents-sdk-gemini` | `.claude/skills/openai-agents-sdk-gemini/` | OpenAI Agents + MCP integration |
| `openai-chatkit-integration` | `.claude/skills/openai-chatkit-integration/` | ChatKit UI for chatbots |
| `chatbot-widget-creator` | `.claude/skills/chatbot-widget-creator/` | Embeddable chat widgets |
| `mcp-builder` | `.claude/skills/mcp-builder/` | Building MCP servers |

### Full-Stack Development Skills
| Skill | Location | Use When |
|-------|----------|----------|
| `better-auth-integration` | `.claude/skills/better-auth-integration/` | Authentication with Better Auth |
| `building-nextjs-apps` | `.claude/skills/building-nextjs-apps/` | Next.js application patterns |
| `neon-postgresql` | `.claude/skills/neon-postgresql/` | Neon DB setup and queries |
| `frontend-designer` | `.claude/skills/frontend-designer/` | UI/UX design patterns |
| `theme-factory` | `.claude/skills/theme-factory/` | Theming and styling |
| `ux-evaluator` | `.claude/skills/ux-evaluator/` | UX evaluation and feedback |

### Meta Skills
| Skill | Location | Use When |
|-------|----------|----------|
| `skill-creator-pro` | `.claude/skills/skill-creator-pro/` | Creating new reusable skills |
| `skill-validator` | `.claude/skills/skill-validator/` | Validating skill quality |
| `console-cli-builder` | `.claude/skills/console-cli-builder/` | Building CLI applications |

### Content & Documentation
| Skill | Location | Use When |
|-------|----------|----------|
| `book-content-writer` | `.claude/skills/book-content-writer/` | Technical writing |
| `book-structure-generator` | `.claude/skills/book-structure-generator/` | Documentation structure |
| `social-media-writer` | `.claude/skills/social-media-writer/` | Marketing content |
| `rag-pipeline-builder` | `.claude/skills/rag-pipeline-builder/` | RAG implementations |

### Additional Skills
| Skill | Location | Use When |
|-------|----------|----------|
| `gemini-frontend-assistant` | `.claude/skills/gemini-frontend-assistant/` | Gemini AI frontend patterns |
| `ai-collaborate-teaching` | `.claude/skills/ai-collaborate-teaching/` | AI teaching/learning patterns |
| `skills-proficiency-mapper` | `.claude/skills/skills-proficiency-mapper/` | Mapping skill proficiency levels |

---

## CLOUD-NATIVE ENGINEERING PROTOCOL (Phase IV & V)

**Before implementing ANY cloud-native feature, complete this research protocol:**

### 1. Research Existing Solutions (MANDATORY)

**Use tavily MCP for research:**
```bash
# Via tavily MCP tool
tavily search "Docker multi-stage build FastAPI optimization 2025"
tavily search "Helm chart Next.js Kubernetes best practices"
tavily search "Dapr pub/sub Kafka configuration tutorial"
```

**Alternative: WebSearch**
```
WebSearch: "[technology] [feature] best practices 2025"
```
**Why**: Avoids reinventing wheels and ensures production-ready patterns.

### 2. Technology Decision Matrix

| Technology | Purpose | When to Use |
|------------|---------|-------------|
| **Docker** | Containerization | Package apps with dependencies |
| **Docker Gordon** | AI-assisted Docker | Dockerfile optimization, troubleshooting |
| **Minikube** | Local K8s | Development and testing |
| **kubectl-ai** | AI-assisted K8s | Natural language K8s operations |
| **Kagent** | K8s analysis | Cluster health, resource optimization |
| **Helm** | K8s packaging | Templated deployments, releases |
| **Dapr** | Distributed runtime | Pub/Sub, state, secrets, service invocation |
| **Kafka/Redpanda** | Event streaming | Async messaging, event-driven architecture |

### 3. Edge Case Brainstorm (MANDATORY)
Before writing infrastructure code, list potential failures:

| Category | Questions to Ask |
|----------|------------------|
| **Resources** | What CPU/memory limits? What happens if exceeded? |
| **Networking** | CORS? SSL? Service discovery? |
| **Secrets** | How are secrets passed? K8s secrets? Dapr? |
| **Scaling** | HPA configured? Min/max replicas? |
| **Health** | Liveness/readiness probes configured? |
| **Storage** | Persistent volumes needed? Volume mounts? |
| **Rollback** | How to revert failed deployment? |

### 4. Implementation Checklist (Cloud-Native)
```
□ Dockerfile uses multi-stage build
□ Image size optimized (no dev dependencies in prod)
□ Health check endpoint exists (/health)
□ Environment variables externalized
□ Secrets not hardcoded
□ Resource limits defined (CPU, memory)
□ Helm values.yaml is environment-agnostic
□ Tested on Minikube before cloud deployment
```

### 5. AIOps Commands Reference

**kubectl-ai (Natural Language K8s):**
```bash
# Basic deployments
kubectl-ai "deploy backend with 2 replicas exposing port 8000"
kubectl-ai "create HPA for frontend when CPU > 70%"
kubectl-ai "why are the pods in pending state"
kubectl-ai "show me resource usage in teamflow namespace"

# Phase 5: Microservices
kubectl-ai "deploy notification service with Dapr sidecar"
kubectl-ai "create deployment for realtime-sync-service without Dapr"
kubectl-ai "add sticky session annotations to ingress for WebSocket"

# Phase 5: Kafka & Dapr
kubectl-ai "show me Dapr components in teamflow namespace"
kubectl-ai "verify Kafka topics exist in Redpanda"
kubectl-ai "check Dapr sidecar health status"

# Phase 5: Troubleshooting
kubectl-ai "why is WebSocket connection dropping"
kubectl-ai "show me pods with OOMKilled status"
kubectl-ai "check if cert-manager is issuing certificates"
```

**Docker Gordon (AI Docker Assistance):**
```bash
docker ai "optimize this Dockerfile for smaller size"
docker ai "what's wrong with this Dockerfile"
docker ai "create docker-compose for local development"

# Phase 5: Multi-stage builds
docker ai "create multi-stage Dockerfile for FastAPI with Dapr CLI"
docker ai "optimize Docker layer caching for faster builds"
```

**Kagent (Cluster Analysis):**
```bash
kagent "analyze cluster resource utilization"
kagent "suggest optimizations for production"
kagent "show me pods with high memory usage"
kagent "what are the bottlenecks in my application"
```

---

## Dapr Integration Patterns

### Building Blocks Used in TeamFlow

| Block | Component Type | Configuration |
|-------|----------------|---------------|
| **Pub/Sub** | `pubsub.kafka` | Kafka/Redpanda for events |
| **State** | `state.postgresql` | Neon DB for state |
| **Secrets** | `secretstores.kubernetes` | K8s secrets |
| **Bindings** | `bindings.cron` | Scheduled jobs |
| **Service Invocation** | Built-in | mTLS between services |

### Publishing Events (FastAPI + Dapr)
```python
import httpx

DAPR_PORT = 3500

async def publish_event(topic: str, data: dict):
    await httpx.post(
        f"http://localhost:{DAPR_PORT}/v1.0/publish/kafka-pubsub/{topic}",
        json=data
    )
```

### Subscribing to Events
```python
@app.get("/dapr/subscribe")
async def subscribe():
    return [
        {"pubsubname": "kafka-pubsub", "topic": "task-events", "route": "/events/tasks"}
    ]

@app.post("/events/tasks")
async def handle_task_event(data: dict):
    # Process event
    return {"status": "SUCCESS"}
```

### Kafka Topics Used in TeamFlow
| Topic | Purpose | Publisher | Subscribers |
|-------|---------|-----------|-------------|
| `task-events` | Task CRUD events | Backend | Notification Service, Realtime Sync |
| `reminders` | Due date reminders | Reminder Scheduler | Notification Service |
| `task-updates` | Real-time changes | Backend | Realtime Sync Service |
| `time-logged` | Time tracking events | Time Service | Analytics Service (future) |

---

## WebSocket Integration (Phase 5)

**IMPORTANT: WebSocket services do NOT use Dapr sidecar** - Dapr does not support WebSocket proxying.

### Realtime Sync Service Pattern
```python
from fastapi import WebSocket
from app.dapr.connection_manager import ConnectionManager

connection_manager = ConnectionManager()

@app.websocket("/ws/tasks")
async def websocket_tasks_endpoint(websocket: WebSocket):
    # JWT authentication
    token = websocket.query_params.get("token")
    token_data = decode_jwt_token(token)

    # Register connection
    await connection_manager.register(connection_id, user_id, agency_id, websocket)

    try:
        while True:
            # Keep connection alive with ping/pong
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        connection_manager.disconnect(connection_id)
```

### WebSocket Client with Auto-Reconnect
```typescript
export class TaskEventStream extends EventEmitter {
  private reconnectDelay: number = 1000;  // Start with 1s
  private maxReconnectDelay: number = 30000;  // Max 30s

  private scheduleReconnect(): void {
    const delay = Math.min(this.reconnectDelay, this.maxReconnectDelay);
    this.reconnectTimer = setTimeout(() => {
      this.connect();
      this.reconnectDelay = Math.min(this.reconnectDelay * 2, this.maxReconnectDelay);
    }, delay);
  }
}
```

### Ingress Configuration for WebSocket
```yaml
annotations:
  nginx.ingress.kubernetes.io/websocket-services: "realtime-sync-service"
  nginx.ingress.kubernetes.io/affinity: "cookie"
  nginx.ingress.kubernetes.io/session-cookie-name: "route"
  nginx.ingress.kubernetes.io/proxy-read-timeout: "3600"
  nginx.ingress.kubernetes.io/proxy-send-timeout: "3600"
```

---

## CI/CD Pipeline (Phase 5)

### GitHub Actions Workflow Structure
```yaml
# .github/workflows/phase5-cloud-deploy.yml
jobs:
  build-test:        # Run tests, upload coverage
  security-scan:     # Trivy vulnerability scan
  build-images:      # Build & push to GHCR
  deploy-staging:    # Deploy to staging via Helm
  integration-tests: # Playwright E2E tests
  deploy-production: # Manual approval gate
```

### Deployment Commands (used in CI/CD)
```bash
# Staging deployment
helm upgrade --install teamflow ./helm/teamflow \
  --namespace teamflow-staging \
  --create-namespace \
  --values helm/teamflow/values-staging.yaml \
  --set image.backend.tag=${GITHUB_SHA} \
  --set image.frontend.tag=${GITHUB_SHA} \
  --wait --timeout 10m

# Production deployment (manual approval)
helm upgrade --install teamflow ./helm/teamflow \
  --namespace teamflow-production \
  --create-namespace \
  --values helm/teamflow/values-production.yaml \
  --set image.backend.tag=${GITHUB_SHA} \
  --set image.frontend.tag=${GITHUB_SHA} \
  --wait --timeout 10m
```

---

## Production Deployment (Oracle OKE)

### Oracle OKE Always Free Limits
| Resource | Limit | Usage |
|----------|-------|-------|
| OCPUs | 4 total | Backend: 1-2, Frontend: 0.5-1, Microservices: 1 |
| RAM | 24GB total | Backend: 1GB, Frontend: 512MB, each microservice: 256MB |
| Storage | 2x 50GB Block Volumes | Not needed (using Neon PostgreSQL) |

### Pre-Deployment Checklist
```
□ Dapr installed on cluster: dapr init -k --runtime-version 1.14.0
□ Kafka/Redpanda deployed: helm install redpanda redpanda/redpanda -n kafka
□ Topics created: kubectl exec -it redpanda-0 -n kafka -- rpk topic create task-events
□ GHCR credentials secret created
□ Database migrations run: kubectl exec -it deployment/teamflow-backend -- alembic upgrade head
□ Cert-manager installed for TLS
□ Ingress DNS configured
```

### Production Deployment Steps
```bash
# 1. Create namespace
kubectl create namespace teamflow-production

# 2. Create secrets
kubectl create secret generic teamflow-secrets \
  --from-literal=database-url="$DATABASE_URL" \
  --from-literal=jwt-secret="$JWT_SECRET" \
  --from-literal=sendgrid-api-key="$SENDGRID_API_KEY" \
  --namespace=teamflow-production

# 3. Deploy
helm install teamflow ./helm/teamflow \
  --namespace teamflow-production \
  --values helm/teamflow/values-production.yaml

# 4. Verify
kubectl get pods -n teamflow-production
kubectl get ingress -n teamflow-production
```

---

## Failure Prevention

**These patterns caused real failures. Don't repeat them:**

### Infrastructure Failures
- ❌ Missing `output: 'standalone'` in Next.js config → Docker build fails
- ❌ Not copying README.md before pip install → hatchling error
- ❌ Hardcoded secrets in Dockerfile → Security vulnerability
- ❌ Missing health check endpoints → K8s can't verify pod health
- ❌ Resource limits too low → OOM kills in production
- ❌ Skipping Minikube testing → Cloud deployment surprises
- ❌ **Using Dapr sidecar with WebSocket** → Connections fail, use direct pod access

### Deployment Failures
- ❌ Not using `pool_pre_ping=True` for Neon PostgreSQL → Connection closed errors
- ❌ Using sync SQLAlchemy patterns with AsyncSession → `query` attribute error
- ❌ Missing CORS configuration for cross-origin requests → Frontend can't call backend
- ❌ Branch name mismatch in GitHub Actions (`main` vs `master`)
- ❌ **Missing sticky sessions for WebSocket** → Connections drop on pod restart
- ❌ **Not setting WebSocket timeout annotations** → 60s default closes long connections

### Phase 5 Specific Issues
- ❌ **Dapr pub/sub not receiving events** → Check Kafka topic creation, component configuration
- ❌ **WebSocket JWT authentication failing** → Verify token is passed as query param
- ❌ **Reminders not sending** → Check SendGrid API key, topic subscription, cron schedule
- ❌ **Real-time updates not working** → Verify NO Dapr sidecar on realtime-sync-service
- ❌ **Certificate errors in production** → Install cert-manager, create ClusterIssuer

### Prevention Protocol
1. Always read existing code before modifying
2. Use existing skills when available
3. Test locally with Docker/Minikube before cloud
4. Document all AIOps commands used (for hackathon submission)

---

## Project Structure

```
teamflow-web/
├── frontend/                 # Next.js application
│   ├── src/
│   ├── package.json
│   └── Dockerfile           # NEW: Create for Phase IV
├── backend/                  # FastAPI application
│   ├── app/
│   ├── pyproject.toml
│   └── Dockerfile           # EXISTS: Optimize for Phase IV
├── helm/                     # NEW: Helm charts
│   └── teamflow/
└── dapr-components/          # NEW: Dapr configuration

specs/                        # Feature specifications
├── 001-ai-chatbot/
└── 002-fullstack-web-crm/

.claude/
├── agents/                   # Subagent definitions
├── commands/                 # Slash commands
└── skills/                   # Reusable skills (20+ available)

.specify/
└── memory/constitution.md    # Project principles

history/prompts/              # Prompt History Records
```

---

## Development Guidelines

### 1. Mandatory Documentation Lookup (NON-NEGOTIABLE)
**BEFORE implementing any code**, use MCP tools for research:

**For Library/Framework Docs:**
```
context7 resolve-library-id → get-library-docs
```

**For General Research (Best Practices, Tutorials, Examples):**
```
tavily search "[topic] best practices 2025"
tavily search "[technology] deployment tutorial"
```

- NEVER assume syntax from internal knowledge
- ALWAYS verify current version's best practices
- Use **tavily MCP** for web research on patterns, troubleshooting, and latest trends

### 2. Skills-First Development
```
IF task matches existing skill:
    1. Read skill SKILL.md first
    2. Follow skill patterns exactly
    3. Use skill assets/templates
ELSE IF pattern recurs 2+ times:
    1. Create new skill in .claude/skills/
    2. Use skill-creator-pro skill for guidance
```

### 3. Human as Tool Strategy
Invoke the user when encountering:
- Ambiguous requirements
- Multiple valid approaches with tradeoffs
- Cloud provider selection (AKS vs GKE vs OKE)
- Architectural decisions

---

## Hackathon Phase Requirements

### Phase IV (250 pts) - Local Kubernetes
| Requirement | How to Fulfill |
|-------------|----------------|
| Containerize with Gordon | Use `docker ai` commands, document them |
| Create Helm charts | Use kubectl-ai/kagent to generate |
| Use kubectl-ai | Document all natural language commands |
| Use Kagent | Document cluster analysis |
| Deploy on Minikube | Test full stack locally |

### Phase V (300 pts) - Cloud Deploy
| Requirement | How to Fulfill |
|-------------|----------------|
| Dapr Pub/Sub | Configure `pubsub.kafka` component |
| Dapr State | Configure `state.postgresql` component |
| Dapr Secrets | Configure `secretstores.kubernetes` |
| Dapr Bindings | Configure `bindings.cron` for reminders |
| Kafka | Deploy Redpanda or Strimzi |
| Cloud (AKS/GKE/OKE) | Same Helm charts, cloud cluster |
| CI/CD | GitHub Actions workflow |

### Bonus Points Opportunities
| Bonus | Points | How to Achieve |
|-------|--------|----------------|
| Cloud-Native Blueprints | +200 | Create K8s/Dapr skills in `.claude/skills/` |
| Reusable Intelligence | +200 | Create subagents for deployment |
| Multi-language (Urdu) | +100 | Add Urdu to chatbot |
| Voice Commands | +200 | Web Speech API integration |

---

## Quick Commands

```bash
# Minikube
minikube start --cpus=4 --memory=8192
minikube dashboard
minikube service teamflow-frontend -n teamflow

# Docker
docker build -t teamflow/backend:latest .
docker ai "optimize this Dockerfile"

# Helm
helm install teamflow ./helm/teamflow -n teamflow --create-namespace
helm upgrade teamflow ./helm/teamflow -n teamflow

# kubectl-ai
kubectl-ai "deploy backend with 2 replicas"
kubectl-ai "why are pods pending"

# Dapr
dapr init -k
dapr status -k
```

---

## PHR Documentation

After completing significant work, create Prompt History Record:
```bash
.specify/scripts/bash/create-phr.sh --title "<title>" --stage <stage> --json
```
Stages: spec | plan | tasks | general

---

## Active Technologies

| Phase | Technologies |
|-------|--------------|
| Phase I | Python 3.13+, Typer, Rich, Pydantic |
| Phase II | Next.js, FastAPI, SQLModel, Neon PostgreSQL, Better Auth |
| Phase III | OpenAI Agents SDK, MCP SDK, ChatKit |
| **Phase IV** | Docker, Minikube, Helm, kubectl-ai, Kagent, Gordon |
| **Phase V** | Dapr, Kafka/Redpanda, AKS/GKE/OKE, GitHub Actions |

---

## Code Standards

See `.specify/memory/constitution.md` for:
- Code quality principles
- Testing requirements
- Performance standards
- Security requirements
- Architecture patterns

---

## Phase 5 Documentation

For detailed Phase 5 information, see:

| Document | Purpose | Location |
|----------|---------|----------|
| **Deployment Troubleshooting** | Common deployment issues and solutions | `docs/DEPLOYMENT-TROUBLESHOOTING.md` |
| **AIOps Commands Used** | All kubectl-ai, Docker Gordon, Tavily commands | `docs/AIOPS-COMMANDS-USED.md` |
| **External Services Setup** | Neon, SendGrid, GitHub, Oracle Cloud setup | `docs/EXTERNAL-SERVICES-SETUP.md` |
| **Production Values** | Oracle OKE Always Free configuration | `helm/teamflow/values-production.yaml` |
| **Staging Values** | Pre-production environment config | `helm/teamflow/values-staging.yaml` |
| **Dapr Components** | Kafka pub/sub, state store, secrets | `dapr-components/` |
| **CI/CD Workflow** | GitHub Actions deployment pipeline | `.github/workflows/phase5-cloud-deploy.yml` |

---

## Quick Diagnosis Commands (Phase 5)

```bash
# Check all pods in namespace
kubectl get pods -n teamflow

# Check pod logs for errors
kubectl logs -l app=teamflow-backend -n teamflow --tail=50

# Describe pod for detailed status
kubectl describe pod <pod-name> -n teamflow

# Check recent events
kubectl get events -n teamflow --sort-by='.lastTimestamp'

# Verify Dapr components
kubectl get components -n teamflow

# Check Kafka topics
kubectl exec -it redpanda-0 -n kafka -- rpk topic list

# Test database connectivity
kubectl exec -it deployment/teamflow-backend -n teamflow -- python -c "
import asyncio
from app.database import engine
asyncio.run(engine.connect())
print('Database OK')
"

# Check Dapr sidecar status
kubectl get pods -n teamflow -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[*].name}{"\n"}{end}'

# View HPA status
kubectl get hpa -n teamflow

# Check ingress TLS certificate
kubectl get secret teamflow-tls -n teamflow -o yaml
```
