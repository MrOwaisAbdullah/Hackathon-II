# Implementation Plan: TeamFlow Advanced Cloud Deployment (Phase 5)

**Branch**: `005-advanced-cloud-deployment` | **Date**: 2026-01-29 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-advanced-cloud-deployment/spec.md`

## Summary

Transform TeamFlow from a monolithic Kubernetes deployment to an **event-driven microservices architecture** with Dapr sidecar integration, Kafka/Redpanda event streaming, and Oracle OKE cloud deployment. Add **advanced features**: recurring tasks with automatic instance creation, due date reminders with scheduled notifications, and real-time task synchronization via WebSocket. Implement **CI/CD automation** via GitHub Actions with security scanning, staging deployment, and production approval gates.

**Technical Approach**:
- **Event-Driven**: Use Dapr Pub/Sub with Redpanda Kafka for decoupled microservice communication
- **Microservices**: Deploy Notification, Recurring Task, and Real-Time Sync services as independent scalable units
- **Cloud-Native**: Leverage Dapr building blocks (state, secrets, bindings) instead of custom implementations
- **Infrastructure**: Deploy to Oracle OKE Always Free tier with Helm charts and GitHub Actions CI/CD
- **Observability**: Implement health checks, structured logging, and Prometheus metrics for production monitoring

## Technical Context

**Language/Version**: Python 3.13+ (backend), TypeScript/Next.js 14 (frontend), Go 1.21+ (Dapr sidecar)
**Primary Dependencies**: FastAPI 0.115+, Dapr SDK 1.14+, Redpanda/Kafka, Helm 3.0+, kubectl-ai, GitHub Actions
**Storage**: Neon PostgreSQL (external managed), Dapr state store (caching layer), Kafka topics (event streaming)
**Testing**: pytest (backend), vitest (frontend), integration tests (event streaming), load tests (k6 or Locust)
**Target Platform**: Oracle OKE (Always Free: 4 OCPUs, 24GB RAM), Kubernetes 1.29+
**Project Type**: Web application with microservices architecture
**Performance Goals**:
- API endpoints: < 200ms p95 (excluding event processing latency)
- Event processing: < 2s from publish to consumer delivery
- Real-time updates: < 2s propagation to all connected clients
- Support 100 concurrent users with sub-second response times
- Zero downtime rolling updates (maxUnavailable: 0)

**Constraints**:
- Container images must remain under 500MB for efficient deployment
- Must use free-tier cloud resources where possible (OKE Always Free, Redpanda Free Tier)
- Backward compatibility with Phase IV Minikube deployment
- All secrets managed via Kubernetes secrets or Dapr secret store
- Timeline: Complete by hackathon deadline January 18, 2026

**Scale/Scope**:
- 3 microservices (Notification, Recurring Task, Real-Time Sync) + main backend/frontend
- 4 Kafka topics (task-events, reminders, time-logged, task-updates)
- 5 Dapr components (pubsub.kafka, state.postgresql, secretstores.kubernetes, bindings.cron x2)
- Single-region deployment (multi-region out of scope)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Phase 0: Pre-Implementation Check

- [x] **Existing Skills Consulted**: Reviewed `cloud-native-blueprints`, `deployment-engineer`, `mcp-builder`, `rag-pipeline-builder` skills
- [x] **SOLID Principles**:
  - **SRP**: Each microservice has single responsibility (Notification sends alerts, Recurring creates instances, Sync broadcasts)
  - **OCP**: Dapr components enable swapping implementations (Kafka → RabbitMQ) without code changes
  - **LSP**: All microservices implement same EventConsumer protocol
  - **ISP**: Separate pub/sub, state, and secret interfaces (no forced dependencies)
  - **DIP**: Services depend on Dapr abstractions, not concrete Kafka clients
- [x] **DRY Applied**: Reusing Helm chart templates from Phase IV, Dapr component configurations from cloud-native-blueprints skill
- [x] **TDD Ready**: Unit tests for event handlers, integration tests for Kafka flows, E2E tests for complete user journeys
- [x] **Type Safety**: Python type hints for all service functions, TypeScript strict mode for frontend
- [x] **Security**: Secrets never in git, Kubernetes secrets for credentials, Dapr mTLS for service-to-service
- [x] **Performance**: Resource limits defined, health probes configured, HPA for autoscaling
- [x] **MCP Tools**: Context7 used for Dapr/Kafka docs research, Tavily for cloud deployment best practices
- [x] **Skill Refinement**: Documented all learned patterns in existing skills

**Result**: ✅ All constitution requirements satisfied. Proceed to Phase 0 research.

## Project Structure

### Documentation (this feature)

```text
specs/005-advanced-cloud-deployment/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   ├── event-streaming-api.yaml    # Kafka event schemas
│   ├── microservices-api.yaml      # Microservice endpoints
│   └── webhook-api.yaml            # Webhook contracts for 3rd party integrations
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
teamflow-web/
├── backend/
│   ├── app/
│   │   ├── main.py                    # MODIFY: Add Dapr subscription endpoints
│   │   ├── services/
│   │   │   ├── event_publisher.py     # NEW: Dapr event publishing wrapper
│   │   │   ├── task_service.py        # MODIFY: Emit events on CRUD ops
│   │   │   ├── recurrence_service.py  # NEW: Recurrence calculation logic
│   │   │   └── reminder_service.py    # NEW: Reminder scheduling logic
│   │   ├── routers/
│   │   │   ├── tasks.py               # MODIFY: Add recurrence/reminder fields
│   │   │   └── websocket.py           # NEW: WebSocket endpoint for real-time updates
│   │   ├── models/
│   │   │   ├── task.py                # MODIFY: Add recurrence_rule, reminder_settings
│   │   │   └── event.py               # NEW: TaskEvent model
│   │   └── dapr/                      # NEW: Dapr integration layer
│   │       ├── __init__.py
│   │       ├── pubsub.py              # Dapr pub/sub client
│   │       ├── state.py               # Dapr state client
│   │       └── secrets.py             # Dapr secrets client
│   ├── tests/
│   │   ├── test_event_publisher.py    # NEW: Unit tests for event publishing
│   │   ├── test_recurrence.py         # NEW: Unit tests for recurrence logic
│   │   └── test_reminders.py          # NEW: Unit tests for reminder scheduling
│   └── microservices/                 # NEW: Independent microservices
│       ├── notification_service/
│       │   ├── main.py                # FastAPI app consuming reminder events
│       │   ├── email_client.py        # Email sending (SendGrid/SES)
│       │   └── Dockerfile
│       ├── recurring_task_service/
│       │   ├── main.py                # FastAPI app consuming task completion events
│       │   ├── recurrence_calculator.py
│       │   └── Dockerfile
│       └── realtime_sync_service/
│           ├── main.py                # FastAPI + WebSocket consuming task events
│           ├── connection_manager.py
│           └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── tasks/
│   │   │   │   ├── TaskForm.tsx       # MODIFY: Add recurrence/reminder UI
│   │   │   │   ├── TaskList.tsx       # MODIFY: Real-time update integration
│   │   │   │   └── RecurrenceDialog.tsx  # NEW: Recurrence rule configuration
│   │   │   └── notifications/
│   │   │       └── ReminderSettings.tsx  # NEW: Reminder preference UI
│   │   ├── hooks/
│   │   │   ├── useTaskEvents.ts       # NEW: WebSocket event subscription hook
│   │   │   └── useRealtimeTasks.ts    # NEW: Auto-updating task list
│   │   └── services/
│   │       └── websocket.ts           # NEW: WebSocket client
│   └── Dockerfile                     # MODIFY: Already exists from Phase IV
│
├── dapr-components/                     # NEW: Dapr component configurations
│   ├── pubsub.kafka.yaml               # Kafka pub/sub component
│   ├── state.postgresql.yaml           # PostgreSQL state store
│   ├── secretstores.kubernetes.yaml    # Kubernetes secret store
│   └── bindings/
│       ├── reminder-checker.cron.yaml  # Cron binding for reminder checks
│       └── task-cleanup.cron.yaml      # Cron binding for task cleanup
│
├── helm/
│   └── teamflow/
│       ├── Chart.yaml                  # MODIFY: Add microservices dependencies
│       ├── values.yaml                 # MODIFY: Add microservice configuration
│       └── templates/
│           ├── backend-deployment.yaml # MODIFY: Add Dapr annotations
│           ├── frontend-deployment.yaml # MODIFY: Add Dapr annotations
│           ├── notification-service-deployment.yaml  # NEW
│           ├── recurring-task-service-deployment.yaml  # NEW
│           ├── realtime-sync-service-deployment.yaml  # NEW
│           └── ingress.yaml            # MODIFY: Add WebSocket route
│
├── k8s/                                 # NEW: Raw Kubernetes manifests (backup)
│   ├── redpanda/
│   │   └── redpanda-cluster.yaml       # Redpanda Kafka cluster
│   └── base/
│       ├── namespace.yaml
│       └── resource-quotas.yaml
│
└── .github/
    └── workflows/
        └── deploy.yml                  # NEW: CI/CD pipeline
