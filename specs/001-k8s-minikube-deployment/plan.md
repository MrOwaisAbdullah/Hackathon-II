# Architecture Plan: TeamFlow Kubernetes Deployment on Minikube

**Feature Branch**: `001-k8s-minikube-deployment`
**Created**: 2026-01-18
**Status**: Draft
**Spec Reference**: [spec.md](./spec.md)

---

## 1. Architecture Overview

### 1.1 System Context

TeamFlow is a full-stack agency CRM application consisting of:
- **Frontend**: Next.js 14 (React-based, port 3000)
- **Backend**: FastAPI (Python 3.13, port 8000)
- **Database**: Neon PostgreSQL (external, managed service)

This deployment package containerizes the application and deploys it to a local Minikube Kubernetes cluster using Helm charts.

### 1.2 High-Level Architecture

```
┌───────────────────────── MINIKUBE CLUSTER ─────────────────────────┐
│                                                                           │
│  ┌────────────────────────── Namespace: teamflow ──────────────────────┐ │
│  │                                                                    │  │
│  │  ┌─────────────────────────────────────────────────────────────┐   │  │
│  │  │                    Ingress Controller                        │   │  │
│  │  │                    (nginx ingress addon)                    │   │  │
│  │  │                             │                             │   │  │
│  │  │  ┌────────────────────────────────────────┐  ┌──────────────┐  │   │  │
│  │  │  │                                        │  │              │  │   │  │
│  │  │  │  ┌──────────┐        ┌──────────┐  │  │              │  │   │  │
│  │  │  │  │Frontend  │        │ Backend  │  │  │              │  │   │  │
│  │  │  │Deployment│        │Deployment│  │  │              │  │   │  │
│  │  │  │  │ 2 replicas│        │ 2 replicas│  │  │──────────────┘  │   │  │
│  │  │  │  │          │        │          │  │  │ ClusterIP       │  │   │  │
│  │  │  │  └──────────┘        └──────────┘  │  │  Services       │  │   │  │
│  │  │  │          │                │          │  │  │                │  │   │  │
│  │  │  │          │                │          │  │  └────────────────┘  │   │  │
│  │  │  └─────────────────────────────────────────────────────┘  │  │
│  │  │                                                           │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                           │
                ┌────────────────────────────────┐
                │  External: Neon PostgreSQL    │
                │  (Managed PostgreSQL Service)   │
                └────────────────────────────────┘
```

### 1.3 Component Responsibilities

| Component | Responsibility | Technology |
|-----------|----------------|------------|
| **Frontend Deployment** | Serve Next.js application, handle UI routing | Next.js 14, Node.js 22 |
| **Backend Deployment** | Serve FastAPI application, handle API routes | FastAPI, Python 3.13 |
| **Frontend Service** | ClusterIP service for frontend pod access | Kubernetes Service |
| **Backend Service** | ClusterIP service for backend pod access | Kubernetes Service |
| **Ingress Controller** | External access routing via host-based routing | NGINX (Minikube addon) |
| **Kubernetes Secrets** | Store sensitive configuration (DATABASE_URL, API keys) | Kubernetes Secrets |
| **ConfigMap** | Store non-sensitive configuration | Kubernetes ConfigMap |

### 1.4 Data Flow

```
User Browser
    │
    ├─► Ingress Controller (teamflow.local)
    │
    ├─► Frontend Service (ClusterIP:3000)
    │         │
    │         └─► Frontend Pods (2 replicas)
    │                │
    │                └─► Next.js Application (Port 3000)
    │                     │
    │                     ├─► API Calls (/api/*)
    │                     │
    └─────────────────────┘
                              │
                              ▼
                     Backend Service (ClusterIP:8000)
                              │
                              └─► Backend Pods (2 replicas)
                                      │
                                      └─► FastAPI Application (Port 8000)
                                          │
                                          ├─► Database Queries
                                          │
                                          ▼
                              Neon PostgreSQL (External)
```

---

## 2. Implementation Phases

### Phase 1: Containerization (FR-001 to FR-010)

**Objective**: Create production-ready Docker images for frontend and backend with multi-stage builds and security best practices.

#### Task 1.1: Create Frontend Dockerfile
- **File**: `teamflow-web/frontend/Dockerfile` (CREATE)
- **Requirements**: FR-001, FR-002, FR-003, FR-004
- **Implementation**:
  ```dockerfile
  # Stage 1: Dependencies
  FROM node:22-alpine AS deps
  WORKDIR /app
  COPY package.json package-lock.json* ./
  RUN npm ci

  # Stage 2: Builder
  FROM node:22-alpine AS builder
  WORKDIR /app
  COPY --from=deps /app/node_modules ./node_modules
  COPY . .
  ENV NEXT_TELEMETRY_DISABLED=1
  RUN npm run build

  # Stage 3: Runner
  FROM node:22-alpine AS runner
  WORKDIR /app
  ENV NODE_ENV=production
  RUN addgroup --system --gid 1001 nodejs
  RUN adduser --system --uid 1001 nextjs
  COPY --from=builder /app/public ./public
  COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
  COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
  USER nextjs
  EXPOSE 3000
  CMD ["node", "server.js"]
  ```

