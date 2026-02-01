# Quickstart Guide: TeamFlow Advanced Cloud Deployment (Phase 5)

**Feature**: 005-advanced-cloud-deployment | **Branch**: `005-advanced-cloud-deployment` | **Date**: 2026-01-29

---

## Overview

This guide provides step-by-step instructions for setting up and running the Phase 5 Advanced Cloud Deployment locally with Dapr, Kafka/Redpanda, and microservices.

---

## Prerequisites

### Required Software

| Tool | Version | Purpose | Installation |
|------|---------|---------|--------------|
| **Docker Desktop** | 4.53+ | Container runtime | https://www.docker.com/products/docker-desktop |
| **Minikube** | 1.34+ | Local Kubernetes cluster | https://minikube.sigs.k8s.io/docs/start/ |
| **kubectl** | Latest | K8s CLI | https://kubernetes.io/docs/tasks/tools/ |
| **Helm** | 3.0+ | K8s package manager | https://helm.sh/docs/intro/install/ |
| **Dapr CLI** | 1.14+ | Dapr runtime | https://docs.dapr.io/getting-started/install-dapr-cli/ |
| **Python** | 3.13+ | Backend runtime | https://www.python.org/downloads/ |
| **Node.js** | 20+ | Frontend runtime | https://nodejs.org/ |
| **uv** | Latest | Python package manager | `pip install uv` |
| **npm** | Latest | Node.js package manager | Included with Node.js |

### Required Services

| Service | URL | Purpose |
|---------|-----|---------|
| **Neon PostgreSQL** | `https://console.neon.tech` | External database (already configured from Phase II) |
| **SendGrid** | `https://sendgrid.com/` | Email service for reminders (free tier: 100 emails/day) |

---

## 1. Environment Setup

### 1.1 Clone Repository

```bash
git clone <repository-url>
cd teamflow-web
git checkout 005-advanced-cloud-deployment
```

### 1.2 Backend Environment Variables

Create `teamflow-web/backend/.env`:

```bash
# Database (from Phase II)
DATABASE_URL=postgresql://user:pass@ep-cool-us-east-1.aws.neon.tech/neondb?sslmode=require

# Better Auth (from Phase II)
BETTER_AUTH_SECRET=your-secret-key-here
BETTER_AUTH_URL=http://localhost:3000

# OpenAI API (from Phase III - for chatbot)
OPENAI_API_KEY=sk-...

# Dapr Configuration
DAPR_HTTP_PORT=3500
DAPR_GRPC_PORT=50001

# App Settings
ENV=development
LOG_LEVEL=debug

# Microservices Settings
NOTIFICATION_SERVICE_URL=http://notification-service.teamflow.svc.cluster.local:8000
RECURRING_TASK_SERVICE_URL=http://recurring-task-service.teamflow.svc.cluster.local:8000
REALTIME_SYNC_SERVICE_URL=http://realtime-sync-service.teamflow.svc.cluster.local:8000
```

### 1.3 Frontend Environment Variables

Create `teamflow-web/frontend/.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws/tasks
```

---

## 2. Start Minikube

### 2.1 Start Cluster

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

**Expected Output**:
```
minikube
type: Control Plane
host: Running
kubelet: Running
apiserver: Running
kubeconfig: Configured
```

---

### 2.2 Use Minikube's Docker Daemon

```bash
# Point shell to Minikube's Docker daemon
eval $(minikube docker-env)

# Verify
docker images | grep node
# Should show empty or different from local Docker
```

---

## 3. Install Dapr

### 3.1 Initialize Dapr on Minikube

```bash
# Install Dapr to Kubernetes cluster
dapr init -k --runtime-version 1.14.0

# Verify Dapr system pods running
kubectl get pods -n dapr-system
```

**Expected Output**:
```
NAME                                     READY   STATUS    RESTARTS   AGE
dapr-dashboard-7c6d8f7f9c-x2v5q         1/1     Running   0          2m
dapr-operator-7d9f8f7c9c-x2v5q           1/1     Running   0          2m
dapr-placement-server-7f9d8f7c9c-x2v5q   1/1     Running   0          2m
dapr-sidecar-injector-7b9f8f7c9c-x2v5q   1/1     Running   0          2m
dapr-sentry-7c9f8f7c9c-x2v5q             1/1     Running   0          2m
```

---

### 3.2 Verify Dapr CLI

```bash
# Check Dapr version
dapr --version

# Expected: CLI version: 1.14.0, Runtime version: 1.14.0
```

---

## 4. Deploy Redpanda (Kafka)