```

**Structure Decision**: Web application structure with backend/frontend separation. Microservices deployed as independent Kubernetes deployments within same namespace. Dapr sidecar injected into all services for event streaming, state management, and secret retrieval. Helm charts used for templated deployment across environments (dev, staging, production).

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| **Event-Driven Architecture** | Enables decoupled microservices for recurring tasks, reminders, and real-time sync without tight coupling | Synchronous polling would require constant database queries, poor scalability, and delayed notifications |
| **Dapr Sidecar** | Provides standard building blocks (pub/sub, state, secrets) without writing custom Kafka client code or reinventing caching | Direct Kafka integration adds complexity (connection management, serialization, error handling) and reduces portability |
| **Three Microservices** | Each feature (notifications, recurrence, sync) has independent scaling needs and failure domains | Monolithic backend would scale all features together, wasting resources, and single failure would take down all functionality |
| **Redpanda vs Apache Kafka** | Redpanda eliminates ZooKeeper dependency, simpler deployment for hackathon timeline, fully Kafka-compatible | Apache Kafka with Strimzi operator requires more resources, complex ZooKeeper coordination, steeper learning curve |
| **WebSocket for Real-Time** | Requires bidirectional communication for instant updates across all connected clients | Server-Sent Events (SSE) unidirectional only, polling inefficient with high latency, GraphQL subscriptions add framework complexity |

**Justification**: All architectural decisions align with cloud-native best practices, enable horizontal scaling, and follow Dapr/Kafka patterns documented in existing skills. Complexity is necessary for production-ready event-driven system.

---

## Implementation Phases

### Phase 0: Technology Research (MANDATORY PRE-REQUISITE)

**Objective**: Validate technology choices, document best practices, identify edge cases.

**Key Research Areas**:
1. **Dapr Building Blocks**: Verify pubsub.kafka, state.postgresql, secretstores.kubernetes components for Dapr 1.14+
2. **Redpanda Deployment**: Confirm Helm chart configuration for Kubernetes, resource requirements, topic management
3. **Oracle OKE Setup**: Document Always Free tier limits, cluster creation workflow, kubectl credential setup
4. **Email Providers**: Compare SendGrid vs AWS SES vs Mailgun for transactional email (free tier availability)
5. **CI/CD Patterns**: Research GitHub Actions workflows for container security scanning (Trivy, Grype), Helm deployment patterns
6. **WebSocket with Dapr**: Verify Dapr service invocation supports WebSocket upgrade protocol
7. **Kafka Event Schemas**: Research CloudEvents standard for event envelope format
8. **Recurring Task Libraries**: Evaluate `dateutil.rrule` vs `schedule` vs custom implementation

**Output**: `research.md` with technology decisions, configuration examples, troubleshooting guides.

---

### Phase 1: Data Model & API Contracts

**Objective**: Define data entities, API contracts, and database schema changes.

**Deliverables**:
- `data-model.md`: TaskEvent, RecurrenceRule, ReminderSettings, WebSocketConnection entities
- `contracts/event-streaming-api.yaml`: Kafka topic schemas, event envelopes
- `contracts/microservices-api.yaml`: Microservice endpoint definitions
- `contracts/webhook-api.yaml`: Webhook contracts for email providers, push notifications

**Key Schema Changes**:
```sql
-- Add to existing tasks table
ALTER TABLE tasks ADD COLUMN recurrence_rule JSONB;
ALTER TABLE tasks ADD COLUMN reminder_settings JSONB;
ALTER TABLE tasks ADD COLUMN next_instance_id UUID REFERENCES tasks(id);

