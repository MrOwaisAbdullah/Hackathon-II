# Phase 4: TeamFlow Local Kubernetes Deployment - Complete Implementation Prompt

You are acting as the **Cloud-Native DevOps Engineer** for TeamFlow. Your goal is to containerize and deploy the TeamFlow application to a local Kubernetes cluster using Minikube.

---

## Context

We are implementing **Phase IV: Local Kubernetes Deployment** of the TeamFlow Agency CRM Hackathon.
The full-stack application (Next.js frontend + FastAPI backend) is already built and working locally.
This phase focuses on **containerization, Helm chart creation, and Minikube deployment**.

**Hackathon Points:** 250 pts
**Deadline:** January 18, 2026

---

## MANDATORY: Use Cloud-Native Blueprints Skill

Before any implementation, **READ AND APPLY** the cloud-native-blueprints skill:
```
@.claude/skills/cloud-native-blueprints/SKILL.md
```

This skill contains:
- Helm chart templates and structure
- Dapr component configurations
- AIOps command patterns (kubectl-ai, kagent, Gordon)
- Production-ready deployment patterns

**Use the templates from:**
- `@.claude/skills/cloud-native-blueprints/assets/templates/` for Helm chart YAML files
- `@.claude/skills/cloud-native-blueprints/assets/components/` for Dapr configurations
- `@.claude/skills/cloud-native-blueprints/references/` for best practices

---

## MANDATORY: Research First

Before implementing, use MCP tools for research:

**For Library/Framework Documentation:**
```
context7 resolve-library-id "helm" → get-library-docs
context7 resolve-library-id "kubernetes" → get-library-docs
```

**For Best Practices and Troubleshooting:**
```
tavily search "Docker multi-stage build FastAPI Python 3.13 2025"
tavily search "Next.js standalone Docker Kubernetes deployment"
tavily search "Minikube Helm deployment best practices"
```

---

## Current State Analysis

### Application Architecture
| Component | Technology | Port | Status |
|-----------|------------|------|--------|
| Frontend | Next.js 14 | 3000 | ✅ Running locally |
| Backend | FastAPI | 8000 | ✅ Running locally |
| Database | Neon PostgreSQL | External | ✅ Connected |

### Existing Files
| File | Location | Status |
|------|----------|--------|
| Backend Dockerfile | `teamflow-web/backend/Dockerfile` | ⚠️ Needs optimization |
| Frontend Dockerfile | `teamflow-web/frontend/Dockerfile` | ❌ Missing |
| next.config.ts | `teamflow-web/frontend/next.config.ts` | ⚠️ Needs `output: 'standalone'` |
| Helm charts | `helm/teamflow/` | ❌ Missing |

---

## Hackathon Requirements (250 pts)

| Requirement | Implementation | AIOps Tool |
|-------------|----------------|------------|
| Containerize frontend and backend | Multi-stage Dockerfiles | **Gordon** |
| Use Docker AI Agent (Gordon) | Document all `docker ai` commands | **Gordon** |
| Create Helm charts for deployment | Generate with AI assistance | **kubectl-ai** |
| Use kubectl-ai for K8s operations | Document all commands | **kubectl-ai** |
| Use Kagent for cluster analysis | Document usage | **Kagent** |
| Deploy on Minikube locally | Full stack deployment | All tools |

---

## Implementation Tasks

### Part 1: Docker Containerization (Use Gordon)

#### Task 1.1: Frontend Dockerfile

**File:** `teamflow-web/frontend/Dockerfile` (CREATE)

**Requirements:**
- Multi-stage build for smaller image
- Node.js 22 Alpine base
- Next.js standalone output mode
- Non-root user for security
- Optimized layer caching

**Gordon Commands to Run and Document:**
```bash
docker ai "create optimized Dockerfile for Next.js 14 standalone production build"
docker ai "what base image is best for Next.js production in 2025"
docker ai "optimize this Dockerfile for smaller image size"
```

