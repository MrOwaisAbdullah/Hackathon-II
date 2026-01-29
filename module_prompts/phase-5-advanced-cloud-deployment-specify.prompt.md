# Phase 5: TeamFlow Advanced Cloud Deployment - Complete Specification Prompt

You are acting as the **Cloud-Native Solutions Architect** for TeamFlow. Your goal is to generate the **Specify (Requirement Specification)** for Phase 5 of the hackathon project.

---

## Context

We are implementing **Phase V: Advanced Cloud Deployment** of the TeamFlow Agency CRM Hackathon.

**Current Implementation Status:**
- ✅ **Phase I Complete**: Console app with in-memory task distribution
- ✅ **Phase II Complete**: Full-stack web app with Next.js + FastAPI + Neon DB + Better Auth
- ✅ **Phase III Complete**: AI Chatbot with OpenAI Agents SDK + MCP tools
- ✅ **Phase IV Complete**: Local Kubernetes deployment with Minikube + Helm charts

**What We Have (Phase IV):**
- Working Docker images (frontend + backend)
- Helm charts for Minikube deployment
- Basic Kubernetes manifests (Deployment, Service, Ingress)
- Local Minikube testing environment

**What's Missing (Phase V Goals):**
- ❌ Dapr sidecar integration
- ❌ Kafka/Redpanda event streaming
- ❌ Event-driven microservices architecture
- ❌ Advanced features (recurring tasks, due date reminders, real-time sync)
- ❌ Cloud Kubernetes deployment (AKS/GKE/OKE)
- ❌ CI/CD pipeline with GitHub Actions
- ❌ Production monitoring and observability

**Hackathon Points:** 300 pts
**Deadline:** January 18, 2026

---

## MANDATORY: Research First with MCP Tools

Before generating the specification, you MUST use MCP tools for research:

### Step 1: Cloud Provider Selection Research

```bash
# Via tavily MCP:
tavily search "Oracle OKE always free tier 2025 ARM Ampere pricing"
tavily search "AKS GKE OKE Kubernetes managed services comparison 2025"
tavily search "Kubernetes deployment cost optimization cloud providers"
```

### Step 2: Dapr Integration Research

```bash
# Via context7 MCP:
context7 resolve-library-id "dapr" → query-docs "pubsub kafka configuration"
context7 resolve-library-id "dapr" → query-docs "state management postgresql"
context7 resolve-library-id "dapr" → query-docs "secret stores kubernetes"

# Via tavily:
tavily search "Dapr Kubernetes sidecar deployment tutorial 2025"
tavily search "Dapr pubsub Kafka Redpanda Strimzi integration"
```

### Step 3: Kafka/Redpanda Research

```bash
# Via tavily:
tavily search "Redpanda vs Kafka Strimzi Kubernetes deployment 2025"
tavily search "Kafka topics event sourcing microservices architecture"
tavily search "Kubernetes Kafka Strimzi operator production deployment"
```

### Step 4: CI/CD Pipeline Research

```bash
# Via context7:
context7 resolve-library-id "github-actions" → query-docs "deploy helm kubernetes"

# Via tavily:
tavily search "GitHub Actions Helm deployment pipeline Kubernetes 2025"
tavily search "ArgoCD GitOps Kubernetes deployment patterns"
```

### Step 5: Existing Skills Review

```bash
# Read and apply:
@.claude/skills/cloud-native-blueprints/SKILL.md
@.claude/skills/deployment-engineer/SKILL.md
```

---

## Part A: Gap Analysis - What to Add/Replace

### Current Architecture (Phase IV)
```
┌─────────────────────────────────────────────────────────────┐
│                   MINIKUBE CLUSTER                          │
│                                                              │
│  ┌─────────────┐   ┌─────────────┐                         │
│  │  Frontend   │   │  Backend    │                         │
│  │  (Next.js)  │──▶│  (FastAPI)  │──▶ Neon DB (External) │
│  │  Pod        │   │  Pod        │                         │
│  └─────────────┘   └─────────────┘                         │
│         │                 │                                 │
│         └─────────────────┼─────────┐                       │
│                          ▼         ▼                       │
│                   ┌─────────────┐                           │
│                   │  Ingress    │                           │
│                   └─────────────┘                           │
└─────────────────────────────────────────────────────────────┘
```