-- New table for event log
CREATE TABLE task_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type TEXT NOT NULL,
    task_id UUID REFERENCES tasks(id),
    user_id UUID REFERENCES users(id),
    payload JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

### Phase 2: Dapr Integration & Local Development

**Objective**: Set up local environment with Dapr, Kafka, and implement event publishing.

**Tasks**:
1. Install Dapr CLI and initialize on Minikube: `dapr init -k`
2. Deploy Redpanda to Minikube via Helm
3. Create Dapr component files (pubsub, state, secrets, bindings)
4. Implement `event_publisher.py` for Dapr HTTP client
5. Add `/dapr/subscribe` endpoint to backend
6. Emit events on all task CRUD operations (create, update, complete, delete)
7. Test event flow: curl → backend → Dapr → Kafka → consumer

**Acceptance**:
- Events visible in Redpanda topic: `rpk topic consume task-events`
- Backend subscription endpoint returns valid routes
- No errors in Dapr sidecar logs: `kubectl logs <pod> -c daprd`

---

### Phase 3: Microservices Implementation

**Objective**: Build three event-driven microservices with Dapr integration.

**3.1 Notification Service**

**Purpose**: Consume reminder events from Kafka and send email/push notifications.

**Tech Stack**: FastAPI + Dapr SDK + SendGrid/SES

