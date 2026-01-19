# TeamFlow Phase 4 & 5 Deployment Plan
## Cloud-Native Deployment with Docker, Kubernetes, Dapr, and Kafka

---

## Executive Summary

This comprehensive plan outlines the steps to deploy TeamFlow (your agency task management system) on **Kubernetes** with **Dapr** and **Kafka** for an event-driven architecture. The plan covers both **Phase IV** (local Minikube deployment) and **Phase V** (cloud deployment on AKS/GKE/OKE with advanced features).

Your TeamFlow project already has a solid foundation:
- **Frontend**: Next.js application in `teamflow-web/frontend`
- **Backend**: FastAPI application in `teamflow-web/backend` (with existing Dockerfile)
- **Database**: Neon PostgreSQL (external, already configured)

---

## ✅ Hackathon Requirements Compliance Checklist

### Phase IV Requirements (250 pts) - Due: Jan 18, 2026

| Requirement | Status | Task ID | Notes |
|-------------|--------|---------|-------|
| **Containerize frontend and backend (Use Gordon)** | ⬜ | T401-T403 | Docker AI for Dockerfile optimization |
| **Use Docker AI Agent (Gordon)** for AI-assisted Docker ops | ⬜ | T408 | Document commands used |
| **Create Helm charts for deployment** | ⬜ | T404 | Use kubectl-ai/kagent to generate |
| **Use kubectl-ai** for AI-assisted K8s operations | ⬜ | T408 | Document all commands |
| **Use Kagent** for cluster analysis | ⬜ | T408 | Document usage |
| **Deploy on Minikube locally** | ⬜ | T406-T407 | Full stack deployment |

### Phase V Requirements (300 pts) - Due: Jan 18, 2026

#### Part A: Advanced Features
| Requirement | Status | Task ID | Notes |
|-------------|--------|---------|-------|
| **Recurring Tasks** (auto-create next instance) | ⬜ | T508 | Event-driven via Kafka |
| **Due Dates & Reminders** (browser notifications) | ⬜ | T507, T509 | Dapr Jobs API |
| **Priorities & Tags/Categories** | ⬜ | Already in Phase 2 | Verify implementation |
| **Search & Filter** | ⬜ | Already in Phase 2 | Verify implementation |
| **Sort Tasks** | ⬜ | Already in Phase 2 | Verify implementation |

#### Part B: Local Deployment with Dapr
| Requirement | Status | Task ID | Notes |
|-------------|--------|---------|-------|
| **Deploy to Minikube** | ⬜ | T406 | Pre-requisite |
| **Dapr Pub/Sub** (Kafka abstraction) | ⬜ | T501-T503 | Event streaming |
| **Dapr State Management** | ⬜ | T502 | PostgreSQL state store |
| **Dapr Bindings (cron)** | ⬜ | T509 | For scheduled reminders |
| **Dapr Secrets** | ⬜ | T502 | K8s secrets integration |
| **Dapr Service Invocation** | ⬜ | T503 | Frontend → Backend |

#### Part C: Cloud Deployment
| Requirement | Status | Task ID | Notes |
|-------------|--------|---------|-------|
| **Deploy to AKS/GKE/OKE** | ⬜ | T511 | Choose one provider |
| **Full Dapr on Cloud** | ⬜ | T511 | Same as local |
| **Kafka (Confluent/Redpanda Cloud)** | ⬜ | T501 | Or alternative PubSub |
| **CI/CD with GitHub Actions** | ⬜ | T510 | Build + Deploy pipeline |
| **Monitoring and Logging** | ⬜ | T512 | Prometheus/Grafana |

### Submission Requirements
| Requirement | Status | Notes |
|-------------|--------|-------|
| **GitHub Repository** with all source code | ⬜ | Already exists |
| **/specs folder** with specification files | ⬜ | Exists in project |
| **CLAUDE.md** with instructions | ⬜ | Already exists |
| **README.md** with documentation | ⬜ | Update for Phase IV/V |
| **Phase IV: Minikube setup instructions** | ⬜ | Add to README |
| **Phase V: Cloud deployment URL** | ⬜ | After cloud deploy |
| **Demo video (≤90 seconds)** | ⬜ | Record after completion |

### Kafka Use Cases (Required)
| Use Case | Status | Implementation |
|----------|--------|----------------|
| **Reminder/Notification System** | ⬜ | `reminders` topic → Notification Service |
| **Recurring Task Engine** | ⬜ | `task-events` topic → Recurring Task Service |
| **Activity/Audit Log** | ⬜ | `task-events` topic → Audit Service |
| **Real-time Sync Across Clients** | ⬜ | `task-updates` topic → WebSocket Service |