**Expected Dockerfile Structure:**
```dockerfile
# Stage 1: Dependencies
FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
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

#### Task 1.2: Update Next.js Config

**File:** `teamflow-web/frontend/next.config.ts` (MODIFY)

Add to the config object:
```typescript
output: 'standalone',
```

This enables the optimized standalone build for Docker.

#### Task 1.3: Backend Dockerfile Optimization

**File:** `teamflow-web/backend/Dockerfile` (MODIFY)

**Gordon Commands to Run and Document:**
```bash
docker ai "optimize this FastAPI Dockerfile for production"
docker ai "create multi-stage build for Python 3.13 uv package manager"
```

**Requirements:**
- Multi-stage build
- Python 3.13 slim base
- UV package manager for fast installs
- Non-root user
- Health check endpoint

#### Task 1.4: Create .dockerignore Files

**Files to Create:**
- `teamflow-web/frontend/.dockerignore`
- `teamflow-web/backend/.dockerignore`

```
node_modules/
.next/
*.log
.env.local
.git/
```

---

### Part 2: Helm Chart Creation (Use kubectl-ai)

#### Task 2.1: Initialize Helm Chart Structure

**Directory:** `helm/teamflow/`

**kubectl-ai Commands to Run and Document:**
```bash
kubectl-ai "create helm chart structure for a Next.js frontend and FastAPI backend"
kubectl-ai "generate values.yaml for multi-container deployment"
```

**Required Structure:**
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

#### Task 2.2: Chart.yaml

**File:** `helm/teamflow/Chart.yaml`

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

#### Task 2.3: values.yaml

**File:** `helm/teamflow/values.yaml`

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
  resources:
    limits:
      cpu: 500m
      memory: 512Mi
    requests:
      cpu: 100m
      memory: 128Mi
  env:
    NEXT_PUBLIC_API_URL: "http://teamflow-backend:8000"

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
  resources:
    limits:
      cpu: 1000m
      memory: 1Gi
    requests:
      cpu: 200m
      memory: 256Mi

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

#### Task 2.4: Deployment Templates

Use templates from `@.claude/skills/cloud-native-blueprints/assets/templates/`

**Create:**
- `templates/frontend-deployment.yaml`
- `templates/backend-deployment.yaml`
- `templates/frontend-service.yaml`
- `templates/backend-service.yaml`

Include:
- Proper labels and selectors
- Resource limits
- Health probes (liveness/readiness)
- Environment variables from ConfigMap/Secrets

#### Task 2.5: Secrets Template

**File:** `helm/teamflow/templates/secrets.yaml`

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

---

### Part 3: Minikube Deployment

#### Task 3.1: Start Minikube

```bash
# Start with sufficient resources
minikube start --cpus=4 --memory=8192 --driver=docker

# Enable required addons
minikube addons enable ingress
minikube addons enable metrics-server

# Verify cluster status
minikube status
```

#### Task 3.2: Build Images in Minikube

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

#### Task 3.3: Deploy with Helm

**kubectl-ai Commands to Run and Document:**
```bash
kubectl-ai "install helm chart from ./helm/teamflow to namespace teamflow"
kubectl-ai "verify all pods are running in teamflow namespace"
```

**Manual Commands:**
```bash
# Create secrets file (do not commit!)
cat > helm/teamflow/secrets.yaml << EOF
secrets:
  databaseUrl: "postgresql://user:pass@host/db"
  openaiApiKey: "sk-..."
  betterAuthSecret: "your-secret-here"
EOF

# Install Helm chart
helm install teamflow ./helm/teamflow \
  --namespace teamflow \
  --create-namespace \
  -f helm/teamflow/secrets.yaml

# Verify deployment
kubectl get pods -n teamflow
kubectl get services -n teamflow
```

#### Task 3.4: Access Application

```bash
# Get Minikube IP
minikube ip

# Add to hosts file (optional)
echo "$(minikube ip) teamflow.local" | sudo tee -a /etc/hosts

