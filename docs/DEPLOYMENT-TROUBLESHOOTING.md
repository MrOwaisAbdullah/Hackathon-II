# T180: Deployment Troubleshooting Guide

Common issues encountered when deploying TeamFlow Phase 5 and their solutions.

---

## Table of Contents

1. [Dapr Sidecar Issues](#1-dapr-sidecar-issues)
2. [WebSocket Connection Failures](#2-websocket-connection-failures)
3. [Container Image Pull Errors](#3-container-image-pull-errors)
4. [Database Connection Problems](#4-database-connection-problems)
5. [Resource Limits and OOMKilled](#5-resource-limits-and-oomkilled)
6. [SSL/TLS Certificate Issues](#6-ssltls-certificate-issues)
7. [Kafka/Redpanda Connection](#7-kafka-redpanda-connection)
8. [Horizontal Pod Autoscaler Issues](#8-horizontal-pod-autoscaler-issues)

---

## 1. Dapr Sidecar Issues

### Problem: Dapr sidecar not starting

**Symptoms:**
- Pod status shows `CrashLoopBackOff`
- Logs show "dapr-entrypoint: command not found"
- Sidecar container not visible in `kubectl describe pod`

**Solutions:**

1. **Check Dapr initialization:**
```bash
# Verify Dapr is installed on the cluster
kubectl get pods -n dapr-system

# Initialize Dapr if not present
dapr init -k --runtime-version 1.14.0
```

2. **Verify annotations in deployment:**
```bash
# Check if dapr.io/enabled annotation exists
kubectl get deployment teamflow-backend -n teamflow -o yaml | grep dapr
```

3. **Check Dapr version compatibility:**
```yaml
# Ensure version matches cluster installation
dapr:
  enabled: true
  version: "1.14.0"  # Must match kubectl-ai output
```

4. **View sidecar logs:**
```bash
# Dapr logs are in a separate container
kubectl logs <pod-name> -c dapr -n teamflow
```

### Problem: Dapr pub/sub not receiving events

**Symptoms:**
- Events published but not received
- No errors in logs
- Subscription endpoint returns correct topics

**Solutions:**

1. **Verify topic creation in Kafka:**
```bash
kubectl exec -it redpanda-0 -n kafka -- rpk topic list
# Should show: task-events, reminders, task-updates, time-logged
```

2. **Check Dapr component configuration:**
```bash
kubectl get components -n teamflow
# Should show: kafka-pubsub, state-postgresql, secretstores.kubernetes
```

3. **Test pub/sub manually:**
```bash
# Post a test event
curl -X POST "http://teamflow-backend.teamflow.svc.cluster.local:3500/v1.0/publish/kafka-pubsub/task-events" \
  -H "Content-Type: application/json" \
  -d '{
    "specversion": "1.0",
    "type": "test.event",
    "source": "/test",
    "data": {"test": "data"}
  }'
```

---

## 2. WebSocket Connection Failures

### Problem: WebSocket connections dropped immediately

**Symptoms:**
- Connection status shows "Offline"
- Browser console shows "Connection closed before handshake"
- No WebSocket in `kubectl get pods`

**Solutions:**

1. **Verify realtime-sync-service is running:**
```bash
kubectl get pods -n teamflow | grep realtime-sync
```

2. **Check Ingress WebSocket annotations:**
```yaml
# In ingress.yaml must have:
nginx.ingress.kubernetes.io/websocket-services: "realtime-sync-service"
```

3. **Verify sticky sessions are enabled:**
```yaml
nginx.ingress.kubernetes.io/affinity: "cookie"
nginx.ingress.kubernetes.io/session-cookie-name: "route"
```

4. **Test WebSocket connection directly:**
```bash
# Test via port-forwarding
kubectl port-forward svc/realtime-sync-service -n teamflow 8000:8000
# Then: ws://localhost:8000/ws/tasks?token=YOUR_JWT_TOKEN
```

### Problem: JWT authentication failing

**Symptoms:**
- WebSocket closes with code 1008
- Logs show "Invalid token" or "Token expired"

**Solutions:**

1. **Verify JWT secret exists:**
```bash
kubectl get secret jwt-secret -n teamflow
```

2. **Check token in localStorage:**
```javascript
// In browser console
localStorage.getItem('token')
```

3. **Test token decode:**
```bash
# Decode and verify JWT
echo "YOUR_TOKEN" | jwt decode
```

---

## 3. Container Image Pull Errors

### Problem: ImagePullBackOff / ErrImagePull

**Symptoms:**
- Pod status: `ImagePullBackOff`
- Events: `Failed to pull image`

**Solutions:**

1. **Verify image registry secret exists:**
```bash
kubectl get secret ghcr-credentials -n teamflow
```

2. **Recreate secret with correct credentials:**
```bash
kubectl delete secret ghcr-credentials -n teamflow
kubectl create secret docker-registry ghcr-credentials \
  --docker-server=ghcr.io \
  --docker-username=YOUR_USERNAME \
  --docker-password=YOUR_TOKEN \
  --namespace=teamflow
```

3. **Verify image exists in registry:**
```bash
# Check if image tag exists
# Visit: https://github.com/<username>/teamflow/packages
```

4. **Test pull manually:**
```bash
docker pull ghcr.io/yourusername/teamflow-backend:latest
```

---

## 4. Database Connection Problems

### Problem: Connection closed / Neon DB errors

**Symptoms:**
- Backend logs show "connection closed"
- 500 errors on API endpoints
- "no such table" errors

**Solutions:**

1. **Run database migrations:**
```bash
# Check migration status
kubectl exec -it deployment/teamflow-backend -n teamflow \
  -- alembic current

# Run migrations
kubectl exec -it deployment/teamflow-backend -n teamflow \
  -- alembic upgrade head
```

2. **Verify DATABASE_URL environment variable:**
```bash
kubectl get secret teamflow-secrets -n teamflow
# Should contain database-url
```

3. **Check Neon DB connection pooling:**
```python
# In backend code, ensure:
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,  # CRITICAL: Check connections before use
    pool_size=10,
    max_overflow=20,
)
```

4. **Test database connectivity:**
```bash
# Port-forward to backend pod
kubectl port-forward deployment/teamflow-backend -n teamflow 8000:8000

# Test connection from local machine
psql $DATABASE_URL
```

---

## 5. Resource Limits and OOMKilled

### Problem: Pods killed with OOMKilled

**Symptoms:**
- Pod status: `OOMKilled`
- Pod restarts frequently
- Memory usage spikes

**Solutions:**

1. **Check current resource usage:**
```bash
kubectl top pods -n teamflow
```

2. **Verify resource limits:**
```bash
kubectl describe pod <pod-name> -n teamflow
# Look for "limits" section
```

3. **Increase memory limits in values.yaml:**
```yaml
resources:
  limits:
    memory: "512Mi"  # Increase as needed
```

4. **Check Always Free tier limits:**
```bash
# OKE Always Free: 4 OCPUs, 24GB RAM total
kubectl describe nodes
# Look at "Allocated resources"
```

5. **Add HPA for auto-scaling:**
```yaml
autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 5
  targetMemoryUtilizationPercentage: 80
```

---

## 6. SSL/TLS Certificate Issues

### Problem: Certificate errors in browser

**Symptoms:**
- Browser shows "Your connection is not private"
- Mixed content warnings
- Certificate expired or self-signed

**Solutions:**

1. **Check cert-manager:**
```bash
kubectl get pods -n cert-manager
```

2. **Create ClusterIssuer:**
```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@yourdomain.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
```

3. **Verify ingress annotations:**
```yaml
annotations:
  cert-manager.io/cluster-issuer: "letsencrypt-prod"
```

4. **Test certificate:**
```bash
# Check certificate
kubectl get secret teamflow-tls -n teamflow
```

---

## 7. Kafka/Redpanda Connection

### Problem: Microservices can't connect to Kafka

**Symptoms:**
- Event publishing fails
- Subscription errors
- "Connection refused" errors

**Solutions:**

1. **Verify Redpanda is running:**
```bash
kubectl get pods -n kafka
# Should see redpanda-0, redpanda-1, redpanda-2
```

2. **Check Kafka topics:**
```bash
kubectl exec -it redpanda-0 -n kafka -- rpk topic list
```

3. **Test Kafka connection:**
```bash
# Port-forward to Kafka
kubectl port-forward svc/redpanda -n kafka 9092:9092

# Create test topic
kubectl exec -it redpanda-0 -n kafka -- rpk topic create test-topic
```

4. **Verify Dapr Kafka component:**
```bash
kubectl get component kafka-pubsub -n teamflow
```

---

## 8. Horizontal Pod Autoscaler Issues

### Problem: HPA not scaling

**Symptoms:**
- CPU/memory high but pods not scaling
- `kubectl get hpa` shows 0/1 replicas

**Solutions:**

1. **Check resource requests are set:**
```yaml
resources:
  requests:
    cpu: "100m"      # REQUIRED for HPA
    memory: "128Mi"  # REQUIRED for HPA
```

2. **Verify metrics server is running:**
```bash
kubectl get pods -n kube-system | grep metrics-server
```

3. **Check HPA metrics:**
```bash
kubectl get hpa -n teamflow
kubectl describe hpa <hpa-name> -n teamflow
```

4. **Test scaling manually:**
```bash
kubectl scale deployment/teamflow-backend -n teamflow --replicas=3
```

---

## Quick Diagnosis Commands

```bash
# Check all pods
kubectl get pods -n teamflow

# Check pod logs for errors
kubectl logs -l <pod-name> -n teamflow --tail=50

# Describe pod for detailed status
kubectl describe pod <pod-name> -n teamflow

# Check events for errors
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
```

---

## Getting Help

For issues not covered here:

1. Check logs: `kubectl logs -n teamflow --tail=100`
2. Check docs: `docs/EXTERNAL-SERVICES-SETUP.md`
3. Review architecture: `specs/005-advanced-cloud-deployment/plan.md`
4. Create GitHub issue with logs and error details