#### Task 1.2: Modify next.config.ts
- **File**: `teamflow-web/frontend/next.config.ts` (MODIFY)
- **Requirements**: FR-010
- **Change**: Add `output: 'standalone'` to config object

#### Task 1.3: Optimize Backend Dockerfile
- **File**: `teamflow-web/backend/Dockerfile` (MODIFY)
- **Requirements**: FR-005, FR-006, FR-007
- **Implementation**:
  ```dockerfile
  # Stage 1: Dependencies
  FROM python:3.13-slim AS deps
  WORKDIR /app
  COPY pyproject.toml uv.lock* ./
  RUN pip install --no-cache-dir uv && uv sync

  # Stage 2: Builder
  FROM python:3.13-slim AS builder
  WORKDIR /app
  COPY --from=deps /app/.venv ./app/.venv
  COPY pyproject.toml uv.lock* ./
  COPY . .
  RUN uv sync

  # Stage 3: Runner
  FROM python:3.13-slim AS runner
  WORKDIR /app
  RUN addgroup --system --gid 1001 appuser && \
      adduser --system --uid 1001 appuser
  COPY --from=builder /app/.venv ./app/.venv
  COPY --chown=appuser:appuser /app/app ./app
  USER appuser
  EXPOSE 8000
  HEALTHCHECK --interval=30s --timeout=3s --start-period=5s \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health').raise_for_status(200)"
  CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
  ```

#### Task 1.4: Create .dockerignore Files
- **Files**:
  - `teamflow-web/frontend/.dockerignore` (CREATE)
  - `teamflow-web/backend/.dockerignore` (CREATE)
- **Requirements**: FR-009
- **Content**:
  ```
  node_modules/
  .next/
  *.log
  .env.local
  .git/
  __pycache__/
  *.py[cod]
  .pytest_cache/
  .coverage
  .venv/
  ```

#### Task 1.5: Validate Image Sizes
- **Requirement**: FR-008
- **Commands**:
  ```bash
  docker images | grep teamflow-frontend
  docker images | grep teamflow-backend
  ```
- **Acceptance**: Both images < 500MB

---

### Phase 2: Helm Chart Development (FR-011 to FR-021)

**Objective**: Create a production-ready Helm chart with all required templates, configuration, and validation.

#### Task 2.1: Initialize Chart Structure
- **Directory**: `helm/teamflow/`
- **Requirements**: FR-011
- **Structure**:
  ```
  helm/teamflow/
  ├── Chart.yaml
  ├── values.yaml
  ├── templates/
  │   ├── _helpers.tpl
  │   ├── namespace.yaml
  │   ├── frontend-deployment.yaml
  │   ├── frontend-service.yaml
  │   ├── backend-deployment.yaml
  │   ├── backend-service.yaml
  │   ├── configmap.yaml
  │   ├── secrets.yaml
  │   └── ingress.yaml
  ```

#### Task 2.2: Create Chart.yaml
- **File**: `helm/teamflow/Chart.yaml`
- **Requirements**: FR-011
- **Content**:
  ```yaml
  apiVersion: v2
  name: teamflow
  description: TeamFlow Agency CRM - Full-Stack Application
  version: 1.0.0
  appVersion: "1.0"
  type: application
  keywords:
    - teamflow
    - crm
    - agency
    - task-management
  ```

#### Task 2.3: Create values.yaml
- **File**: `helm/teamflow/values.yaml`
- **Requirements**: FR-011
- **Content**:
  ```yaml
  namespace: teamflow

  frontend:
    name: teamflow-frontend
    replicaCount: 2
    image:
      repository: teamflow/frontend
      tag: latest
      pullPolicy: IfNotPresent
    service:
      type: ClusterIP
      port: 3000
      targetPort: 3000
    resources:
      limits:
        cpu: 500m
        memory: 512Mi
      requests:
        cpu: 100m
        memory: 128Mi
    env:
      NEXT_PUBLIC_API_URL: "http://teamflow-backend:8000"
    livenessProbe:
      httpGet:
        path: /
        port: http
      initialDelaySeconds: 30
      periodSeconds: 10
      timeoutSeconds: 5
      successThreshold: 1
      failureThreshold: 3
    readinessProbe:
      httpGet:
        path: /
        port: http
      initialDelaySeconds: 5
      periodSeconds: 5
      timeoutSeconds: 3
      successThreshold: 1
      failureThreshold: 3

  backend:
    name: teamflow-backend
    replicaCount: 2
    image:
      repository: teamflow/backend
      tag: latest
      pullPolicy: IfNotPresent
    service:
      type: ClusterIP
      port: 8000
      targetPort: 8000
    resources:
      limits:
        cpu: 1000m
        memory: 1Gi
      requests:
        cpu: 200m
        memory: 256Mi
    livenessProbe:
      httpGet:
        path: /health
        port: http
      initialDelaySeconds: 30
      periodSeconds: 10
      timeoutSeconds: 5
      successThreshold: 1
      failureThreshold: 3
    readinessProbe:
      httpGet:
        path: /ready
        port: http
      initialDelaySeconds: 5
      periodSeconds: 5
      timeoutSeconds: 3
      successThreshold: 1
      failureThreshold: 3

  secrets:
    databaseUrl: ""  # Set via --set or secrets file
    openaiApiKey: ""
    betterAuthSecret: ""

  ingress:
    enabled: true
    className: nginx
    hosts:
      - host: teamflow.local
        paths:
          - path: /
            pathType: Prefix
            service: frontend
          - path: /api
            pathType: Prefix
            service: backend
  ```