**Events Consumed**:
- Topic: `reminders`
- Event: `{task_id, user_id, title, due_at, remind_at, notification_type}`

**API Endpoints**:
- `POST /events/reminders` (Dapr subscription route)
- `GET /health` (health check)

**Dockerfile**: Multi-stage Python 3.13-slim build

**3.2 Recurring Task Service**

**Purpose**: Consume task completion events, calculate next instance, create new task.

**Tech Stack**: FastAPI + Dapr SDK + dateutil.rrule

**Events Consumed**:
- Topic: `task-events`
- Filter: `event_type == 'completed'`
- Event: `{task_id, recurrence_rule, user_id, project_id}`

**Recurrence Logic**:
```python
from dateutil.rrule import rrule, rruleset, DAILY, WEEKLY, MONTHLY

def calculate_next_instance(completed_at: datetime, rule: dict) -> datetime:
    """Calculate next occurrence based on recurrence rule."""
    if rule['frequency'] == 'daily':
        return completed_at + timedelta(days=rule['interval'])
    elif rule['frequency'] == 'weekly':
        days = [parse_day(d) for d in rule['days_of_week']]
        next_date = rrule(WEEKLY, interval=rule['interval'], byweekday=days, dtstart=completed_at)[1]
        return next_date
    # ... monthly, custom logic
```

**API Endpoints**:
- `POST /events/task-events` (Dapr subscription route)
- `GET /health` (health check)

**3.3 Real-Time Sync Service**

**Purpose**: Consume task events, broadcast to connected WebSocket clients.

**Tech Stack**: FastAPI + WebSocket + Dapr SDK + connection pool

**Events Consumed**:
- Topic: `task-events` (all types)
- Event: `{event_type, task_id, payload, timestamp}`

**WebSocket Endpoint**:
- `WS /ws/tasks?token=<jwt>` (client connects with auth token)
- Broadcast events to all connections matching user_id filters

**Connection Manager**:
```python
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def broadcast(self, user_id: str, event: dict):
        for connection in self.active_connections.get(user_id, []):
            await connection.send_json(event)
```

**Deployment**: 3 replicas initially, HPA based on connection count

---

### Phase 4: Frontend Real-Time Integration

**Objective**: Add WebSocket client, recurrence/reminder UI, real-time task updates.