### Target Architecture (Phase V)
```
┌─────────────────────────────────────────────────────────────────────────┐
│                         CLOUD KUBERNETES (AKS/GKE/OKE)                  │
│                                                                          │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │  Frontend Pod (Next.js)            Backend Pod (FastAPI)          │ │
│  │  ┌───────────┐ ┌───────────┐         ┌───────────┐ ┌───────────┐ │ │
│  │  │ Next.js   ││   Dapr    │         │  FastAPI  ││   Dapr    │ │ │
│  │  └───────────┘│  Sidecar  │         │ + Agents  ││  Sidecar  │ │ │
│  │  └───────────┘             │         └───────────┘└───────────┘ │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                 │                                     │
│                                 ▼                                     │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │                         DAPR COMPONENTS                            │ │
│  │  ┌─────────────────────────────────────────────────────────────┐  │ │
│  │  │ pubsub.kafka        → Kafka/Redpanda (task-events,         │  │ │
│  │  │                        reminders, time-logged)               │  │ │
│  │  ├─────────────────────────────────────────────────────────────┤  │ │
│  │  │ state.postgresql   → Neon DB (conversation state, cache)    │  │ │
│  │  ├─────────────────────────────────────────────────────────────┤  │ │
│  │  │ secretstores.k8s   → K8s Secrets (API keys, credentials)    │  │ │
│  │  ├─────────────────────────────────────────────────────────────┤  │ │
│  │  │ bindings.cron      → Scheduled reminders (due date alerts)  │  │ │
│  │  └─────────────────────────────────────────────────────────────┘  │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                 │                                     │
│                                 ▼                                     │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │                    KAFKA/REDPANDA CLUSTER                         │ │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐                 │ │
│  │  │task-events  │ │  reminders  │ │ time-logged │                 │ │
│  │  │(CRUD ops)   │ │(scheduled)  │ │(analytics)  │                 │ │
│  │  └─────────────┘ └─────────────┘ └─────────────┘                 │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                 │                                     │
│                                 ▼                                     │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │              EVENT-DRIVEN MICROSERVICES (K8s Deployments)        │ │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐                 │ │
│  │  │ Notification│ │  Recurring  │ │  Billing   │                 │ │
│  │  │  Service    │ │  Task Svc   │ │  Service   │                 │ │
│  │  │(Email/Push) │ │(Auto-create)│ │(Invoices)  │                 │ │
│  │  └─────────────┘ └─────────────┘ └─────────────┘                 │ │
│  └───────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Part B: What Needs to be ADDED (New Components)

### 1. Dapr Sidecar Integration

**Files to Create:**
- `dapr-components/` - Dapr component YAML configurations
- `helm/teamflow-prod/` - Production Helm charts with Dapr annotations

**Key Changes:**
- Add Dapr sidecar annotations to all Deployments
- Create Dapr component configurations for:
  - `pubsub.kafka` - Kafka pub/sub component
  - `state.postgresql` - PostgreSQL state store (Neon)
  - `secretstores.kubernetes` - K8s secret store
  - `bindings.cron` - Cron binding for scheduled reminders

### 2. Kafka/Redpanda Event Streaming

**Choice Required:** Kafka with Strimzi Operator vs Redpanda

**Recommendation:** Use **Redpanda** for hackathon because:
- No ZooKeeper dependency (simpler architecture)
- Single binary deployment (faster setup)
- Kafka-compatible (same client libraries work)
- Faster for learning/event-driven patterns

**Files to Create:**
- `kafka/` - Kafka cluster configuration
- `kafka/topics/` - Topic definitions (task-events, reminders, time-logged)
- `kafka/consumers/` - Consumer service implementations

**Topics to Create:**
- `task-events` - All task CRUD operations (create, update, assign, complete)
- `reminders` - Scheduled reminder triggers
- `time-logged` - Time entry events for billing

### 3. Event-Driven Microservices

**New Services to Implement:**

#### A. Notification Service
```python
# Location: teamflow-web/backend/app/services/notification_service.py

Purpose: Consume reminder events and send notifications
Input: Kafka topic 'reminders'
Output: Email/Push notifications to users
```

#### B. Recurring Task Service
```python
# Location: teamflow-web/backend/app/services/recurring_task_service.py

Purpose: Auto-create next instance of recurring tasks
Input: Kafka topic 'task-events' (filter for completed recurring tasks)
Output: New task created in database
```

#### C. Real-Time Sync Service
```python
# Location: teamflow-web/backend/app/services/realtime_sync_service.py