### 4.1 Add Redpanda Helm Repository

```bash
helm repo add redpanda https://charts.redpanda.com
helm repo update
```

---

### 4.2 Deploy Redpanda

```bash
# Create namespace
kubectl create namespace kafka

# Deploy Redpanda
helm install redpanda redpanda/redpanda \
  --namespace kafka \
  --set replicas=1 \
  --set resources.limits.memory=2Gi \
  --set resources.requests.memory=256Mi \
  --set resources.limits.cpu=1 \
  --set resources.requests.cpu=100m

# Wait for Redpanda to be ready
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=redpanda -n kafka --timeout=300s
```

---

### 4.3 Verify Redpanda

```bash
# Check pod status
kubectl get pods -n kafka

# Expected: redpanda-0  Running
```

---

### 4.4 Create Kafka Topics

```bash
# Access Redpanda pod
kubectl exec -it redpanda-0 -n kafka -- bash

# Inside Redpanda pod, create topics
rpk topic create task-events --partitions 3 --replication-factor 1
rpk topic create reminders --partitions 3 --replication-factor 1
rpk topic create time-logged --partitions 1 --replication-factor 1
rpk topic create task-updates --partitions 3 --replication-factor 1

# Verify topics
rpk topic list

# Exit pod
exit
```

**Expected Output**:
```
NAME            PARTITIONS  REPLICAS
task-events     3           1
reminders       3           1
time-logged     1           1
task-updates    3           1
```

---

## 5. Deploy Dapr Components

### 5.1 Create Namespace

```bash
kubectl create namespace teamflow
```

---

### 5.2 Create Dapr Components

```bash
# Create directory for Dapr components
mkdir -p dapr-components

# Create pubsub component
cat > dapr-components/pubsub.kafka.yaml << 'EOF'
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
      value: "redpanda-0.redpanda-headless.kafka.svc.cluster.local:9092"
    - name: consumerGroup
      value: "teamflow-services"
    - name: authType
      value: "none"
    - name: initialOffset
      value: "newest"
EOF

# Create state store component
cat > dapr-components/state.postgresql.yaml << 'EOF'
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
        key: database-url
EOF

# Create secret store component
cat > dapr-components/secretstores.kubernetes.yaml << 'EOF'
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kubernetes-secrets
  namespace: teamflow
spec:
  type: secretstores.kubernetes
  version: v1
EOF

# Apply components
kubectl apply -f dapr-components/
```

---

### 5.3 Create Kubernetes Secrets

```bash
# Create secret with database URL and other sensitive values
kubectl create secret generic teamflow-secrets \
  --namespace teamflow \
  --from-literal=database-url='postgresql://user:pass@ep-cool-us-east-1.aws.neon.tech/neondb?sslmode=require' \
  --from-literal=openai-api-key='sk-...' \
  --from-literal=better-auth-secret='your-secret-key' \
  --from-literal=sendgrid-api-key='SG.YOUR_API_KEY'
```

---

## 6. Build Application Images

### 6.1 Build Backend Image

```bash
cd teamflow-web/backend

# Build image in Minikube's Docker daemon
docker build -t teamflow/backend:latest .

# Verify image
docker images | grep teamflow/backend
```

---

### 6.2 Build Frontend Image

```bash
cd teamflow-web/frontend

# Build image in Minikube's Docker daemon
docker build -t teamflow/frontend:latest .

# Verify image
docker images | grep teamflow/frontend
```

---

### 6.3 Build Microservice Images

```bash
# Notification Service
cd teamflow-web/backend/microservices/notification_service
docker build -t teamflow/notification-service:latest .

# Recurring Task Service
cd ../recurring_task_service
docker build -t teamflow/recurring-task-service:latest .

# Real-Time Sync Service
cd ../realtime_sync_service
docker build -t teamflow/realtime-sync-service:latest .
```

---

## 7. Deploy Application with Helm

### 7.1 Deploy Backend and Frontend

```bash
# Navigate to Helm chart directory
cd teamflow-web/helm/teamflow

# Install/upgrade Helm release
helm install teamflow ./helm/teamflow \
  --namespace teamflow \
  --create-namespace \
  --set backend.image.tag=latest \
  --set frontend.image.tag=latest \
  --set backend.dapr.enabled=true \
  --set frontend.dapr.enabled=true

# Wait for pods to be ready
kubectl wait --for=condition=ready pod -l app.kubernetes.io/instance=teamflow -n teamflow --timeout=300s
```

---

### 7.2 Deploy Microservices