### Bonus Points Opportunities
| Bonus | Points | Status | Notes |
|-------|--------|--------|-------|
| **Reusable Intelligence** (Claude subagents/skills) | +200 | ⬜ | Create K8s deployment skill |
| **Cloud-Native Blueprints** (Agent Skills) | +200 | ⬜ | Helm chart templates |
| **Multi-language (Urdu)** | +100 | ⬜ | Chatbot Urdu support |
| **Voice Commands** | +200 | ⬜ | Web Speech API |

---

## Phase IV: Local Kubernetes Deployment (250 points)

### 4.1 Prerequisites Checklist

| Tool | Version | Purpose |
|------|---------|---------|
| Docker Desktop | 4.53+ | Container runtime |
| Minikube | Latest | Local K8s cluster |
| kubectl | Latest | K8s CLI |
| Helm | 3.x | K8s package manager |
| kubectl-ai | Latest | AI-assisted K8s ops |
| Kagent | Latest | K8s agent analysis |

### 4.2 Containerization Strategy

#### 4.2.1 Backend Dockerfile (Already Exists)

Your backend already has a Dockerfile at `teamflow-web/backend/Dockerfile`. 

> [!IMPORTANT]
> **Review Required**: Verify the existing Dockerfile follows multi-stage build practices for production optimization.

**Recommended Dockerfile Structure:**
```dockerfile
# Stage 1: Build
FROM python:3.13-slim AS builder
WORKDIR /app
COPY pyproject.toml uv.lock ./
COPY README.md ./
RUN pip install uv && uv sync --frozen --no-dev

# Stage 2: Production
FROM python:3.13-slim
WORKDIR /app
COPY --from=builder /app/.venv ./.venv
COPY app/ ./app/
ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 4.2.2 Frontend Dockerfile (Needs Creation)

Create `teamflow-web/frontend/Dockerfile`:

```dockerfile
# Stage 1: Dependencies
FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --legacy-peer-deps

# Stage 2: Build
FROM node:22-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

# Stage 3: Production
FROM node:22-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
USER nextjs
EXPOSE 3000
ENV PORT=3000
CMD ["node", "server.js"]
```

> [!WARNING]
> **Next.js Config Required**: Add `output: 'standalone'` to `next.config.ts` for optimized Docker builds.

### 4.3 Helm Chart Structure

Create the following directory structure:

```
helm/teamflow/
├── Chart.yaml
├── values.yaml
├── templates/
│   ├── _helpers.tpl
│   ├── namespace.yaml
│   ├── configmap.yaml
│   ├── secrets.yaml
│   ├── frontend-deployment.yaml
│   ├── frontend-service.yaml
│   ├── backend-deployment.yaml
│   ├── backend-service.yaml
│   └── ingress.yaml
```

#### Key values.yaml Configuration:

```yaml
namespace: teamflow

frontend:
  replicaCount: 2
  image:
    repository: teamflow/frontend
    tag: latest
  service:
    type: ClusterIP
    port: 3000
  resources:
    limits:
      cpu: 500m
      memory: 512Mi
    requests:
      cpu: 100m
      memory: 128Mi

backend:
  replicaCount: 2
  image:
    repository: teamflow/backend
    tag: latest
  service:
    type: ClusterIP
    port: 8000
  resources:
    limits:
      cpu: 1000m
      memory: 1Gi
    requests:
      cpu: 200m
      memory: 256Mi

env:
  DATABASE_URL: "" # From secret
  OPENAI_API_KEY: "" # From secret
  BETTER_AUTH_SECRET: "" # From secret
```

### 4.4 Minikube Deployment Steps

```bash
# 1. Start Minikube with sufficient resources
minikube start --cpus=4 --memory=8192 --driver=docker

# 2. Enable required addons
minikube addons enable ingress
minikube addons enable metrics-server

# 3. Set Docker env to use Minikube's Docker daemon
eval $(minikube docker-env)

# 4. Build images inside Minikube
cd teamflow-web/backend
docker build -t teamflow/backend:latest .

cd ../frontend
docker build -t teamflow/frontend:latest .

# 5. Deploy using Helm
helm install teamflow ./helm/teamflow --namespace teamflow --create-namespace

# 6. Access the application
minikube service teamflow-frontend --namespace teamflow
```

### 4.5 AIOps Integration

#### kubectl-ai Commands:
```bash
# Deploy with natural language
kubectl-ai "deploy teamflow frontend with 2 replicas exposing port 3000"
kubectl-ai "create a horizontal pod autoscaler for backend when CPU exceeds 70%"
kubectl-ai "check the logs of the backend pods for errors"