#### Task 2.4: Create Namespace Template
- **File**: `helm/teamflow/templates/namespace.yaml`
- **Content**:
  ```yaml
  apiVersion: v1
  kind: Namespace
  metadata:
    name: {{ .Values.namespace }}
    labels:
      name: {{ .Values.namespace }}
  ```

#### Task 2.5: Create Deployment Templates
- **Files**:
  - `helm/teamflow/templates/frontend-deployment.yaml`
  - `helm/teamflow/templates/backend-deployment.yaml`
- **Requirements**: FR-012, FR-014, FR-015
- **Key Features**:
  - Rolling update strategy (maxUnavailable: 0, maxSurge: 1)
  - Resource limits with CPU throttling and memory OOM kill
  - Liveness and readiness probes
  - Non-root user security

#### Task 2.6: Create Service Templates
- **Files**:
  - `helm/teamflow/templates/frontend-service.yaml`
  - `helm/teamflow/templates/backend-service.yaml`
- **Requirements**: FR-013
- **Content**: ClusterIP services exposing ports 3000 and 8000

#### Task 2.7: Create Secrets Template
- **File**: `helm/teamflow/templates/secrets.yaml`
- **Requirements**: FR-018
- **Content**:
  ```yaml
  apiVersion: v1
  kind: Secret
  metadata:
    name: teamflow-secrets
    namespace: {{ .Values.namespace }}
  type: Opaque
  stringData:
    DATABASE_URL: {{ .Values.secrets.databaseUrl | quote }}
    OPENAI_API_KEY: {{ .Values.secrets.openaiApiKey | quote }}
    BETTER_AUTH_SECRET: {{ .Values.secrets.betterAuthSecret | quote }}
  ```

#### Task 2.8: Create ConfigMap Template
- **File**: `helm/teamflow/templates/configmap.yaml`
- **Content**:
  ```yaml
  apiVersion: v1
  kind: ConfigMap
  metadata:
    name: teamflow-config
    namespace: {{ .Values.namespace }}
  data:
    NEXT_PUBLIC_API_URL: {{ .Values.frontend.env.NEXT_PUBLIC_API_URL | quote }}
  ```

#### Task 2.9: Create Ingress Template
- **File**: `helm/teamflow/templates/ingress.yaml`
- **Requirements**: FR-016
- **Content**:
  ```yaml
  apiVersion: networking.k8s.io/v1
  kind: Ingress
  metadata:
    name: teamflow-ingress
    namespace: {{ .Values.namespace }}
    annotations:
      nginx.ingress.kubernetes.io/rewrite-target: /
  spec:
    ingressClassName: {{ .Values.ingress.className }}
    rules:
    - host: {{ .Values.ingress.hosts[0].host }}
      http:
        paths:
          - path: {{ .Values.ingress.hosts[0].paths[0].path }}
            pathType: {{ .Values.ingress.hosts[0].paths[0].pathType }}
            backend:
              service:
                name: {{ .Values.ingress.hosts[0].paths[0].service }}
                port:
                  number: {{ .Values.frontend.service.port }}
          - path: {{ .Values.ingress.hosts[1].paths[0].path }}
            pathType: {{ .Values.ingress.hosts[1].paths[0].pathType }}
            backend:
              service:
                name: {{ .Values.ingress.hosts[1].paths[0].service }}
                port:
                  number: {{ .Values.backend.service.port }}
  ```

#### Task 2.10: Create Template Helpers
- **File**: `helm/teamflow/templates/_helpers.tpl`
- **Content**: Standard Helm template helpers (labels, selector labels, fullname)

#### Task 2.11: Validate Chart
- **Requirements**: FR-019, FR-020
- **Commands**:
  ```bash
  helm lint ./helm/teamflow
  helm template teamflow ./helm/teamflow --debug
  ```
- **Acceptance**: Zero errors, zero warnings

---

### Phase 3: Minikube Deployment (FR-022 to FR-032)

**Objective**: Deploy the containerized application to Minikube with proper configuration and verification.

#### Task 3.1: Configure Minikube Cluster
- **Requirements**: FR-022, FR-023, FR-024
- **Commands**:
  ```bash
  # Start Minikube with sufficient resources
  minikube start --cpus=4 --memory=8192 --driver=docker

  # Enable required addons
  minikube addons enable ingress
  minikube addons enable metrics-server

  # Verify cluster status
  minikube status
  kubectl get nodes
  ```