**4.1 WebSocket Client**

```typescript
// src/services/websocket.ts
export class TaskEventStream {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;

  connect(token: string) {
    this.ws = new WebSocket(`ws://localhost:8000/ws/tasks?token=${token}`);
    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      // Update local state or trigger refetch
      eventBus.emit('task:updated', data);
    };
    this.ws.onclose = () => this.reconnect();
  }

  private reconnect() {
    setTimeout(() => this.connect(this.token), 1000 * (2 ** this.reconnectAttempts));
  }
}
```

**4.2 Task Form Enhancement**

Add fields to `TaskForm.tsx`:
- **Recurrence**: Toggle + frequency dropdown (daily, weekly, monthly) + interval + days of week (multi-select) + end date (optional)
- **Reminders**: Multi-select for notification times (15 min, 1 hour, 1 day, 1 week before)

**4.3 Real-Time Task List**

```typescript
// src/hooks/useRealtimeTasks.ts
export function useRealtimeTasks() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const eventStream = useRef<TaskEventStream>();

  useEffect(() => {
    eventStream.current = new TaskEventStream();
    eventStream.current.connect(getToken());

    const handleUpdate = (event) => {
      if (event.type === 'created') {
        setTasks(prev => [...prev, event.task]);
      } else if (event.type === 'updated') {
        setTasks(prev => prev.map(t => t.id === event.task.id ? event.task : t));
      } else if (event.type === 'deleted') {
        setTasks(prev => prev.filter(t => t.id !== event.task_id));
      }
    };

    eventBus.on('task:updated', handleUpdate);
    return () => eventBus.off('task:updated', handleUpdate);
  }, []);

  return tasks;
}
```

---

### Phase 5: Cloud Deployment (Oracle OKE)

**Objective**: Deploy full stack to Oracle OKE Always Free tier with production configuration.

**5.1 Oracle Cloud Setup**

```bash
# 1. Install OCI CLI
brew install oci-cli  # Mac
# Or download from https://docs.oracle.com/en-us/iaas/Content/API/Concepts/cliconcepts.htm

# 2. Configure credentials
oci setup config

# 3. Create Always Free cluster
oci ce cluster create \
  --name teamflow-cluster \
  --compartment-id $COMPARTMENT_ID \
  --kubernetes-version 1.29 \
  --node-pool-config "size=1,shape=VM.Standard.E4.Flex" \
  --endpoint-type PUBLIC_ENDPOINT

# 4. Get kubeconfig
oci ce cluster create-kubeconfig \
  --cluster-id $CLUSTER_ID \
  --file $HOME/.kube/config-teamflow \
  --region us-ashburn-1

export KUBECONFIG=$HOME/.kube/config-teamflow
```

**5.2 Redpanda Deployment**

```bash
# Add Redpanda Helm repo
helm repo add redpanda https://charts.redpanda.com
helm repo update

# Deploy Redpanda
helm install redpanda redpanda/redpanda \
  --namespace kafka \
  --create-namespace \
  --set resources.limits.cpu=2 \
  --set resources.limits.memory=4Gi \
  --set resources.requests.cpu=100m \
  --set resources.requests.memory=256Mi

# Create topics
kubectl exec -it redpanda-0 -n kafka -- \
  rpk topic create task-events \
  --partitions 3 \
  --replication-factor 1

kubectl exec -it redpanda-0 -n kafka -- \
  rpk topic create reminders \
  --partitions 3 \
  --replication-factor 1
```

**5.3 Dapr Installation**

```bash
# Initialize Dapr on OKE cluster
dapr init -k --runtime-version 1.14.0

# Verify Dapr system pods running
kubectl get pods -n dapr-system
```

**5.4 Deploy Application**

```bash
# Build and push images to registry (use GitHub Container Registry)
docker tag teamflow/backend:latest ghcr.io/yourusername/teamflow-backend:latest
docker tag teamflow/frontend:latest ghcr.io/yourusername/teamflow-frontend:latest
docker push ghcr.io/yourusername/teamflow-backend:latest
docker push ghcr.io/yourusername/teamflow-frontend:latest