# Troubleshooting
kubectl-ai "why are the pods in pending state"
kubectl-ai "show me the resource usage of all teamflow pods"
```

#### Docker AI (Gordon):
```bash
docker ai "optimize the backend Dockerfile for size"
docker ai "create a docker-compose for local development"
docker ai "what's the best way to handle secrets in this container"
```

---

## Phase V: Advanced Cloud Deployment (300 points)

### 5.1 Advanced Features to Implement

| Feature | Description | Priority |
|---------|-------------|----------|
| **Recurring Tasks** | Auto-create next task instance on completion | High |
| **Due Date Reminders** | Push notifications for upcoming deadlines | High |
| **Priorities & Tags** | Categorization and filtering | Medium |
| **Search & Filter** | Full-text search across tasks | Medium |
| **Real-time Sync** | WebSocket updates across clients | Medium |

### 5.2 Event-Driven Architecture with Kafka

#### 5.2.1 Kafka Topics Design

| Topic Name | Producer | Consumers | Purpose |
|------------|----------|-----------|---------|
| `task-events` | Backend API | Audit, Recurring Task, Analytics | All task CRUD operations |
| `reminders` | Scheduler | Notification Service | Due date alerts |
| `time-logged` | Time Tracking | Billing, Dashboard | Profitability updates |
| `team-assignments` | AI Suggestion Engine | Notification Service | Assignment changes |

#### 5.2.2 Event Schemas

**Task Event Schema:**
```json
{
  "event_id": "uuid",
  "event_type": "created|updated|completed|deleted|assigned",
  "task_id": 123,
  "user_id": "user_abc",
  "agency_id": "agency_xyz",
  "project_id": 5,
  "payload": {
    "title": "Task title",
    "status": "doing",
    "assignee_id": "user_def"
  },
  "timestamp": "2026-01-18T12:00:00Z"
}
```

**Reminder Event Schema:**
```json
{
  "event_id": "uuid",
  "task_id": 123,
  "user_id": "user_abc",
  "title": "Finish client report",
  "due_at": "2026-01-20T09:00:00Z",
  "remind_at": "2026-01-19T09:00:00Z",
  "notification_type": "push|email"
}
```

#### 5.2.3 Kafka Deployment Options

**Option A: Redpanda (Recommended for Hackathon)**
- Kafka-compatible, no ZooKeeper needed
- Simpler deployment, lower resource usage
- Free Serverless tier available on Redpanda Cloud

**Option B: Strimzi Operator (Full Kafka)**
- Production-grade Kafka on K8s
- More complex but feature-complete
- Better for learning real Kafka

```bash
# Redpanda on Kubernetes (Local)
helm repo add redpanda https://charts.redpanda.com
helm install redpanda redpanda/redpanda --namespace kafka --create-namespace

# OR Strimzi for Apache Kafka
kubectl create namespace kafka
kubectl apply -f https://strimzi.io/install/latest?namespace=kafka
```

### 5.3 Dapr Integration

#### 5.3.1 Dapr Building Blocks Used

| Building Block | Use Case | Configuration |
|----------------|----------|---------------|
| **Pub/Sub** | Kafka event streaming | `pubsub.kafka` |
| **State Management** | Conversation history | `state.postgresql` |
| **Service Invocation** | Frontend → Backend | Built-in with mTLS |
| **Secrets** | API keys, DB creds | `secretstores.kubernetes` |
| **Jobs API** | Scheduled reminders | `jobs/scheduler` |

#### 5.3.2 Dapr Component Files

**kafka-pubsub.yaml:**
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
  namespace: teamflow
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "redpanda:9092"
    - name: consumerGroup
      value: "teamflow-services"
    - name: authType
      value: "none"  # Use SASL for production
```

**state-store.yaml:**
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
  namespace: teamflow
spec:
  type: state.postgresql
  version: v1
  metadata:
    - name: connectionString
      secretKeyRef:
        name: teamflow-secrets
        key: DATABASE_URL
```

**secrets-store.yaml:**
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kubernetes-secrets
  namespace: teamflow
spec:
  type: secretstores.kubernetes
  version: v1
```

#### 5.3.3 Backend Code Changes for Dapr

**Publishing Events via Dapr:**
```python
import httpx
from datetime import datetime

DAPR_HTTP_PORT = 3500

async def publish_task_event(event_type: str, task_id: int, user_id: str, payload: dict):
    """Publish task event via Dapr PubSub (no Kafka client needed)."""
    async with httpx.AsyncClient() as client:
        await client.post(
            f"http://localhost:{DAPR_HTTP_PORT}/v1.0/publish/kafka-pubsub/task-events",
            json={
                "event_type": event_type,
                "task_id": task_id,
                "user_id": user_id,
                "payload": payload,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
```