#### Task 3.2: Build Images in Minikube
- **Requirements**: FR-025
- **Commands**:
  ```bash
  # Use Minikube's Docker daemon
  eval $(minikube docker-env)

  # Build backend image
  cd teamflow-web/backend
  docker build -t teamflow/backend:latest .

  # Build frontend image
  cd ../frontend
  docker build -t teamflow/frontend:latest .

  # Verify images
  docker images | grep teamflow
  ```
  - **Acceptance**: Both images exist in Minikube Docker daemon

#### Task 3.3: Create Secrets File
- **File**: `helm/teamflow/secrets.yaml` (not committed to git)
- **Content**:
  ```yaml
  secrets:
    databaseUrl: "postgresql://user:pass@host/db"
    openaiApiKey: "sk-..."
    betterAuthSecret: "your-secret-here"
  ```

#### Task 3.4: Deploy Helm Chart
- **Requirements**: FR-026, FR-027
- **Commands**:
  ```bash
  # Install Helm chart
  helm install teamflow ./helm/teamflow \
    --namespace teamflow \
    --create-namespace \
    -f helm/teamflow/secrets.yaml

  # Verify deployment
  kubectl get pods -n teamflow
  kubectl get services -n teamflow
  ```
- - **Acceptance**: All pods in Running state within 5 minutes

#### Task 3.5: Verify Service Access
- **Requirements**: FR-028, FR-029
- **Commands**:
  ```bash
  # Port-forward to backend
  kubectl port-forward svc/teamflow-backend 8000:8000 -n teamflow

  # Test health endpoint
  curl http://localhost:8000/health

  # Port-forward to frontend
  kubectl port-forward svc/teamflow-frontend 3000:3000 -n teamflow

  # Test frontend in browser
  # Open http://localhost:3000
  ```
- - **Acceptance**: Both services accessible, health endpoint returns 200

#### Task 3.6: Validate Database Connection
- **Requirements**: FR-030, FR-032
- **Verification**:
  - Check backend logs for successful database connection
  - Test application login and data persistence

#### Task 3.7: Test Frontend-Backend Communication
- **Requirements**: FR-031
- **Verification**:
  - Access frontend in browser
  - Login and navigate to dashboard
  - Create a task and verify it persists

---

### Phase 4: Validation & Documentation (FR-033 to FR-038)

**Objective**: Validate end-to-end functionality and document all AIOps commands used.

#### Task 4.1: E2E Functionality Testing
- **Requirements**: US-3 (User Story 3)
- **Test Cases**:
  1. Load login page without errors
  2. Login and navigate to dashboard
  3. Create new task and verify persistence
  4. Test database operations (read/write)

#### Task 4.2: Document AIOps Commands
- **Requirements**: FR-033 to FR-038
- **File**: `docs/PHASE4-AIOPS-COMMANDS.md`
- **Content**:
  ```markdown
  # Phase 4: AIOps Commands Documentation

  ## Docker AI (Gordon)

  ### Commands Used
  | Command | Purpose | Result |
  |---------|---------|--------|
  | `docker ai "create optimized Dockerfile for Next.js 14"` | Frontend image optimization | Multi-stage build implemented |
  | `docker ai "optimize FastAPI Dockerfile for production"` | Backend image optimization | Multi-stage build implemented |
  | ... | ... | ... |

  ## kubectl-ai

  ### Commands Used
  | Command | Purpose | Result |
  |---------|---------|--------|
  | `kubectl-ai "create helm chart for TeamFlow deployment"` | Chart structure generated | Templates created |
  | ... | ... | ... |

  ## Kagent

  ### Commands Used
  | Command | Purpose | Result |
  |---------|---------|--------|
  | `kagent "analyze cluster health and suggest optimizations"` | Cluster analysis | Recommendations applied |
  | ... | ... | ... |
  ```

#### Task 4.3: Verify All Success Criteria
- **Requirements**: SC-001 to SC-012
- **Verification Matrix** (see Section 6)

---

## 3. Technical Decisions

### 3.1 Base Image Selection

**Frontend: `node:22-alpine`**
- **Rationale**: Alpine Linux is significantly smaller than standard images (~5MB vs ~100MB), provides Node.js 22 LTS support, and maintains compatibility with Next.js 14. The Alpine variant is battle-tested for production deployments and offers security advantages due to minimal attack surface.

**Backend: `python:3.13-slim`**
- **Rationale**: Python 3.13 introduces improved performance and syntax features. The slim variant provides a balance between size (~130MB vs ~1GB for full image) and compatibility. UV package manager (required by constitution) is fully supported in Python 3.13, enabling fast dependency resolution during builds.

### 3.2 Health Check Strategy

**Liveness Probe**
- **Path**: `/health` (frontend), `/health` (backend)
- **Purpose**: Detect and restart unhealthy containers
- **Configuration**:
  - Initial delay: 30 seconds (allow application startup)
  - Period: 10 seconds (check every 10s)
  - Timeout: 5 seconds (fail fast)
  - Failure threshold: 3 consecutive failures before restart