```bash
# Deploy Notification Service
kubectl apply -f k8s/notification-service.yaml

# Deploy Recurring Task Service
kubectl apply -f k8s/recurring-task-service.yaml

# Deploy Real-Time Sync Service
kubectl apply -f k8s/realtime-sync-service.yaml

# Wait for all pods to be ready
kubectl get pods -n teamflow -w
```

**Expected Output**:
```
NAME                                      READY   STATUS    RESTARTS   AGE
teamflow-backend-7f9d8f7c9c-x2v5q        2/2     Running   0          5m
teamflow-frontend-7b9f8f7c9c-x2v5q        2/2     Running   0          5m
notification-service-7c9f8f7c9c-x2v5q      2/2     Running   0          2m
recurring-task-service-7d9f8f7c9c-x2v5q    2/2     Running   0          2m
realtime-sync-service-7e9f8f7c9c-x2v5q     2/2     Running   0          2m
```

**Note**: `2/2` in READY column indicates 2 containers per pod (app container + Dapr sidecar).

---

## 8. Access Application

### 8.1 Port-Forward to Frontend

```bash
# Port-forward frontend service
kubectl port-forward svc/teamflow-frontend 3000:3000 -n teamflow
```

### 8.2 Access in Browser

```bash
# Open browser to http://localhost:3000
# On Windows/Mac: start http://localhost:3000
# On Linux: xdg-open http://localhost:3000
```

---

### 8.3 Port-Forward to Backend (Optional)

```bash
# For direct API access
kubectl port-forward svc/teamflow-backend 8000:8000 -n teamflow

# Test health endpoint
curl http://localhost:8000/health

# Expected: {"status":"healthy"}
```

---

## 9. Test Event Streaming

### 9.1 Create Test Task

```bash
# Use frontend UI or API to create a task with recurrence
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Daily standup",
    "description": "Recurring daily standup meeting",
    "priority": "medium",
    "recurrence_rule": {
      "frequency": "daily",
      "interval": 1
    },
    "reminder_settings": {
      "offsets": ["1h"],
      "channels": ["email"]
    }
  }'
```

---

### 9.2 Monitor Kafka Topics

```bash
# Access Redpanda pod
kubectl exec -it redpanda-0 -n kafka -- bash

# Consume task-events topic
rpk topic consume task-events

# You should see task-created event appear
# Press Ctrl+C to exit

# Exit pod
exit
```

---

### 9.3 Verify Dapr Event Publishing

```bash
# Check backend logs for event publishing
kubectl logs -l app=teamflow-backend -n teamflow -c teamflow-backend --tail=50

# Expected: "Published event to topic task-events"
```

---

## 10. Test Recurring Task Service

### 10.1 Complete a Recurring Task

```bash
# Mark the daily standup task as complete
curl -X PATCH http://localhost:8000/api/v1/tasks/{task_id} \
  -H "Content-Type: application/json" \
  -d '{"status": "done"}'
```

---

### 10.2 Verify Next Instance Created

```bash
# Check recurring task service logs
kubectl logs -l app=recurring-task-service -n teamflow -c recurring-task-service --tail=50

# Expected: "Created next instance for task {task_id}"
```

---

### 10.3 Verify Task in Database

```bash
# Query database for next instance
# Or use frontend UI to see new task with tomorrow's date
```

---

## 11. Test Reminder Notifications

### 11.1 Trigger Reminder

```bash
# Create task due in 1 hour with 1-hour reminder
TASK_DUE=$(date -u -d '+1 hour' +%Y-%m-%dT%H:%M:%SZ)
REMIND_AT=$(date -u -d '+55 minutes' +%Y-%m-%dT%H:%M:%SZ)

curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d "{
    \"title\": \"Urgent bug fix\",
    \"due_at\": \"$TASK_DUE\",
    \"reminder_settings\": {
      \"offsets\": [\"1h\"],
      \"channels\": [\"email\"]
    }
  }"
```

---

### 11.2 Wait for Reminder

```bash
# Wait for remind_at time (or manually trigger in database)
# Check notification service logs
kubectl logs -l app=notification-service -n teamflow -c notification-service --tail=50

# Expected: "Sending reminder email for task {task_id}"
```

---

### 11.3 Verify Email Sent

```bash
# Check SendGrid dashboard
# Or use SendGrid API to verify email sent
curl -X GET "https://api.sendgrid.com/v3/messages?limit=10" \
  -H "Authorization: Bearer SG.YOUR_API_KEY"
```

---

## 12. Test Real-Time Sync

### 12.1 Connect WebSocket (JavaScript)