**Subscribing to Events:**
```python
from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/api/events/task-events")
async def handle_task_event(request: Request):
    """Dapr calls this endpoint when task events are received."""
    event = await request.json()
    
    if event["event_type"] == "completed":
        # Check if task is recurring, create next instance
        await create_next_recurring_task(event["task_id"])
    
    return {"status": "SUCCESS"}

# Dapr subscription configuration
@app.get("/dapr/subscribe")
async def subscribe():
    return [
        {
            "pubsubname": "kafka-pubsub",
            "topic": "task-events",
            "route": "/api/events/task-events"
        }
    ]
```

### 5.4 Microservices Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                       KUBERNETES CLUSTER (AKS/GKE/OKE)                        │
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │                         FRONTEND SERVICE                                 │ │
│  │  ┌───────────────┐ ┌────────────────┐                                   │ │
│  │  │   Next.js     │ │  Dapr Sidecar  │                                   │ │
│  │  │   (3 pods)    │ │   (Injected)   │                                   │ │
│  │  └───────────────┘ └────────────────┘                                   │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                    │                                          │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │                         BACKEND SERVICE                                  │ │
│  │  ┌───────────────┐ ┌────────────────┐ ┌──────────────┐                  │ │
│  │  │   FastAPI     │ │  Dapr Sidecar  │ │  MCP Server  │                  │ │
│  │  │   (3 pods)    │ │   (Injected)   │ │  (In-proc)   │                  │ │
│  │  └───────────────┘ └────────────────┘ └──────────────┘                  │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                    │                                          │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │                    EVENT-DRIVEN SERVICES                                 │ │
│  │  ┌─────────────┐ ┌─────────────────┐ ┌───────────────┐                  │ │
│  │  │ Notification│ │ Recurring Task  │ │    Billing    │                  │ │
│  │  │   Service   │ │    Service      │ │    Service    │                  │ │
│  │  └─────────────┘ └─────────────────┘ └───────────────┘                  │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                    ↕                                          │
│  ┌─────────────────────────┐     ┌──────────────────────────────────────────┐│
│  │    KAFKA/REDPANDA       │     │           DAPR COMPONENTS               ││
│  │  ┌──────────────────┐   │     │  • pubsub.kafka                         ││
│  │  │ task-events      │   │     │  • state.postgresql                     ││
│  │  │ reminders        │   │     │  • secretstores.kubernetes              ││
│  │  │ time-logged      │   │     │  • jobs/scheduler                       ││
│  │  └──────────────────┘   │     └──────────────────────────────────────────┘│
│  └─────────────────────────┘                                                 │
│                                    ↓                                          │
│                        ┌───────────────────┐                                 │
│                        │   Neon PostgreSQL  │                                 │
│                        │   (External DB)    │                                 │
│                        └───────────────────┘                                 │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 5.5 Cloud Provider Deployment

#### Option 1: Azure AKS (Recommended - $200 free credit)

```bash
# 1. Create AKS cluster
az aks create \
  --resource-group teamflow-rg \
  --name teamflow-cluster \
  --node-count 3 \
  --node-vm-size Standard_B2s \
  --enable-addons monitoring

# 2. Get credentials
az aks get-credentials --resource-group teamflow-rg --name teamflow-cluster

# 3. Install Dapr
dapr init -k --runtime-version 1.14.0

# 4. Deploy application
helm upgrade --install teamflow ./helm/teamflow-prod -n teamflow --create-namespace
```

#### Option 2: Oracle OKE (Always Free Tier)

```bash
# Best for learning - no time pressure
# Up to 4 OCPUs and 24GB RAM in Always Free tier
oci ce cluster create --name teamflow-cluster --compartment-id $COMPARTMENT_ID
```

#### Option 3: Google Cloud GKE ($300 credit for 90 days)

```bash
gcloud container clusters create teamflow-cluster \
  --zone us-central1-a \
  --num-nodes 3 \
  --machine-type e2-medium
```

