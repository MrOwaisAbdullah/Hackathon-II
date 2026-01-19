# TeamFlow - Complete Local Development Guide with Minikube

**Last Updated:** January 20, 2026
**Environment:** WSL2 + Docker Desktop + Minikube + Helm

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Building Docker Images](#building-docker-images)
4. [Deploying to Minikube](#deploying-to-minikube)
5. [Running the Application](#running-the-application)
6. [Development Workflow](#development-workflow)
7. [Common Commands](#common-commands)
8. [Troubleshooting](#troubleshooting)
9. [Architecture Overview](#architecture-overview)

---

## Prerequisites

### Required Software

| Software | Purpose | Installation Check |
|----------|---------|-------------------|
| **Docker Desktop** | Container runtime | `docker --version` |
| **Minikube** | Local K8s cluster | `~/.local/bin/minikube version` |
| **Helm** | K8s package manager | `~/.local/bin/helm version` |
| **WSL2** | Linux environment | `wsl --version` |

### Quick Install Commands

If you don't have these installed:

```bash
# Minikube (Linux)
curl -Lo minikube https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
chmod +x minikube
sudo mv minikube ~/.local/bin/

# Helm (Linux)
curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
chmod +x get_helm.sh
./get_helm.sh
```

---

## Initial Setup

### Step 1: Start Minikube

```bash
~/.local/bin/minikube start --driver=docker --cpus=4 --memory=6000
```

**Expected Output:**
```
✅ Minikube started
🟉  Kubernetes is available at https://127.0.0.1:XXXXX
```

**Verify:**
```bash
~/.local/bin/minikube status
```

Should show:
```
type: Control Plane
host: Running
kubelet: Running
apiserver: Running
kubeconfig: Configured
```

---

## Building Docker Images

### Step 2: Build Frontend Image

```bash
cd "/mnt/d/GIAIC/Quarter 4/Hackathon II"

# Build with Windows Docker (faster)
docker.exe build --no-cache --build-arg NEXT_PUBLIC_API_URL="" \
  -t teamflow/frontend:minikube \
  -f teamflow-web/frontend/Dockerfile \
  teamflow-web/frontend/
```

**Build time:** ~5-7 minutes (first run), ~2-3 minutes (cached)

---

### Step 3: Build Backend Image

```bash
# Build with Windows Docker
docker.exe build --no-cache \
  -t teamflow/backend:latest \
  -f teamflow-web/backend/Dockerfile \
  teamflow-web/backend/
```

**Build time:** ~3-5 minutes

---

### Step 4: Load Images into Minikube

```bash
# Transfer images from Windows Docker to Minikube Docker
docker.exe save teamflow/frontend:minikube teamflow/backend:latest | \
  (eval "$(minikube docker-env)" && docker load)
```

**Expected Output:**
```
Loaded image: teamflow/frontend:minikube
Loaded image: teamflow/backend:latest
```

**Verify images are in Minikube:**
```bash
eval "$(minikube docker-env)"
docker images | grep teamflow
```

---

## Deploying to Minikube

### Step 5: Create Namespace

```bash
~/.local/bin/kubectl create namespace teamflow --dry-run=client -o yaml | \
  ~/.local/bin/kubectl apply -f -
```

---

### Step 6: Deploy with Helm

```bash
~/.local/bin/helm install teamflow ./helm/teamflow --namespace teamflow
```

**Expected Output:**
```
NAME: teamflow
LAST DEPLOYED: Tue Jan 20 XX:XX:XX 2026
NAMESPACE: teamflow
STATUS: deployed
REVISION: 1
TEST SUITE: None
```

---

### Step 7: Wait for Pods to be Ready

```bash
# Watch pod status
~/.local/bin/kubectl get pods -n teamflow -w
```

**Expected Output:**
```
NAME                                READY   STATUS    RESTARTS   AGE
teamflow-backend-xxxxx-xxxxx   0/1     Pending   0          5s
teamflow-backend-xxxxx-xxxxx   0/1     Running   0          30s
teamflow-frontend-xxxxx-xxxxx  0/1     Pending   0          5s
teamflow-frontend-xxxxx-xxxxx  0/1     Running   0          30s
```

Wait until both pods show `2/2` or `1/1` READY.

---

## Running the Application

### Step 8: Start Frontend Service Tunnel

**Option A: Using WSL Terminal**
```bash
cd "/mnt/d/GIAIC/Quarter 4/Hackathon II"
~/.local/bin/minikube service teamflow-frontend -n teamflow
```

**Option B: Using Windows Batch File**
Double-click: `start-frontend.bat`

**Expected Output:**
```
* service teamflow/teamflow-frontend has no node port
http://127.0.0.1:46615
```

**⚠️ Keep this terminal/window open!** The tunnel must stay running.

---

### Step 9: Access the Application

1. Open your browser
2. Go to the URL shown (e.g., `http://127.0.0.1:46615`)
3. Navigate to `/login`

**Test Credentials:**
```
Email: admin@test.com
Password: password123
```

---

## Development Workflow

### Making Frontend Code Changes

1. Edit files in `teamflow-web/frontend/src/`

2. Rebuild Docker image:
```bash
docker.exe build --build-arg NEXT_PUBLIC_API_URL="" \
  -t teamflow/frontend:minikube \
  -f teamflow-web/frontend/Dockerfile \
  teamflow-web/frontend/

docker.exe save teamflow/frontend:minikube | \
  (eval "$(minikube docker-env)" && docker load)
```

3. Restart deployment:
```bash
~/.local/bin/kubectl rollout restart deployment teamflow-frontend -n teamflow
```

4. Refresh browser (hard refresh: `Ctrl+Shift+R`)

---

### Making Backend Code Changes

1. Edit files in `teamflow-web/backend/app/`

2. Rebuild Docker image:
```bash
docker.exe build -t teamflow/backend:latest \
  -f teamflow-web/backend/Dockerfile \
  teamflow-web/backend/

docker.exe save teamflow/backend:latest | \
  (eval "$(minikube docker-env)" && docker load)
```

3. Restart deployment:
```bash
~/.local/bin/kubectl rollout restart deployment teamflow-backend -n teamflow
```

---

### Updating Environment Variables

1. Edit `helm/teamflow/values.yaml` (local file, gitignored)
2. Apply changes:
```bash
~/.local/bin/helm upgrade teamflow ./helm/teamflow --namespace teamflow
```

---

### Running Database Migrations

```bash
cd teamflow-web/backend
DATABASE_URL="postgresql://neondb_owner:npg_4u6wxICjUqTW@ep-shiny-hall-a1mjei2a-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require" \
  alembic upgrade head
```

---

## Common Commands

### Check Cluster Status

```bash
# Overall Minikube status
~/.local/bin/minikube status

# All pods in teamflow namespace
~/.local/bin/kubectl get pods -n teamflow

# Services
~/.local/bin/kubectl get svc -n teamflow

# Deployments
~/.local/bin/kubectl get deployments -n teamflow
```

---

### View Logs

```bash
# Frontend logs (follow)
~/.local/bin/kubectl logs -f deployment/teamflow-frontend -n teamflow

# Backend logs (follow)
~/.local/bin/kubectl logs -f deployment/teamflow-backend -n teamflow

# Last 50 lines
~/.local/bin/kubectl logs deployment/teamflow-backend -n teamflow --tail=50

# Logs from specific pod
~/.local/bin/kubectl logs -f teamflow-backend-xxxxx-xxxxx -n teamflow
```

---

### Restart Services

```bash
# Restart frontend
~/.local/bin/kubectl rollout restart deployment teamflow-frontend -n teamflow

# Restart backend
~/.local/bin/kubectl rollout restart deployment/teamflow-backend -n teamflow

# Rollback to previous revision
~/.local/bin/helm rollback teamflow -n teamflow
```

---

### Scale Replicas

```bash
# Scale frontend to 3 replicas
~/.local/bin/kubectl scale deployment teamflow-frontend -n teamflow --replicas=3

# Scale backend to 3 replicas
~/.local/bin/kubectl scale deployment teamflow-backend -n teamflow --replicas=3

# Scale back to 1
~/.local/bin/kubectl scale deployment teamflow-backend -n teamflow --replicas=1
```

---

### Exec into Pods

```bash
# Get shell access to frontend pod
~/.local/bin/kubectl exec -it -n teamflow deployment/teamflow-frontend -- sh

# Get shell access to backend pod
~/.local/bin/kubectl exec -it -n teamflow deployment/teamflow-backend -- sh

# Run Python command in backend pod
~/.local/bin/kubectl exec -n teamflow deployment/teamflow-backend -- python -c "print('Hello')"
```

---

### Resource Monitoring

```bash
# Pod resource usage
~/.local/bin/kubectl top pods -n teamflow

# Node resource usage
~/.local/bin/kubectl top nodes

# Describe pod for details
~/.local/bin/kubectl describe pod teamflow-backend-xxxxx-xxxxx -n teamflow
```

---

### Minikube Management

```bash
# Start Minikube
~/.local/bin/minikube start --driver=docker --cpus=4 --memory=6000

# Stop Minikube (when done working)
~/.local/bin/minikube stop

# Delete cluster (if needed)
~/.local/bin/minikube delete --all --purge

# Open Dashboard
~/.local/bin/minikube dashboard
```

---

### Helm Operations

```bash
# List releases
~/.local/bin/helm list -n teamflow

# Get rendered manifests (dry-run)
~/.local/bin/helm template teamflow ./helm/teamflow -n teamflow

# Upgrade with new values
~/.local/bin/helm upgrade teamflow ./helm/teamflow -n teamflow

# Rollback to previous version
~/.local/bin/helm rollback teamflow -n teamflow

# Uninstall release
~/.local/bin/helm uninstall teamflow -n teamflow
```

---

## Troubleshooting

### Issue: "Minikube command not found"

**Solution:**
```bash
# Use full path
~/.local/bin/minikube status

# Or add to PATH (in ~/.bashrc)
export PATH="$PATH:$HOME/.local/bin"
```

---

### Issue: "Pods stuck in ImagePullBackOff"

**Cause:** Images not available in Minikube Docker

**Solution:**
```bash
# 1. Verify images are in Minikube Docker
eval "$(minikube docker-env)"
docker images | grep teamflow

# 2. If not found, rebuild and load images
# (See Building Docker Images section above)

# 3. Delete pods to force re-pull
~/.local/bin/kubectl delete pod -n teamflow -l app.kubernetes.io/component=frontend
~/.local/bin/kubectl delete pod -n teamflow -l app.kubernetes.io/component=backend
```

---

### Issue: "Login not working / API errors"

**Check 1: Backend is running**
```bash
~/.local/bin/kubectl get pods -n teamflow -l app.kubernetes.io/component=backend
```

**Check 2: Backend logs**
```bash
~/.local/bin/kubectl logs -f deployment/teamflow-backend -n teamflow --tail=50
```

**Check 3: Test API directly**
```bash
# Get backend service URL
~/.local/bin/minikube service teamflow-backend -n teamflow --url

# Test login
curl -X POST http://127.0.0.1:XXXXX/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@test.com","password":"password123"}'
```

**Check 4: Frontend API proxy**
```bash
# Test through frontend proxy
curl -X POST http://127.0.0.1:XXXXX/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@test.com","password123"}'
```

---

### Issue: "Frontend showing old code"

**Solution:**
```bash
~/.local/bin/kubectl rollout restart deployment teamflow-frontend -n teamflow
```

Wait 30 seconds and hard refresh browser (`Ctrl+Shift+R`).

---

### Issue: "Database connection errors"

**Solution:**
```bash
# Test connection from local machine
psql "postgresql://neondb_owner:npg_4u6wxICjUqTW@ep-shiny-hall-a1mjei2a-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"

# Or run migrations
cd teamflow-web/backend
DATABASE_URL="postgresql://..." alembic upgrade head
```

---

### Issue: "Service tunnel URL changed after restart"

**Explanation:** Minikube service tunnel URLs change when:
- Minikube restarts
- Pods are recreated
- Computer restarts

**Solution:** Run the service command again to get the new URL:
```bash
~/.local/bin/minikube service teamflow-frontend -n teamflow
```

---

### Issue: "502 Bad Gateway / 503 Service Unavailable"

**Solution:**
```bash
# 1. Check pods
~/.local/bin/kubectl get pods -n teamflow

# 2. Check services
~/.local/bin/kubectl get svc -n teamflow

# 3. Check pod resource usage
~/.local/bin/kubectl top pods -n teamflow

# 4. Restart affected service
~/.local/bin/kubectl rollout restart deployment/teamflow-backend -n teamflow
```

---

### Issue: "Minikube keeps stopping"

**Solution:**
```bash
# 1. Check available memory
free -h

# 2. Reduce memory if needed
~/.local/bin/minikube stop
~/.local/bin/minikube start --driver=docker --cpus=4 --memory=5000

# 3. Or delete and recreate
~/.local/bin/minikube delete --all --purge
~/.local/bin/minikube start --driver=docker --cpus=4 --memory=6000
```

---

## Architecture Overview

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
│  → Host: ep-shiny-hall-a1mjei2a-pooler.ap-southeast-1...    │
└─────────────────────────────────────────────────────────────┘
```

**Key Points:**
- Browser only sees `http://127.0.0.1:46615` (no knowledge of K8s)
- Frontend proxies `/api/*` requests to backend via internal K8s DNS
- Backend connects to external Neon PostgreSQL
- All services use `ClusterIP` (not exposed externally)

---

## File Locations

| Component | Location |
|-----------|----------|
| **Frontend Source** | `teamflow-web/frontend/src/` |
| **Frontend Dockerfile** | `teamflow-web/frontend/Dockerfile` |
| **Backend Source** | `teamflow-web/backend/app/` |
| **Backend Dockerfile** | `teamflow-web/backend/Dockerfile` |
| **Helm Charts** | `helm/teamflow/templates/` |
| **Configuration** | `helm/teamflow/values.yaml` (gitignored, local only) |
| **Example Config** | `helm/teamflow/values.yaml.example` (in git) |
| **API Proxy** | `teamflow-web/frontend/src/app/api/[...path]/route.ts` |

---

## Quick Reference

### Complete Startup Sequence

```bash
# 1. Start Minikube
~/.local/bin/minikube start --driver=docker --cpus=4 --memory=6000

# 2. Build frontend image
docker.exe build --build-arg NEXT_PUBLIC_API_URL="" \
  -t teamflow/frontend:minikube \
  -f teamflow-web/frontend/Dockerfile \
  teamflow-web/frontend/

# 3. Build backend image
docker.exe build -t teamflow/backend:latest \
  -f teamflow-web/backend/Dockerfile \
  teamflow-web/backend/

# 4. Load images into Minikube
docker.exe save teamflow/frontend:minikube teamflow/backend:latest | \
  (eval "$(minikube docker-env)" && docker load)

# 5. Deploy (first time only)
~/.local/bin/helm install teamflow ./helm/teamflow --namespace teamflow

# 6. Or upgrade (if already deployed)
~/.local/bin/helm upgrade teamflow ./helm/teamflow --namespace teamflow

# 7. Wait for pods
~/.local/bin/kubectl get pods -n teamflow -w

# 8. Start service tunnel
~/.local/bin/minikube service teamflow-frontend -n teamflow

# 9. Open browser to shown URL
```

### Daily Development

```bash
# After making code changes:
docker.exe build --build-arg NEXT_PUBLIC_API_URL="" \
  -t teamflow/frontend:minikube \
  -f teamflow-web/frontend/Dockerfile \
  teamflow-web/frontend/

docker.exe save teamflow/frontend:minikube | \
  (eval "$(minikube docker-env)" && docker load)

~/.local/bin/kubectl rollout restart deployment teamflow-frontend -n teamflow
```

### Shutdown

```bash
# Stop service tunnel (press Ctrl+C)

# Stop Minikube (when done)
~/.local/bin/minikube stop

# Or keep Minikube running for next session
```

---

## Getting Help

### Check System Health

```bash
# 1. Minikube status
~/.local/bin/minikube status

# 2. All pods
~/.local/bin/kubectl get pods -n teamflow

# 3. Recent events
~/.local/bin/kubectl get events -n teamflow --sort-by='.lastTimestamp'

# 4. Frontend logs
~/.local/bin/kubectl logs -f deployment/teamflow-frontend -n teamflow

# 5. Backend logs
~/.local/bin/kubectl logs -f deployment/teamflow-backend -n teamflow
```

### Useful Aliases (add to ~/.bashrc)

```bash
# Minikube aliases
alias minikube='~/.local/bin/minikube'
alias kubectl='~/.local/bin/kubectl'
alias helm='~/.local/bin/helm'

# TeamFlow aliases
alias tf-pods='kubectl get pods -n teamflow'
alias tf-logs-frontend='kubectl logs -f deployment/teamflow-frontend -n teamflow'
alias tf-logs-backend='kubectl logs -f deployment/teamflow-backend -n teamflow'
alias tf-restart-frontend='kubectl rollout restart deployment teamflow-frontend -n teamflow'
alias tf-restart-backend='kubectl rollout restart deployment/teamflow-backend -n teamflow'
alias tf-frontend='minikube service teamflow-frontend -n teamflow'
```

---

## FAQ

**Q: Do I need to rebuild images for every code change?**
A: Yes. Docker images are immutable. After code changes, rebuild the image and restart the deployment.

**Q: Can I run multiple instances of TeamFlow locally?**
A: Yes, but you'll need to change the namespace name or use different Minikube profiles.

**Q: How do I update environment variables?**
A: Edit `helm/teamflow/values.yaml` and run `helm upgrade`.

**Q: My database tables are missing. What do I do?**
A: Run migrations: `alembic upgrade head` from the backend directory.

**Q: How do I access the backend directly without the frontend?**
A: Use `minikube service teamflow-backend -n teamflow` to get a direct URL.

**Q: Can I use this setup for production?**
A: This is for local development only. For production, use cloud Kubernetes (AKS/GKE) with external databases and proper secret management.

---

**Need More Help?**

- Check logs: `~/.local/bin/kubectl logs -f deployment/teamflow-backend -n teamflow`
- Check pods: `~/.local/bin/kubectl get pods -n teamflow`
- Check events: `~/.local/bin/kubectl get events -n teamflow --sort-by='.lastTimestamp'`