**Readiness Probe**
- **Path**: `/` (frontend), `/ready` (backend)
- **Purpose**: Remove pods from service if not ready
- **Configuration**:
  - Initial delay: 5 seconds (fast initial check)
  - Period: 5 seconds (frequent checks for quick recovery)
  - Timeout: 3 seconds (fail fast)
  - Failure threshold: 3 consecutive failures

### 3.3 Resource Allocation

**Frontend Resources**:
- **Limits**: 500m CPU, 512Mi memory
- **Requests**: 100m CPU, 128Mi memory
- **Rationale**: Next.js build optimization and SSR require memory; CPU limits prevent resource starvation. The 2:1 limit:request ratio allows burst traffic handling.

**Backend Resources**:
- **Limits**: 1000m CPU, 1Gi memory
- **Requests**: 200m CPU, 256Mi memory
- **Rationale**: FastAPI with async operations benefits from CPU headroom. Python memory overhead requires higher baseline. 1Gi limit accommodates peak concurrent request handling.

### 3.4 Secret Management

**Approach**: Kubernetes Secrets with separate values file

**Rationale**:
- Kubernetes Secrets provide encrypted at-rest storage
- Separate `secrets.yaml` file (not committed to git) prevents accidental exposure
- Values passed via `helm install -f secrets.yaml` keeps secrets out of values.yaml
- Supports multiple environments (dev, staging, production) with different secret files

**Implementation**:
```bash
# Secrets file (gitignored)
cat > helm/teamflow/secrets.yaml << EOF
secrets:
  databaseUrl: "postgresql://..."
  openaiApiKey: "sk-..."
  betterAuthSecret: "..."
EOF

# Deployment
helm install teamflow ./helm/teamflow -f helm/teamflow/secrets.yaml
```

### 3.5 Service Exposure

**Approach**: ClusterIP services + Ingress for external access

**Rationale**:
- **ClusterIP** for internal service-to-service communication (standard K8s pattern)
- **Ingress** for external access (eliminates NodePort port conflicts)
- Ingress controller (Minikube addon) provides HTTP routing without manual port management
- Supports path-based routing (`/` → frontend, `/api/*` → backend)

**Alternative Considered**:
- LoadBalancer: Not suitable for local Minikube (requires cloud provider)
- NodePort: Conflicts with local ports, requires manual port management

### 3.6 Replica Strategy

**Configuration**: 2 replicas for both frontend and backend

**Rolling Update Strategy**:
```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxUnavailable: 0          # Zero downtime
    maxSurge: 1               # One extra pod during update
```

**Rationale**:
- 2 replicas provide high availability during updates
- `maxUnavailable: 0` ensures zero downtime during rolling updates (SC-011)
- `maxSurge: 1` allows surge capacity for graceful shutdown
- Readiness probes ensure only healthy pods receive traffic

---

## 4. Edge Case Handling

| Edge Case | Mitigation Strategy |
|-----------|---------------------|
| **Minikube resource exhaustion** | Pre-flight check: Verify 4 CPUs and 8GB RAM available. Command: `minikube config` to view current settings. |
| **Neon PostgreSQL unreachable** | Exponential backoff retry (1s, 2s, 4s, 8s, 16s, max 30s). After timeout, return user-friendly error: "Database temporarily unavailable. Please try again." Backend logs retry attempts with jitter. |
| **Docker build failure** | Clear error message indicating specific missing dependency or build error. Suggest dependency installation commands. Enable build caching with `.dockerignore` optimization. |
| **Pod restart during traffic** | Zero-downtime rolling update strategy. Readiness probes ensure new pods are ready before old pods terminate. Service mesh or HA proxy not required for 2-replica deployment. |
| **Helm install failure** | Pre-deployment validation using `helm template --debug`. Dry-run identifies YAML syntax errors, missing values, or template rendering issues before actual deployment. |
| **Missing environment variables** | Fail-fast startup with descriptive error message indicating which variable is missing. Kubernetes validates required env vars before scheduling pods. |
| **Ingress misconfiguration** | Test service access via port-forward first (`kubectl port-forward`) to isolate ingress issues. Add DNS entry (`/etc/hosts` on Linux/Mac, `C:\Windows\System32\drivers\etc\hosts` on Windows) for local testing. |
| **Resource limits exceeded** | CPU throttling (performance degrades gracefully). Memory OOM kills container and triggers pod restart via deployment controller. Horizontal Pod Autoscaler can scale based on metrics. |

---

## 5. File Structure

### Complete File Tree