Purpose: Broadcast task updates to all connected clients
Input: Kafka topic 'task-events'
Output: WebSocket broadcast to frontend
```

### 4. Advanced Features Implementation

#### A. Recurring Tasks
**Database Schema Changes:**
```sql
ALTER TABLE tasks ADD COLUMN recurrence_rule JSONB;
-- Example: {"frequency": "weekly", "days": ["monday"], "end_date": "2025-12-31"}
```

**Backend Changes:**
- Add recurrence logic to `TaskService`
- Create recurring task processor service

#### B. Due Date Reminders
**Implementation:**
- Use Dapr Cron Binding to trigger reminder checks
- Publish to `reminders` topic when task due date is approaching
- Notification service consumes and sends alerts

#### C. Real-Time Updates
**Implementation:**
- WebSocket connection in frontend
- Real-time sync service consumes task-events
- Broadcast updates to all connected clients

### 5. Cloud Kubernetes Deployment

**Provider Selection Decision Framework:**

| Provider | Free Tier | Best For | Monthly Cost (Small) |
|----------|-----------|----------|----------------------|
| **Oracle OKE** ⭐ | 4 OCPUs, 24GB RAM (Always Free) | Cost-conscious, learning | **$0** |
| **Google GKE** | $74.40 credit (one-time) | Best developer experience | ~$150 |
| **Azure AKS** | Free control plane | Microsoft ecosystem | ~$175 |
| **AWS EKS** | $72/mo control plane | AWS shops | ~$285 |

**Recommendation for Hackathon:** **Oracle OKE** (Always Free tier)

**Files to Create:**
- `infrastructure/cloud/` - Cloud provider manifests
- `.github/workflows/deploy-cloud.yml` - CI/CD pipeline

### 6. CI/CD Pipeline (GitHub Actions)

**Pipeline Stages:**
1. **Build** - Build and push Docker images
2. **Test** - Run tests (unit, integration, E2E)
3. **Security Scan** - Trivy vulnerability scanning
4. **Deploy Staging** - Deploy to Minikube/staging
5. **Integration Test** - Smoke tests on staging
6. **Deploy Production** - Deploy to cloud K8s (manual approval)
7. **Notify** - Slack/email notification

---

## Part C: What Needs to be MODIFIED (Existing Components)

### 1. Backend (FastAPI) Changes

#### A. Add Dapr Client Integration
```python
# File: teamflow-web/backend/app/core/dapr_client.py (CREATE)

import httpx

DAPR_PORT = 3500