# Deploy microservices images
# ... (repeat for notification, recurring-task, realtime-sync services)

# Install Helm chart with production values
helm install teamflow ./helm/teamflow \
  --namespace teamflow \
  --create-namespace \
  -f helm/teamflow/values-production.yaml \
  --set backend.image.tag=latest \
  --set frontend.image.tag=latest
```

**5.5 Configure Ingress**

```bash
# Use Oracle OKE's public IP
export LB_IP=$(kubectl get svc teamflow-ingress -n teamflow -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Update DNS (if domain available) or use IP directly
echo "TeamFlow deployed at: http://$LB_IP"
```

---

### Phase 6: CI/CD Pipeline (GitHub Actions)

**Objective**: Automate build, test, security scan, and deployment with approval gates.

**Workflow Stages**:

```yaml
# .github/workflows/deploy.yml
name: Deploy TeamFlow Phase 5

on:
  push:
    branches: [main, 005-advanced-cloud-deployment]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_PREFIX: ${{ github.repository }}

jobs:
  # Stage 1: Build & Test
  build-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Backend Tests
        run: |
          cd teamflow-web/backend
          pip install uv
          uv sync
          uv run pytest --cov=app tests/
      - name: Run Frontend Tests
        run: |
          cd teamflow-web/frontend
          npm ci
          npm test

  # Stage 2: Security Scanning
  security-scan:
    needs: build-and-test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build Backend Image
        run: docker build -t backend:test ./teamflow-web/backend
      - name: Run Trivy Scanner
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: backend:test
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'CRITICAL,HIGH'
      - name: Upload Results to GitHub Security
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'

  # Stage 3: Build & Push Images
  build-images:
    needs: security-scan
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4
      - name: Login to GHCR
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - name: Build & Push Backend
        uses: docker/build-push-action@v5
        with:
          context: ./teamflow-web/backend
          push: true
          tags: ${{ env.REGISTRY }}/${{ env.IMAGE_PREFIX }}/backend:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
      - name: Build & Push Frontend
        uses: docker/build-push-action@v5
        with:
          context: ./teamflow-web/frontend
          push: true
          tags: ${{ env.REGISTRY }}/${{ env.IMAGE_PREFIX }}/frontend:${{ github.sha }}
      - name: Build & Push Microservices
        run: |
          # Repeat for each microservice
          docker build -t ghcr.io/.../notification-service:${{ github.sha }} ./teamflow-web/backend/microservices/notification_service
          docker push ghcr.io/.../notification-service:${{ github.sha }}

  # Stage 4: Deploy to Staging
  deploy-staging:
    needs: build-images
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/005-advanced-cloud-deployment'
    steps:
      - uses: actions/checkout@v4
      - name: Configure kubectl
        run: |
          echo "${{ secrets.KUBE_CONFIG }}" | base64 -d > $HOME/.kube/config
      - name: Deploy via Helm
        run: |
          helm upgrade --install teamflow ./helm/teamflow \
            --namespace teamflow-staging \
            --create-namespace \
            --set backend.image.tag=${{ github.sha }} \
            --set frontend.image.tag=${{ github.sha }} \
            --set environment=staging

  # Stage 5: Integration Tests (Staging)
  integration-tests:
    needs: deploy-staging
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run E2E Tests
        run: |
          # Use Playwright or Cypress to test staging environment
          cd teamflow-web/frontend
          npm ci
          npx playwright test --project=staging

  # Stage 6: Production Deployment (Manual Approval)
  deploy-production:
    needs: integration-tests
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment:
      name: production
      url: https://teamflow.example.com
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to OKE Production
        run: |
          helm upgrade --install teamflow ./helm/teamflow \
            --namespace teamflow-production \
            --create-namespace \
            -f helm/teamflow/values-production.yaml \
            --set backend.image.tag=${{ github.sha }}
```

**Secrets Required in GitHub**:
- `KUBE_CONFIG`: Base64-encoded kubeconfig file for OKE cluster
- `OCI_API_KEY`: Oracle Cloud API key for cluster management (optional)
- `SENDGRID_API_KEY`: Email service credentials
- `DATABASE_URL`: Neon PostgreSQL connection string (if not using Dapr secrets)

---

## Success Criteria Validation

| Criteria | Measurement | Success Threshold |
|----------|-------------|-------------------|
| **SC-001**: Deployment time | Time from `helm install` to all pods Running | < 10 minutes |
| **SC-002**: Concurrent users | Load test with k6 or Locust | 100 concurrent users, < 1s p95 response |
| **SC-003**: Real-time propagation | WebSocket event publish → client receive | < 2 seconds |
| **SC-004**: Reminder delivery rate | Emails sent / reminders due | > 95% success rate |
| **SC-005**: Recurring task creation | Task completion → next instance in DB | < 30 seconds |
| **SC-006**: CI/CD duration | GitHub Actions workflow execution | < 15 minutes (excluding approval wait) |
| **SC-007**: Security scanning | Trivy/Grypose scan results | 100% of images scanned, critical vulns block |
| **SC-008**: Uptime | Kubernetes pod uptime over 7 days | > 99.5% |
| **SC-009**: HPA scaling | CPU > 70% → new pod scheduled | < 2 minutes |
| **SC-010**: Zero downtime | Rolling update with active users | 0 HTTP 5xx errors during update |

---

## Risk Assessment & Mitigation

| Risk | Probability | Impact | Mitigation Strategy |
|------|-------------|--------|---------------------|
| **Oracle OKE Always Free limits exceeded** | Medium | High | Monitor resource usage via `kubectl top`. Set up resource quotas. Have GKE/AKS backup plan. |
| **Redpanda cluster fails** | Low | High | Deploy Redpanda with 3 replicas (if resources allow). Implement event replay from Kafka retention period. |
| **Dapr sidecar crashes** | Low | Medium | Configure liveness/readiness probes for daprd container. Set `dapr.io/sidecar-cpu-request` and `sidecar-memory-request`. |
| **Email provider rate limiting** | Medium | Medium | Implement exponential backoff retry. Queue failed messages in dead letter topic. Alert on delivery failures. |
| **WebSocket connection exhaustion** | Medium | High | Implement connection pooling, limit max connections per pod. Auto-scale based on active connections. |
| **CI/CD pipeline failures** | Low | High | Use matrix builds for testing multiple Python/Node versions. Keep GitHub Actions updated. Monitor quota usage. |
| **Database migration failures** | Low | High | Use Alembic for incremental migrations. Test migrations on staging first. Implement rollback migrations. |
| **Event ordering issues** | Medium | Medium | Use Kafka partitioning by task_id for ordering. Implement idempotent event handlers. |
| **Secrets leakage in logs** | Low | High | Configure structured logging with sanitization. Use Dapr secrets store (never log secret values). |
| **Hackathon deadline pressure** | High | High | Prioritize P1-P3 user stories. Cut M-P4 (voice commands) if time constrained. Focus on working demo over perfection. |

---

## Next Steps

After this plan is approved:

1. **Execute Phase 0 Research**: Document all technology choices in `research.md`
2. **Generate Tasks**: Run `/sp.tasks` to create actionable implementation tasks
3. **Begin Implementation**: Start with Phase 2 (Dapr local setup) before cloud deployment
4. **Track Progress**: Update tasks.md as items are completed
5. **Create PHR**: Document plan completion with `.specify/scripts/bash/create-phr.sh`

**Estimated Implementation Timeline**:
- **Phase 0 Research**: 1 day
- **Phase 1 Data Model**: 1 day
- **Phase 2 Dapr Integration**: 2 days
- **Phase 3 Microservices**: 3 days
- **Phase 4 Frontend**: 2 days
- **Phase 5 Cloud Deploy**: 2 days
- **Phase 6 CI/CD**: 1 day
- **Testing & Validation**: 1 day

**Total**: 13 days (recommend 2-week sprint)

**Critical Path**: Phase 2 → Phase 3 → Phase 5 (Dapr → Microservices → Cloud Deploy)

---

**Document Status**: Draft - Ready for research phase execution