### 5.6 CI/CD Pipeline (GitHub Actions)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy TeamFlow

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_PREFIX: ${{ github.repository }}

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run Backend Tests
        run: |
          cd teamflow-web/backend
          pip install uv
          uv sync
          uv run pytest

      - name: Run Frontend Tests
        run: |
          cd teamflow-web/frontend
          npm ci
          npm test

  build-images:
    needs: build-and-test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Build and Push Backend
        uses: docker/build-push-action@v5
        with:
          context: ./teamflow-web/backend
          push: true
          tags: ${{ env.REGISTRY }}/${{ env.IMAGE_PREFIX }}/backend:${{ github.sha }}

      - name: Build and Push Frontend
        uses: docker/build-push-action@v5
        with:
          context: ./teamflow-web/frontend
          push: true
          tags: ${{ env.REGISTRY }}/${{ env.IMAGE_PREFIX }}/frontend:${{ github.sha }}

  deploy-production:
    needs: build-images
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to Kubernetes
        run: |
          helm upgrade --install teamflow ./helm/teamflow-prod \
            --set frontend.image.tag=${{ github.sha }} \
            --set backend.image.tag=${{ github.sha }}
```

---

## Implementation Checklist

### Phase IV Tasks (Local Kubernetes)

- [ ] **T401**: Optimize backend Dockerfile (multi-stage build)
- [ ] **T402**: Create frontend Dockerfile with standalone output
- [ ] **T403**: Update `next.config.ts` with `output: 'standalone'`
- [ ] **T404**: Create Helm chart structure
- [ ] **T405**: Create Kubernetes secrets for environment variables
- [ ] **T406**: Deploy on Minikube and verify all services running
- [ ] **T407**: Configure Ingress for local access
- [ ] **T408**: Document kubectl-ai and Gordon commands used

### Phase V Tasks (Cloud + Event-Driven)

- [ ] **T501**: Set up Kafka/Redpanda cluster on K8s
- [ ] **T502**: Install and configure Dapr on cluster
- [ ] **T503**: Create Dapr component files (pubsub, state, secrets)
- [ ] **T504**: Implement task event publishing in backend
- [ ] **T505**: Create Notification Service microservice
- [ ] **T506**: Create Recurring Task Service microservice
- [ ] **T507**: Implement Dapr Jobs API for reminders
- [ ] **T508**: Set up CI/CD pipeline with GitHub Actions
- [ ] **T509**: Deploy to cloud provider (AKS/GKE/OKE)
- [ ] **T510**: Configure monitoring and logging

---

## Key Changes Required to Existing Codebase

### 1. Backend Changes

| File | Change | Priority |
|------|--------|----------|
| `backend/Dockerfile` | Optimize for production | High |
| `backend/app/main.py` | Add Dapr subscription endpoint | High |
| `backend/app/services/` | Add `event_publisher.py` | High |
| `backend/app/routers/tasks.py` | Emit events on CRUD ops | High |
| New: `backend/app/services/dapr_client.py` | Dapr HTTP client wrapper | High |

### 2. Frontend Changes

| File | Change | Priority |
|------|--------|----------|
| New: `frontend/Dockerfile` | Create Dockerfile | High |
| `frontend/next.config.ts` | Add `output: 'standalone'` | High |
| `frontend/.env.production` | Add K8s service URLs | Medium |

### 3. New Infrastructure Files

| File | Purpose |
|------|---------|
| `helm/teamflow/` | Helm chart for K8s deployment |
| `dapr-components/` | Dapr component configurations |
| `k8s/` | Raw Kubernetes manifests (backup) |
| `.github/workflows/deploy.yml` | CI/CD pipeline |

---

## Verification Plan

### Automated Tests

1. **Backend Unit Tests** (already exist in `teamflow-web/backend/tests/`)
   ```bash
   cd teamflow-web/backend
   uv run pytest
   ```

2. **Frontend Tests** (check if tests exist)
   ```bash
   cd teamflow-web/frontend
   npm test
   ```

3. **E2E Tests** (if Playwright configured)
   ```bash
   cd teamflow-web/frontend
   npx playwright test
   ```

### Manual Verification

1. **Local Docker Test**:
   - Build and run containers with `docker-compose`
   - Verify frontend accessible at `http://localhost:3000`
   - Verify backend API at `http://localhost:8000/docs`

2. **Minikube Test**:
   - `helm install` completes without errors
   - All pods in `Running` state: `kubectl get pods -n teamflow`
   - Access via `minikube service teamflow-frontend -n teamflow`
   - Create/update/complete a task in the UI

3. **Dapr Integration Test**:
   - Task creation triggers event visible in Kafka/Redpanda logs
   - Recurring task auto-creates on completion

---

## Recommended Approach

> [!TIP]
> **Start with Phase IV first** and get a stable local deployment before adding Dapr and Kafka complexity.

### Week 1 Focus (Phase IV - Due Jan 18):
1. Containerize frontend and backend
2. Create Helm charts
3. Deploy on Minikube
4. Document AIOps commands used

### Week 2 Focus (Phase V - if time permits):
1. Add Kafka/Redpanda
2. Integrate Dapr
3. Deploy to cloud
4. Set up CI/CD