class DaprClient:
    async def publish_event(self, topic: str, data: dict):
        """Publish event to Dapr pub/sub"""
        async with httpx.AsyncClient() as client:
            await client.post(
                f"http://localhost:{DAPR_PORT}/v1.0/publish/kafka-pubsub/{topic}",
                json=data
            )

    async def get_state(self, key: str):
        """Get state from Dapr state store"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"http://localhost:{DAPR_PORT}/v1.0/state/statestore/{key}"
            )
            return response.json()

    async def save_state(self, key: str, data: dict):
        """Save state to Dapr state store"""
        async with httpx.AsyncClient() as client:
            await client.post(
                f"http://localhost:{DAPR_PORT}/v1.0/state/statestore",
                json=[{"key": key, "value": data}]
            )
```

#### B. Add Event Publishing to Task Service
```python
# File: teamflow-web/backend/app/services/task_service.py (MODIFY)

# After each task operation, publish event:
await dapr_client.publish_event("task-events", {
    "event_type": "task_created",
    "task_id": task.id,
    "project_id": task.project_id,
    "user_id": user_id,
    "timestamp": datetime.utcnow().isoformat()
})
```

#### C. Add Dapr Endpoints
```python
# File: teamflow-web/backend/app/api/dapr.py (CREATE)

from fastapi import APIRouter

router = APIRouter(prefix="/dapr")

@router.get("/subscribe")
async def subscribe():
    """Dapr pub/sub subscription endpoint"""
    return [
        {
            "pubsubname": "kafka-pubsub",
            "topic": "task-events",
            "route": "/events/tasks"
        },
        {
            "pubsubname": "kafka-pubsub",
            "topic": "reminders",
            "route": "/events/reminders"
        }
    ]

@router.post("/events/tasks")
async def handle_task_event(event: dict):
    """Handle task events from Kafka"""
    event_type = event.get("event_type")
    # Process event (recurrence, notifications, etc.)
    return {"status": "SUCCESS"}
```

### 2. Frontend (Next.js) Changes

#### A. Add WebSocket Connection for Real-Time Updates
```typescript
// File: teamflow-web/frontend/src/lib/websocket.ts (CREATE)

export class TaskWebSocket {
  private ws: WebSocket | null = null;

  connect() {
    this.ws = new WebSocket('ws://localhost:8000/ws/tasks');
    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      // Update UI based on event
      this.handleTaskUpdate(data);
    };
  }

  handleTaskUpdate(event: TaskEvent) {
    // Update task list in real-time
    // Show notification if task assigned to current user
  }
}
```

#### B. Add Recurring Task UI
```typescript
// File: teamflow-web/frontend/src/components/tasks/RecurringTaskForm.tsx (CREATE)

interface RecurrenceRule {
  frequency: 'daily' | 'weekly' | 'monthly';
  days?: string[];
  end_date?: string;
}

export function RecurringTaskForm() {
  // Form to set up recurring task rules
  // Integrates with task creation modal
}
```

#### C. Add Due Date Reminder UI
```typescript
// File: teamflow-web/frontend/src/components/tasks/ReminderSettings.tsx (CREATE)

export function ReminderSettings({ taskId }: { taskId: number }) {
  // UI to set reminder time before due date
  // Options: 15 min, 1 hour, 1 day, 1 week before
}
```

### 3. Helm Charts Modifications

#### A. Add Dapr Annotations
```yaml
# File: helm/teamflow-prod/templates/backend-deployment.yaml (MODIFY)

metadata:
  annotations:
    dapr.io/enabled: "true"
    dapr.io/app-id: "teamflow-backend"
    dapr.io/app-port: "8000"
    dapr.io/config: "teamflow-dapr-config"
spec:
  template:
    metadata:
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "teamflow-backend"
        dapr.io/app-port: "8000"
```

#### B. Add Service Deployment Templates
```yaml
# File: helm/teamflow-prod/templates/notification-deployment.yaml (CREATE)

apiVersion: apps/v1
kind: Deployment
metadata:
  name: teamflow-notification-service
spec:
  replicas: 1
  selector:
    matchLabels:
      app: notification-service
  template:
    metadata:
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "notification-service"
```

---

## Part D: External Tasks Required

### 1. Cloud Provider Account Setup

**Oracle OKE (Recommended):**
- Sign up at oracle.com/cloud/free
- Create API keys for kubectl authentication
- Create OKE cluster (4 OCPUs, 24GB RAM - Always Free)

**Alternative Providers:**
- Google GKE: Create project, enable GKE API, create cluster
- Azure AKS: Create resource group, create AKS cluster

### 2. Kafka Cluster Setup

**Option A: Redpanda Cloud (Easiest)**
- Sign up at redpanda.com/cloud
- Create Serverless cluster (free tier)
- Create topics: task-events, reminders, time-logged
- Get bootstrap server URL and credentials

**Option B: Self-Hosted on K8s (Strimzi)**
- Install Strimzi operator
- Deploy Kafka cluster using YAML manifest
- Create topics using KafkaTopic CRDs

### 3. CI/CD Secrets Configuration

Add to GitHub repository secrets:
- `DOCKER_USERNAME` - Container registry username
- `DOCKER_PASSWORD` - Container registry password
- `KUBE_CONFIG` - Base64-encoded kubeconfig file
- `CLOUD_API_KEY` - Cloud provider API key

### 4. External Service Accounts

**For Notifications:**
- SendGrid account (email) OR Firebase Cloud Messaging (push)
- Add API keys to K8s secrets

**For Monitoring:**
- Datadog/New Relic account (optional)
- Install agents in cluster

---

## Part E: Step-by-Step Implementation Plan

### Phase 5-A: Local Development with Dapr + Kafka (Minikube)

**Duration:** 3-4 days

#### Step 1: Install Dapr on Minikube
```bash
# Install Dapr CLI
curl -fsSL https://raw.githubusercontent.com/dapr/cli/master/install/install.sh | bash

# Initialize Dapr on Minikube
dapr init -k

# Verify installation
dapr status -k
```

#### Step 2: Deploy Kafka/Redpanda on Minikube
```bash
# Option A: Redpanda (Recommended)
kubectl apply -f kafka/redpanda-minikube.yaml

# Option B: Strimzi
kubectl create namespace kafka
kubectl apply -f https://strimzi.io/install/latest?namespace=kafka -n kafka
kubectl apply -f kafka/kafka-cluster.yaml
```

#### Step 3: Create Dapr Components
```bash
# Apply Dapr component configurations
kubectl apply -f dapr-components/pubsub-kafka.yaml
kubectl apply -f dapr-components/state-postgresql.yaml
kubectl apply -f dapr-components/secrets-kubernetes.yaml
kubectl apply -f dapr-components/bindings-cron.yaml
```

#### Step 4: Update Backend with Dapr Integration
- Add Dapr client dependency
- Implement event publishing in TaskService
- Add Dapr event subscription endpoints
- Test event flow with Kafka

#### Step 5: Implement Event-Driven Services
- Create notification service
- Create recurring task service
- Create real-time sync service
- Deploy to Minikube as separate deployments

#### Step 6: Add Advanced Features
- Implement recurring task logic
- Add due date reminder system
- Add WebSocket real-time updates
- Test end-to-end event flow

### Phase 5-B: Cloud Deployment (AKS/GKE/OKE)

**Duration:** 2-3 days

#### Step 7: Set Up Cloud Provider
- Create cloud account (recommend Oracle OKE for free tier)
- Create Kubernetes cluster
- Configure kubectl access
- Verify cluster connectivity

#### Step 8: Create Production Helm Charts
- Copy Minikube Helm charts
- Add Dapr annotations
- Add cloud-specific configurations
- Update values.yaml for production

#### Step 9: Deploy to Cloud
- Build and push Docker images to registry
- Install Dapr on cloud cluster
- Deploy Kafka/Redpanda
- Deploy application with Helm
- Test all functionality

### Phase 5-C: CI/CD Pipeline

**Duration:** 2 days

#### Step 10: Create GitHub Actions Workflow
- Create `.github/workflows/deploy.yml`
- Configure build stage
- Configure test stage
- Configure security scanning
- Configure deployment stages
- Add manual approval gates

#### Step 11: Configure Secrets and Environments
- Add repository secrets
- Configure environment-specific values
- Test pipeline end-to-end

#### Step 12: Documentation and Submission
- Document AIOps commands used
- Create deployment guide
- Record demo video (< 90 seconds)
- Submit to hackathon form

---

## Part F: Complete Tech Stack

### Core Technologies

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| **Frontend** | Next.js | 16+ | React framework with App Router |
| **Backend** | FastAPI | Latest | Python web framework |
| **Database** | Neon PostgreSQL | Serverless | Primary database |
| **Dapr** | Dapr | 1.14+ | Distributed application runtime |
| **Kafka** | Redpanda/Strimzi | Latest | Event streaming platform |
| **Container** | Docker | Latest | Containerization |
| **Orchestration** | Kubernetes | 1.29+ | Container orchestration |
| **Package Manager** | Helm | 3.15+ | K8s package management |
| **CI/CD** | GitHub Actions | Latest | Automation pipeline |

### Dapr Components

| Component | Type | Configuration |
|-----------|------|---------------|
| **pubsub.kafka** | `pubsub.kafka` | Kafka/Redpanda bootstrap servers |
| **state.postgresql** | `state.postgresql` | Neon DB connection string |
| **secretstores.k8s** | `secretstores.kubernetes` | K8s secret store |
| **bindings.cron** | `bindings.cron` | Scheduled reminder checks |

### Cloud Provider Options

| Provider | Free Tier | Cost | Recommendation |
|----------|-----------|------|----------------|
| **Oracle OKE** | 4 OCPUs, 24GB RAM (Always Free) | $0 | ⭐ Best for hackathon |
| **Google GKE** | $74.40 credit (one-time) | ~$150/mo | Best DX |
| **Azure AKS** | Free control plane | ~$175/mo | Microsoft ecosystem |
| **AWS EKS** | $72/mo control plane | ~$285/mo | AWS shops |

### Additional Tools

| Tool | Purpose | Usage |
|------|---------|-------|
| **kubectl-ai** | Natural language K8s operations | Deployment and scaling |
| **Kagent** | Cluster analysis and optimization | Resource tuning |
| **Docker Gordon** | AI-assisted Dockerfile optimization | Image optimization |
| **Trivy** | Container security scanning | CI/CD security checks |
| **Prometheus** | Metrics collection | Monitoring (optional) |
| **Grafana** | Metrics visualization | Dashboards (optional) |

---

## Part G: User Stories for Phase V

### User Story 1: Recurring Task Automation

As a project manager, I want to set up recurring tasks so that I don't have to manually create the same task every week.

**Acceptance Criteria:**
- User can set recurrence rule when creating task (daily, weekly, monthly)
- System automatically creates next task instance when current task is completed
- User can specify end date for recurrence
- Recurring tasks display recurrence indicator in UI

### User Story 2: Due Date Reminders

As a team member, I want to receive reminders before tasks are due so that I don't miss deadlines.

**Acceptance Criteria:**
- User can set reminder time (15 min, 1 hour, 1 day, 1 week before)
- System sends notification at specified time before due date
- Notifications are sent via email (and optionally push notification)
- User can customize reminder preferences per task

### User Story 3: Real-Time Task Updates

As a team member, I want to see task updates in real-time so that I'm always working with the latest information.

**Acceptance Criteria:**
- When a task is created/updated by any user, all connected clients see update immediately
- No page refresh required to see new tasks
- Notification appears when task is assigned to current user
- Multiple users can collaborate without conflicts

### User Story 4: Event-Driven Architecture

As a developer, I want the system to use event-driven patterns so that services are decoupled and scalable.

**Acceptance Criteria:**
- All task CRUD operations publish events to Kafka
- Separate services consume events (notifications, recurring tasks, sync)
- Services can be scaled independently
- System remains responsive during high load

---

## Part H: Success Criteria

### Containerization & Deployment
- [ ] All services run with Dapr sidecar enabled
- [ ] Kafka/Redpanda cluster deployed and accessible
- [ ] All event topics created and consuming messages
- [ ] Application deployed to cloud Kubernetes (AKS/GKE/OKE)
- [ ] Zero-downtime rolling updates configured

### Event-Driven Features
- [ ] Recurring tasks auto-create next instance
- [ ] Due date reminders sent at correct time
- [ ] Real-time updates work across multiple clients
- [ ] Event-driven services are independently scalable

### CI/CD Pipeline
- [ ] GitHub Actions workflow builds and tests on every push
- [ ] Security scanning (Trivy) runs on all images
- [ ] Automated deployment to staging environment
- [ ] Manual approval gate for production deployment
- [ ] Deployment notifications sent to Slack/email

### Documentation
- [ ] All AIOps commands documented
- [ ] Architecture diagrams updated
- [ ] Deployment guide created
- [ ] Demo video recorded (< 90 seconds)
- [ ] Hackathon form submitted with all links

---

## Part I: Bonus Points Opportunities

| Bonus Feature | Points | Implementation Path |
|---------------|--------|-------------------|
| **Reusable Intelligence** | +200 | Create agent skills for Dapr/Kafka patterns |
| **Cloud-Native Blueprints** | +200 | Document K8s deployment blueprints |
| **Multi-language (Urdu)** | +100 | Add Urdu language support to chatbot |
| **Voice Commands** | +200 | Web Speech API for task commands |

---

## Output Requirement

Generate a comprehensive specification file at:
```
specs/003-advanced-cloud-deployment/spec.md
```

The specification MUST include:

1. **Detailed Requirements** - All functional and non-functional requirements
2. **Architecture Diagrams** - Visual representations of the target architecture
3. **API Specifications** - Dapr endpoints, Kafka event schemas
4. **Database Schema Changes** - Recurrence rules, reminder settings
5. **Deployment Configuration** - Helm values, Dapr components, Kafka topics
6. **CI/CD Pipeline** - GitHub Actions workflow YAML
7. **Testing Strategy** - How to validate event-driven features
8. **Migration Guide** - How to move from Phase IV to Phase V
9. **Troubleshooting** - Common issues and solutions
10. **Bonus Features** - How to achieve bonus points

Remember: This is a hackathon submission. Focus on **demonstrating working features** rather than perfection. Get the event-driven architecture working first, then optimize.

---

**References to Include:**
- Dapr documentation: https://docs.dapr.io
- Redpanda K8s guide: https://docs.redpanda.com/current/migrate/kubernetes/
- Oracle OKE free tier: https://www.oracle.com/cloud/free/
- GitHub Actions K8s deployment: https://docs.github.com/en/actions/deployment/deploying-to-cloud-platforms

**MCP Servers to Use:**
- `context7` - For Dapr, Kubernetes, GitHub Actions docs
- `tavily` - For latest best practices and troubleshooting
- `chrome-devtools` - For testing WebSocket and real-time features