```
teamflow-web/
├── frontend/
│   ├── Dockerfile              # CREATE - Multi-stage Next.js build
│   ├── .dockerignore           # CREATE - Exclude dev artifacts
│   └── next.config.ts          # MODIFY - Add output: 'standalone'
│
├── backend/
│   ├── Dockerfile              # MODIFY - Optimize multi-stage build
│   └── .dockerignore           # CREATE - Exclude dev artifacts
│
helm/
└── teamflow/
    ├── Chart.yaml              # CREATE - Chart metadata (v2, 1.0.0)
    ├── values.yaml             # CREATE - Default configuration with resource limits
    ├── secrets.yaml             # CREATE - Secret values (gitignored)
    └── templates/
        ├── _helpers.tpl        # CREATE - Template helpers (labels, selectors)
        ├── namespace.yaml      # CREATE - Namespace definition
        ├── frontend-deployment.yaml   # CREATE - Deployment with 2 replicas
        ├── frontend-service.yaml      # CREATE - ClusterIP service port 3000
        ├── backend-deployment.yaml    # CREATE - Deployment with 2 replicas
        ├── backend-service.yaml       # CREATE - ClusterIP service port 8000
        ├── configmap.yaml             # CREATE - Environment variables
        ├── secrets.yaml               # CREATE - Kubernetes Secret (database URL, API keys)
        └── ingress.yaml               # CREATE - Ingress routing rules

docs/
└── PHASE4-AIOPS-COMMANDS.md    # CREATE - AIOps documentation (Gordon, kubectl-ai, Kagent)
```

### File Descriptions

#### Docker Files

**Frontend Dockerfile** (`teamflow-web/frontend/Dockerfile`)
- 3-stage build (deps → builder → runner)
- Stage 1 installs dependencies with `npm ci`
- Stage 2 builds Next.js standalone application
- Stage 3 runs as non-root user with minimal attack surface

**Backend Dockerfile** (`teamflow-web/backend/Dockerfile`)
- 3-stage build (deps → builder → runner)
- Stage 1 installs dependencies with `uv sync`
- Stage 2 builds application and copies virtual environment
- Stage 3 runs as non-root user with health check

**.dockerignore files**
- Exclude development artifacts (node_modules, __pycache__, .venv)
- Exclude test and build artifacts
- Exclude logs and environment files

#### Helm Chart Files

**Chart.yaml**
- Helm v2 format with metadata
- Version 1.0.0, appVersion 1.0
- Type: application

**values.yaml**
- Namespace: teamflow
- Frontend: 2 replicas, 500m CPU/512Mi limits
- Backend: 2 replicas, 1000m CPU/1Gi limits
- Resource requests configured (CPU throttling, memory OOM)
- Health probe configurations
- Ingress enabled for teamflow.local

**Templates**
- **_helpers.tpl**: Standard Helm template helpers
- **namespace.yaml**: Creates teamflow namespace
- **frontend-deployment.yaml**: Frontend deployment with rolling update strategy
- **frontend-service.yaml**: ClusterIP service on port 3000
- **backend-deployment.yaml**: Backend deployment with rolling update strategy
- **backend-service.yaml**: ClusterIP service on port 8000
- **configmap.yaml**: Non-sensitive environment configuration
- **secrets.yaml**: Kubernetes Secret for sensitive data (not committed)
- **ingress.yaml**: Ingress routing rules

---

## 6. Verification Matrix

| Criteria | Command | Expected Result | Success Criterion |
|----------|---------|-----------------|-----------------|
| SC-001 | `docker images | grep teamflow` | Size < 500MB each | Image size under 500MB |
| SC-002 | `helm template teamflow ./helm/teamflow --debug` | No errors | Templates render successfully |
| SC-003 | `helm lint ./helm/teamflow` | 0 warnings, 0 errors | Helm chart passes linting |
| SC-004 | `kubectl get pods -n teamflow -w` | Running < 5 min | Pods Running within 5 minutes |
| SC-005 | `curl -w "%{time_total}" http://localhost:3000 -o /dev/null` | < 3s | Frontend loads in under 3 seconds |
| SC-006 | `curl -w "%{time_total}" http://localhost:8000/health -o /dev/null` | < 500ms | Health endpoint responds in under 500ms |
| SC-007 | Check backend logs for database connection | "Database connected" or equivalent | DB connection succeeds on first attempt |
| SC-008 | Manual E2E testing in browser | Login works, dashboard loads, task persistence | Full user flow works |
| SC-009 | Create task via deployed UI and refresh | Task appears in list | Task persistence works |
| SC-010 | Documentation file contains all AIOps commands | All Gordon, kubectl-ai, Kagent commands documented | AIOps commands documented |
| SC-011 | `kubectl rollout restart deployment/teamflow-backend -n teamflow` during user activity | No 5xx errors in browser logs | Zero downtime rolling update |
| SC-012 | `kubectl top -n teamflow` | Resources within limits | Resource usage within defined limits |

---