# Or use minikube service
minikube service teamflow-frontend -n teamflow
```

---

### Part 4: Cluster Analysis (Use Kagent)

#### Task 4.1: Health Check

**Kagent Commands to Run and Document:**
```bash
kagent "analyze the cluster health and identify any issues"
kagent "check resource utilization in teamflow namespace"
kagent "verify service connectivity between frontend and backend"
```

#### Task 4.2: Optimization Suggestions

```bash
kagent "suggest optimizations for the teamflow deployment"
kagent "identify any security concerns in current configuration"
```

---

## AIOps Documentation Requirement

**CRITICAL:** Document ALL AIOps commands used in a file:

**File:** `docs/PHASE4-AIOPS-COMMANDS.md`

```markdown
# Phase 4: AIOps Commands Documentation

## Docker AI (Gordon)

### Commands Used
| Command | Purpose | Result |
|---------|---------|--------|
| `docker ai "optimize this Dockerfile"` | Image optimization | Reduced size by X% |
| ... | ... | ... |

## kubectl-ai

### Commands Used
| Command | Purpose | Result |
|---------|---------|--------|
| `kubectl-ai "deploy backend with 2 replicas"` | Initial deployment | Created deployment |
| ... | ... | ... |

## Kagent

### Commands Used
| Command | Purpose | Result |
|---------|---------|--------|
| `kagent "analyze cluster health"` | Health check | All systems healthy |
| ... | ... | ... |
```

---

## Success Criteria

### Containerization
- [ ] Frontend Dockerfile created with multi-stage build
- [ ] Backend Dockerfile optimized
- [ ] `next.config.ts` has `output: 'standalone'`
- [ ] Both images build successfully
- [ ] Images are under 500MB each

### Helm Charts
- [ ] Chart structure created
- [ ] `values.yaml` properly configured
- [ ] All templates render without errors (`helm template`)
- [ ] Chart passes linting (`helm lint`)

### Minikube Deployment
- [ ] Minikube cluster running
- [ ] All pods in Running state
- [ ] Services accessible via port-forward or ingress
- [ ] Frontend can communicate with backend
- [ ] Backend can connect to Neon database

### AIOps Documentation
- [ ] All Gordon commands documented
- [ ] All kubectl-ai commands documented
- [ ] All Kagent commands documented
- [ ] Results and outcomes recorded

---

## Verification Steps

### 1. Validate Dockerfiles
```bash
cd teamflow-web/backend && docker build -t teamflow/backend:test .
cd teamflow-web/frontend && docker build -t teamflow/frontend:test .
```

### 2. Validate Helm Chart
```bash
helm lint ./helm/teamflow
helm template teamflow ./helm/teamflow --debug
```

### 3. Verify Running Application
```bash
# Check pods
kubectl get pods -n teamflow

# Check logs
kubectl logs -l app=teamflow-frontend -n teamflow
kubectl logs -l app=teamflow-backend -n teamflow

# Test health endpoints
kubectl port-forward svc/teamflow-backend 8000:8000 -n teamflow
curl http://localhost:8000/health

# Test frontend
kubectl port-forward svc/teamflow-frontend 3000:3000 -n teamflow
# Open http://localhost:3000 in browser
```

---

## Files to Create/Modify

| Action | File | Description |
|--------|------|-------------|
| CREATE | `teamflow-web/frontend/Dockerfile` | Multi-stage Next.js build |
| MODIFY | `teamflow-web/frontend/next.config.ts` | Add `output: 'standalone'` |
| MODIFY | `teamflow-web/backend/Dockerfile` | Optimize for production |
| CREATE | `helm/teamflow/Chart.yaml` | Chart metadata |
| CREATE | `helm/teamflow/values.yaml` | Configuration values |
| CREATE | `helm/teamflow/templates/*.yaml` | K8s manifests |
| CREATE | `docs/PHASE4-AIOPS-COMMANDS.md` | AIOps documentation |

---

## Output Requirement

1. All containerization completed with working Dockerfiles
2. Helm chart created and validated
3. Application deployed and accessible on Minikube
4. All AIOps commands documented for hackathon submission
5. Verification steps passed

**Remember:** This is a hackathon requirement. Focus on getting a WORKING deployment first, then optimize.
