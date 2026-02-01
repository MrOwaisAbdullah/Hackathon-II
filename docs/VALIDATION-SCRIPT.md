# Quickstart Validation Script

This document provides commands to validate the TeamFlow Phase 5 deployment.

## Prerequisites

```bash
# Check kubectl is configured
kubectl cluster-info

# Check Helm is installed
helm version

# Check Dapr is installed
dapr version
```

## Quick Validation Commands

### 1. Namespace and Secrets

```bash
# Verify namespace exists
kubectl get namespace teamflow

# Check secrets are created
kubectl get secrets -n teamflow

# Verify critical secrets
kubectl get secret teamflow-secrets -n teamflow
kubectl get secret jwt-secret -n teamflow
kubectl get secret ghcr-credentials -n teamflow
```

### 2. Pods and Services

```bash
# Check all pods are running
kubectl get pods -n teamflow

# Expected output:
# NAME                                    READY   STATUS    RESTARTS   AGE
# teamflow-backend-xxxxxxxxxx-xxxxx       2/2     Running   0          5m
# teamflow-frontend-xxxxxxxxxx-xxxxx      2/2     Running   0          5m
# notification-service-xxxxxxxxxx-xxxxx   2/2     Running   0          5m
# recurring-task-service-xxxxxxxxxx-xxxxx 2/2     Running   0          5m
# realtime-sync-service-xxxxxxxxxx-xxxxx  1/1     Running   0          5m

# Check services
kubectl get svc -n teamflow

# Verify Dapr sidecars are injected
kubectl get pods -n teamflow -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[*].name}{"\n"}{end}'
```

### 3. Dapr Components

```bash
# List Dapr components
kubectl get components -n teamflow

# Expected components:
# - kafka-pubsub
# - state-postgresql
# - secretstores.kubernetes

# Verify Kafka topics
kubectl exec -it redpanda-0 -n kafka -- rpk topic list

# Expected topics:
# - task-events
# - reminders
# - task-updates
# - time-logged
```

### 4. Ingress and Routing

```bash
# Check ingress
kubectl get ingress -n teamflow

# Check ingress configuration
kubectl describe ingress teamflow-ingress -n teamflow

# Verify TLS certificate
kubectl get secret teamflow-tls -n teamflow
```

### 5. Database Connectivity

```bash
# Test database connection from backend pod
kubectl exec -it deployment/teamflow-backend -n teamflow -- python -c "
from app.database import engine
import asyncio
asyncio.run(engine.connect())
print('Database connection: OK')
"

# Run migrations
kubectl exec -it deployment/teamflow-backend -n teamflow -- alembic current
```

### 6. Health Endpoints

```bash
# Port-forward to backend
kubectl port-forward svc/teamflow-backend -n teamflow 8000:8000

# Test health endpoint
curl http://localhost:8000/health

# Test readiness endpoint
curl http://localhost:8000/ready
```

### 7. WebSocket Connection

```bash
# Port-forward to realtime-sync-service
kubectl port-forward svc/realtime-sync-service -n teamflow 8000:8000

# Test WebSocket (requires JWT token)
# Replace YOUR_TOKEN with actual JWT
wscat -c "ws://localhost:8000/ws/tasks?token=YOUR_TOKEN"
```

### 8. Load Testing (100 Concurrent Users)

```bash
# Install k6 or use Docker
docker load < k6:latest

# Create load test script
cat > load-test.js <<'EOF'
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 100 },  // Ramp up to 100 users
    { duration: '1m', target: 100 },   // Stay at 100 users
    { duration: '30s', target: 0 },    // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],  // 95% of requests under 500ms
    http_req_failed: ['rate<0.05'],     // Error rate < 5%
  },
};

const BASE_URL = __ENV.API_URL || 'http://localhost:8000';

export default function () {
  // Test task list endpoint
  let res = http.get(`${BASE_URL}/api/v1/tasks/`);
  check(res, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });

  sleep(1);
}
EOF

# Run load test
k6 run --env API_URL=http://teamflow-backend.teamflow.svc.cluster.local:8000 load-test.js
```

## Common Issues and Fixes

### Issue: Pods in ImagePullBackOff
```bash
# Verify image exists
docker pull ghcr.io/yourusername/teamflow-backend:latest

# Re-create secret
kubectl delete secret ghcr-credentials -n teamflow
kubectl create secret docker-registry ghcr-credentials \
  --docker-server=ghcr.io \
  --docker-username=YOUR_USERNAME \
  --docker-password=YOUR_TOKEN \
  --namespace=teamflow
```

### Issue: Dapr sidecar not starting
```bash
# Verify Dapr installation
kubectl get pods -n dapr-system

# Check Dapr version compatibility
dapr version --runtime-version 1.14.0
```

### Issue: WebSocket connection dropping
```bash
# Verify sticky session annotations
kubectl get ingress teamflow-ingress -n teamflow -o yaml | grep affinity

# Check realtime-sync-service has no Dapr sidecar
kubectl get pod -l app=realtime-sync-service -n teamflow -o jsonpath='{.items[0].spec.containers[*].name}'
```

## Validation Checklist

- [ ] All pods are running with READY status
- [ ] All services are accessible
- [ ] Dapr components are created
- [ ] Kafka topics exist
- [ ] Ingress is configured with TLS
- [ ] Database connection works
- [ ] Health endpoints return 200
- [ ] WebSocket connection accepts JWT
- [ ] Load test passes (100 concurrent users)
- [ ] HPA is configured and working