```javascript
// In browser console (when logged into frontend)
const token = localStorage.getItem('token');  // Get auth token
const ws = new WebSocket(`ws://localhost:8000/ws/tasks?token=${token}`);

ws.onopen = () => console.log('WebSocket connected');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};

// Now create/update a task in another tab or via API
// You should see the event appear in this console
```

---

### 12.2 Verify Real-Time Update

```bash
# Create a task via API in one terminal
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Test real-time sync"}'

# Check browser console - should see task_created event
```

---

## 13. Troubleshooting

### 13.1 Pods Not Starting

```bash
# Check pod status
kubectl get pods -n teamflow

# Describe pod for errors
kubectl describe pod <pod-name> -n teamflow

# Check logs
kubectl logs <pod-name> -n teamflow -c teamflow-backend
kubectl logs <pod-name> -n teamflow -c daprd
```

---

### 13.2 Dapr Sidecar Issues

```bash
# Check Dapr sidecar logs
kubectl logs <pod-name> -n teamflow -c daprd --tail=100

# Verify Dapr components
kubectl get components -n teamflow

# Describe component for errors
kubectl describe component kafka-pubsub -n teamflow
```

---

### 13.3 Kafka Connection Issues

```bash
# Verify Redpanda is running
kubectl get pods -n kafka

# Check Redpanda logs
kubectl logs redpanda-0 -n kafka --tail=100

# Test connectivity from backend pod
kubectl exec -it deployment/teamflow-backend -n teamflow -- \
  nc -zv redpanda-0.redpanda-headless.kafka.svc.cluster.local 9092

# Expected: Connection to redpanda... 9092 port [tcp/*] succeeded!
```

---

### 13.4 Event Not Published

```bash
# Check backend logs for errors
kubectl logs -l app=teamflow-backend -n teamflow -c teamflow-backend --tail=100

# Check if Dapr sidecar is running
kubectl logs -l app=teamflow-backend -n teamflow -c daprd --tail=100

# Verify Dapr pubsub component
kubectl describe component kafka-pubsub -n teamflow
```

---

### 13.5 WebSocket Connection Fails

```bash
# Check realtime-sync-service logs
kubectl logs -l app=realtime-sync-service -n teamflow -c realtime-sync-service --tail=100

# Verify WebSocket endpoint is accessible
kubectl port-forward svc/realtime-sync-service 8000:8000 -n teamflow

# Test with wscat or browser
wscat -c "ws://localhost:8000/ws/tasks?token=invalid"
# Expected: {"type":"error","message":"Invalid authentication token"}
```

---

## 14. Clean Up

### 14.1 Delete Application

```bash
# Uninstall Helm release
helm uninstall teamflow -n teamflow

# Delete microservices
kubectl delete -f k8s/notification-service.yaml -n teamflow
kubectl delete -f k8s/recurring-task-service.yaml -n teamflow
kubectl delete -f k8s/realtime-sync-service.yaml -n teamflow

# Delete namespace
kubectl delete namespace teamflow
```

---

### 14.2 Delete Redpanda

```bash
# Uninstall Redpanda
helm uninstall redpanda -n kafka

# Delete namespace
kubectl delete namespace kafka
```

---

### 14.3 Uninstall Dapr

```bash
# Remove Dapr from cluster
dapr uninstall -k

# Verify Dapr pods gone
kubectl get pods -n dapr-system
```

---

### 14.4 Stop Minikube

```bash
# Stop Minikube
minikube stop

# Or delete cluster completely
minikube delete
```

---

## 15. Next Steps

After successful local deployment:

1. **Test All Features**:
   - Create recurring task
   - Set reminder
   - Complete task and verify next instance created
   - Connect WebSocket and observe real-time updates

2. **Review Dapr Dashboard**:
   ```bash
   # Port-forward Dapr dashboard
   kubectl port-forward svc/dapr-dashboard -n dapr-system 8080:8080

   # Open http://localhost:8080
   # View components, services, and metrics
   ```

3. **Monitor Kafka Topics**:
   ```bash
   # Use Redpanda Console (web UI)
   kubectl port-forward svc/redpanda -n kafka 8080:8080
   # Open http://localhost:8080
   # View topics, messages, consumer groups
   ```

4. **Prepare for Cloud Deployment**:
   - Review `docs/EXTERNAL-SERVICES-SETUP.md`
   - Set up Oracle OKE cluster
   - Configure CI/CD pipeline

---

**Quickstart Status**: ✅ Complete - All local development setup steps documented with verification commands.

**Estimated Setup Time**: 45-60 minutes (first-time setup), 15 minutes (subsequent runs).