## 7. Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Minikube incompatibility** | Low | High | Test on Windows/Mac/Linux before hackathon deadline. Document Minikube version requirements (v1.34.0+). |
| **Image size exceeds 500MB** | Medium | Medium | Use multi-stage builds, .dockerignore optimization, alpine base images. Monitor with `docker images` command. |
| **Database connection fails** | Medium | High | Implement exponential backoff retry (FR-032). Validate connection string format. Provide user-friendly error messages. |
| **Helm validation fails** | Low | Low | Run `helm lint` and `helm template` before install. Use `--dry-run` flag for testing. |
| **Deadline pressure** | Medium | High | Prioritize P1-P2 user stories. M-P1 is containerization (blocks everything). M-P2 is Minikube deployment (blocks P3/P4). |
| **Resource limits exceeded** | Low | Medium | Configure appropriate requests/limits. Monitor with `kubectl top`. Implement horizontal pod autoscaler if needed (future enhancement). |
| **Ingress routing issues** | Medium | Medium | Test with port-forward first. Validate DNS configuration. Use clear host naming conventions. |
| **Startup time exceeds 5 minutes** | Low | Medium | Log warning but continue deployment (per clarification). Investigate slow image pulls or dependency resolution. |
| **AIOps tools unavailable** | Low | Low | Document commands used even if tools unavailable. Use manual equivalent commands as fallback. |

---

## 8. Implementation Order

### 8.1 Dependency Graph

```mermaid
graph TD
    A[1.1 Frontend Dockerfile] --> B[1.5 Validate Images]
    C[1.2 next.config.ts] --> B
    D[1.3 Backend Dockerfile] --> B
    E[1.4 .dockerignore files] --> B

    B --> F[2.1 Chart.yaml/values.yaml]
    F --> G[2.2 Namespace Template]

    H[2.3 Frontend Deployment Template] --> I[2.7 Validate Chart]
    I[2.4 Frontend Service Template] --> I
    J[2.5 Backend Deployment Template] --> I
    K[2.6 Backend Service Template] --> I
    L[2.8 Secrets Template] --> I
    M[2.9 ConfigMap Template] --> I
    N[2.10 Ingress Template] --> I

    I --> O[3.1 Configure Minikube]
    O --> P[3.2 Build Images in Minikube]
    P --> Q[3.3 Deploy Helm Chart]
    Q --> R[3.4 Verify Pod Status]
    R --> S[3.5 Test Service Access]
    S --> T[3.6 Validate DB Connection]
    T --> U[3.7 Test Frontend-Backend Comm]

    U --> V[4.1 E2E Functionality Testing]
    V --> W[4.2 Document AIOps Commands]
    W --> X[4.3 Verify All Success Criteria]
```

### 8.2 Sequential Execution

**Phase 1: Containerization**
1. Create frontend `.dockerignore`
2. Create backend `.dockerignore`
3. Modify `next.config.ts` (add `output: 'standalone'`)
4. Create frontend `Dockerfile`
5. Optimize backend `Dockerfile`
6. Build both images locally to validate
7. Verify image sizes

**Phase 2: Helm Chart Development**
1. Create `helm/teamflow/` directory structure
2. Create `Chart.yaml` with metadata
3. Create `values.yaml` with default configuration
4. Create `_helpers.tpl` with template helpers
5. Create `namespace.yaml`
6. Create `frontend-deployment.yaml` and `frontend-service.yaml`
7. Create `backend-deployment.yaml` and `backend-service.yaml`
8. Create `configmap.yaml` for environment variables
9. Create `secrets.yaml` template
10. Create `ingress.yaml` for external access
11. Run `helm lint ./helm/teamflow`
12. Run `helm template teamflow ./helm/teamflow --debug`

**Phase 3: Minikube Deployment**
1. Start Minikube with required configuration
2. Enable ingress and metrics-server addons
3. Create `secrets.yaml` file (not committed)
4. Build images in Minikube Docker daemon
5. Install Helm chart with secrets
6. Monitor pod startup
7. Verify services and pods
8. Port-forward to test access
9. Validate database connection
10. Test frontend-backend communication

**Phase 4: Validation & Documentation**
1. Perform end-to-end testing
2. Document all Gordon commands used
3. Document all kubectl-ai commands used
4. Document all Kagent commands used
5. Verify all success criteria
6. Create AIOps documentation file

---

## 9. Technical Context

### 9.1 Constitution Compliance

✅ **SOLID Principles**: Helm templates follow single responsibility, secrets follow dependency inversion
✅ **DRY Applied**: Reuses cloud-native-blueprints skill templates
✅ **TDD Ready**: Verification matrix provides testability
✅ **Type Safety**: TypeScript (frontend), Python type hints (backend)
✅ **Security**: Non-root containers, secrets management, no secrets in git
✅ **Performance**: Resource limits defined, probes configured
✅ **MCP Tools**: Context7 and Tavily used for research

### 9.2 Technology Stack

| Component | Technology | Version | Purpose |
|-----------|----------|--------|---------|
| Frontend | Next.js | 14 | React-based UI framework |
| Backend | FastAPI | 0.115+ | Python web framework |
| Container Runtime | Docker | Latest | Containerization |
| Orchestration | Kubernetes | 1.29+ | Container orchestration |
| Package Manager | Helm | 3.0+ | K8s package manager |
| Local Cluster | Minikube | 1.34.0+ | Local K8s for development |
| Python Package | UV | Latest | Fast Python dependency manager |
| Node Package | npm | Latest | JavaScript dependency manager |

### 9.3 External Dependencies

| Dependency | Purpose | URL |
|-----------|---------|-----|
| Neon PostgreSQL | Database | https://neon.tech |
| Cloud-Native Blueprints Skill | Helm/K8s patterns | `.claude/skills/cloud-native-blueprints/` |
| Next.js Documentation | Frontend framework | https://nextjs.org/docs |
| FastAPI Documentation | Backend framework | https://fastapi.tiangolo.com/ |
| Helm Documentation | Package manager | https://helm.sh/docs/ |
| Kubernetes Documentation | Orchestration | https://kubernetes.io/docs/ |

---

## 10. Rollback Procedures

### 10.1 Helm Rollback

```bash
# Check release history
helm list -n teamflow

# Rollback to previous revision
helm rollback teamflow 1 -n teamflow

# Verify rollback
kubectl get pods -n teamflow
```

### 10.2 Image Rollback

```bash
# Tag specific image version
docker build -t teamflow/backend:v1.0 .

# Update values.yaml
helm upgrade teamflow ./helm/teamflow \
  --set backend.image.tag=v1.0 \
  -n teamflow
```

### 10.3 Full Cleanup

```bash
# Uninstall Helm release
helm uninstall teamflow -n teamflow

# Delete namespace
kubectl delete namespace teamflow

# Delete images (optional)
docker rmi teamflow/frontend:latest
docker rmi teamflow/backend:latest
```

---

## 11. Troubleshooting Guide

### 11.1 Common Issues and Solutions

**Issue: Pods stuck in Pending state**
- **Check**: `kubectl describe pod <pod-name> -n teamflow`
- **Causes**: Image pull failure, resource insufficient, node selector mismatch
- **Solution**: Verify image is built in Minikube Docker daemon, check resource availability

**Issue: Health checks failing**
- **Check**: `kubectl logs <pod-name> -n teamflow -c <container>`
- **Causes**: Application crash, port mismatch, probe timing
- **Solution**: Adjust probe timing, verify application health endpoint

**Issue: Frontend cannot reach backend**
- **Check**: `kubectl exec -it <frontend-pod> -n teamflow -- sh -c 'curl http://teamflow-backend:8000/health'`
- **Causes**: Service discovery, network policies, wrong API URL
- **Solution**: Verify NEXT_PUBLIC_API_URL, check service DNS, review network policies

**Issue: Database connection fails**
- **Check**: Backend logs for connection errors
- **Causes**: Wrong connection string, network policy, external database blocked
- **Solution**: Verify DATABASE_URL secret, check network egress policies, test connectivity with psql client

### 11.2 Useful Commands

```bash
# Port forward for local testing
kubectl port-forward svc/teamflow-frontend 3000:3000 -n teamflow
kubectl port-forward svc/teamflow-backend 8000:8000 -n teamflow

# View logs
kubectl logs -l app=teamflow-frontend -n teamflow --tail=100
kubectl logs -l app=teamflow-backend -n teamflow --tail=100

# Describe resources for debugging
kubectl describe pod <pod-name> -n teamflow
kubectl describe deployment teamflow-frontend -n teamflow
kubectl describe service teamflow-frontend -n teamflow

# Exec into container for debugging
kubectl exec -it <pod-name> -n teamflow -- /bin/sh

# Check resource usage
kubectl top -n teamflow
kubectl describe node minikube
```

---

## 12. Success Criteria Validation

### 12.1 Pre-Deployment Checklist

- [ ] Frontend Dockerfile created and tested locally
- [ ] Backend Dockerfile created and tested locally
- [ ] `next.config.ts` has `output: 'standalone'`
- [ ] Both images under 500MB
- [ ] Helm chart structure created
- [ ] `values.yaml` configured
- [ ] All templates created
- [ ] Helm chart passes linting
- [ ] Helm templates render without errors
- [ ] Minikube cluster running with 4 CPUs, 8GB RAM
- [ ] Ingress addon enabled
- - Metrics-server addon enabled
- [ ] Secrets file created (not committed)
- [ ] Application codebase ready

### 12.2 Post-Deployment Verification

- [ ] All pods in Running state
- [ ] All pods Ready (1/1)
- [ ] Frontend service accessible via port-forward or ingress
- [ ] Backend service accessible via port-forward
- [ ] Health endpoint responding < 500ms
- [ ] Database connection successful
- [ ] Frontend-backend communication working
- [ ] Rolling updates tested successfully (zero downtime)
- [ ] AIOps commands documented
- [ ] All success criteria validated

---

## 13. Next Steps

After architecture plan approval:

1. **Review and approve plan.md**
2. **Proceed to `/sp.tasks`** to generate actionable implementation tasks
3. **Begin implementation** following the phased approach
4. **Create PHR** for plan completion

**Estimated Implementation Time**: 4-6 hours (excluding research and validation)
**Critical Path**: Phase 1 → Phase 2 → Phase 3 → Phase 4 (sequential dependencies)

---

**Document Status**: Draft - Ready for review and tasks generation
