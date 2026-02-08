# Oracle OKE Deployment via Cloud Shell

Complete guide for deploying to Oracle Cloud Infrastructure (OCI) Oracle Kubernetes Engine (OKE) using Oracle Cloud Shell.

---

## Overview

Oracle Cloud Shell is a free, browser-based shell that provides:
- Pre-installed kubectl and OCI CLI
- Temporary storage (5GB home directory)
- ARM64 architecture
- **No sudo access** - critical limitation
- Limited multi-line input support

---

## Prerequisites

| Requirement | Source |
|-------------|--------|
| Oracle Cloud Account | [oracle.com/cloud](https://www.oracle.com/cloud/) |
| OKE Cluster Created | OCI Console → Developer Services → Kubernetes Clusters |
| Cluster OCID | OCI Console → Cluster Details |
| Database URL | External (Neon, etc.) or OCI Database |

---

## Step 1: Access Cloud Shell

1. Log in to [Oracle Cloud Console](https://console.oracle-cloud.com/)
2. Click the **Cloud Shell icon** (>_ ) in top-right corner
3. First time: Choose your home region

```bash
# Verify you're in the right region
# The prompt shows: mrowaisabd@cloudshell:~ (ap-mumbai-1)$
```

---

## Step 2: Configure kubectl

### Option A: From Cloud Shell (Recommended - Easier)

```bash
# Generate kubeconfig from Cloud Shell
oci ce cluster create-kubeconfig \
  --cluster-id "ocid1.cluster.oc1.ap-mumbai-1.aaaaaaaaultsuiurj3ggotx2ok6kr5cmg7zaefzs2l7sbxnricr365xbkv5q" \
  --file $HOME/.kube/config \
  --region ap-mumbai-1

# Verify connection
kubectl get nodes
```

### Option B: From Local Machine

1. Install OCI CLI locally
2. Run the same `oci ce cluster create-kubeconfig` command
3. Copy the generated config to `~/.kube/config`

---

## Step 3: Install Dapr CLI

### ❌ Problem: Dapr Installation Without Sudo

The standard Dapr installation script tries to use `sudo`, which is not available in Cloud Shell.

### ✅ Solution: Install to Home Directory

```bash
# Install Dapr CLI to home directory (no sudo required)
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | DAPR_INSTALL_DIR="$HOME/dapr" /bin/bash -s 1.14.0

# Add to PATH
export PATH="$HOME/dapr:$PATH"

# Verify installation
dapr --version
# Expected output: CLI version: 1.14.0
```

### Initialize Dapr on Cluster

```bash
dapr init -k --runtime-version 1.14.0

# Verify Dapr pods
kubectl get pods -n dapr-system
```

**Expected Output:**
```
NAME                                     READY   STATUS    RESTARTS   AGE
dapr-dashboard-85dcbbb967-zgvlr          1/1     Running   0          30s
dapr-operator-77dccb56c5-99qq5           1/1     Running   0          30s
dapr-placement-server-0                  1/1     Running   0          30s
dapr-sentry-55bd9d976-rzd2h              1/1     Running   0          30s
dapr-sidecar-injector-7b48cddb86-wtfj2   1/1     Running   0          30s
```

---

## Step 4: Install Helm

### ❌ Problem: Helm Installation Without Sudo

The standard Helm installation script also requires `sudo`.

### ✅ Solution: Manual Binary Installation

```bash
# Download Helm binary
wget https://get.helm.sh/helm-v3.20.0-linux-arm64.tar.gz

# Extract
tar -zxvf helm-v3.20.0-linux-arm64.tar.gz

# Move to home directory
mv linux-arm64/helm ~/helm

# Add to PATH
export PATH="$HOME:$PATH"

# Verify
helm version
# Expected: version.BuildInfo{Version:"v3.20.0", ...}

# Clean up
rm -rf linux-arm64 helm-v3.20.0-linux-arm64.tar.gz
```

---

## Step 5: Deploy Kafka (Strimzi) - KRaft Mode

### ❌ Problem: Redpanda Requires cert-manager

Redpanda Helm chart tries to create `Certificate` CRDs which require cert-manager.

### ✅ Solution: Use Strimzi with KRaft Mode

```bash
# Add Strimzi Helm repo
helm repo add strimzi https://strimzi.io/charts/
helm repo update

# Create kafka namespace
kubectl create namespace kafka

# Install Strimzi operator
helm install strimzi-kafka-operator strimzi/strimzi-kafka-operator --namespace kafka

# Wait for operator to be ready
kubectl wait --for=condition=ready pod -l name=strimzi-cluster-operator -n kafka --timeout=120s
```

### ❌ Problem: Kafka Version 3.7.0 Not Supported

**Error:** `Unsupported Kafka.spec.kafka.version: 3.7.0. Supported versions are: [4.0.0, 4.0.1, 4.1.0, 4.1.1]`

### ❌ Problem: ZooKeeper Deprecated

**Error:** `ZooKeeper-based Apache Kafka clusters are not supported anymore since Strimzi 0.46.0`

### ✅ Solution: Use KRaft Mode (Kafka 4.0.0 with KafkaNodePool)

**Step 1: Create KafkaNodePool resource**

```bash
nano kafka-pool.yaml
```

**Paste this content:**
```yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaNodePool
metadata:
  name: kafka-pool
  namespace: kafka
  labels:
    strimzi.io/cluster: teamflow-kafka
spec:
  replicas: 1
  roles:
    - controller
    - broker
  storage:
    type: jbod
    volumes:
      - id: 0
        type: persistent-claim
        size: 5Gi
        deleteClaim: false
```

Save (`Ctrl+O`, `Enter`) and exit (`Ctrl+X`).

**Step 2: Create Kafka cluster resource**

```bash
nano kafka-cluster.yaml
```

**Paste this content:**
```yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: Kafka
metadata:
  name: teamflow-kafka
  namespace: kafka
spec:
  kafka:
    version: 4.0.0
    replicas: 1
    listeners:
      - name: plain
        port: 9092
        type: internal
        tls: false
```

Save (`Ctrl+O`, `Enter`) and exit (`Ctrl+X`).

**Step 3: Apply resources**

```bash
# Apply the node pool first
kubectl apply -f kafka-pool.yaml

# Apply the Kafka cluster
kubectl apply -f kafka-cluster.yaml

# Watch pods being created
kubectl get pods -n kafka -w
```

**Expected pods (press Ctrl+C to stop watching):**
```
NAME                                        READY   STATUS    RESTARTS   AGE
strimzi-cluster-operator-59d87b7b87-28gbb   1/1     Running   0          90m
teamflow-kafka-kafka-pool-0                 1/1     Running   0          3m
```

**Verify Kafka is ready:**
```bash
kubectl get kafka teamflow-kafka -n kafka
# Expected: READY=True, KAFKA VERSION=4.0.0
```

### Create Kafka Topics

```bash
# Access Kafka pod (note: pod name is different in KRaft mode)
kubectl exec -it teamflow-kafka-kafka-pool-0 -n kafka -- /bin/bash

# Inside pod, create topics using Kafka console tools
bin/kafka-topics.sh --create --topic task-events --partitions 3 --replication-factor 1 --bootstrap-server localhost:9092
bin/kafka-topics.sh --create --topic reminders --partitions 3 --replication-factor 1 --bootstrap-server localhost:9092
bin/kafka-topics.sh --create --topic time-logged --partitions 1 --replication-factor 1 --bootstrap-server localhost:9092
bin/kafka-topics.sh --create --topic task-updates --partitions 3 --replication-factor 1 --bootstrap-server localhost:9092

# Verify topics
bin/kafka-topics.sh --list --bootstrap-server localhost:9092
# Expected output:
# reminders
# task-events
# task-updates
# time-logged

# Exit pod
exit
```

### ❌ Problem: Terminal Paste Issues

**Symptom:** Commands have extra characters like `\E[200~` when pasting.

**Solution:**
- Type commands directly or paste carefully
- The terminal may add escape sequences during paste
- If paste fails, type the command manually

### Key Differences: ZooKeeper vs KRaft Mode

| Feature | ZooKeeper Mode (Old) | KRaft Mode (New) |
|---------|---------------------|------------------|
| **Pod Names** | `teamflow-kafka-kafka-0`, `teamflow-kafka-zookeeper-0` | `teamflow-kafka-kafka-pool-0` |
| **Resources** | Separate ZooKeeper deployment | KafkaNodePool resource |
| **Kafka Version** | 3.7.0 (not supported in Strimzi 0.50) | 4.0.0, 4.0.1, 4.1.0, 4.1.1 |
| **Configuration** | Uses `spec.zookeeper` | Uses `KafkaNodePool` with controller role |
| **Replicas** | Set in `spec.kafka.replicas` | Set in `KafkaNodePool.spec.replicas` |

---

## Step 6: Create Kubernetes Secrets

```bash
# Create teamflow namespace
kubectl create namespace teamflow

# Create secrets with your actual values
kubectl create secret generic teamflow-secrets \
  --namespace teamflow \
  --from-literal=database-url='postgresql://user:password@ep-xxx.aws.neon.tech/neondb?sslmode=require' \
  --from-literal=openai-api-key='sk-proj-your-key-here' \
  --from-literal=better-auth-secret='your-secret-here' \
  --from-literal=jwt-secret='your-jwt-secret-here'
```

---

## Step 7: Deploy Application

### Using Helm with OKE Values File

The `values-oke.yaml` file is pre-configured for Oracle OKE Always Free tier:
- Uses Docker Hub images (mrowaisabdullah/teamflow-*)
- Single replica for resource optimization
- K8s internal service URLs for environment variables
- References existing `teamflow-secrets`

```bash
# Deploy using OKE-specific values
helm install teamflow ./helm/teamflow \
  --namespace teamflow \
  --values helm/teamflow/values-oke.yaml \
  --wait --timeout 10m
```

**Note:** If the Helm chart doesn't exist locally, you can use inline values:
```bash
helm install teamflow ./helm/teamflow \
  --namespace teamflow \
  --set frontend.image.repository=mrowaisabdullah/teamflow-frontend \
  --set frontend.image.tag=latest \
  --set backend.image.repository=mrowaisabdullah/teamflow-backend \
  --set backend.image.tag=latest \
  --set backend.dapr.enabled=true \
  --set frontend.dapr.enabled=false \
  --set secrets.existingSecret=teamflow-secrets \
  --set ingress.enabled=false \
  --wait --timeout 10m
```

---

## Step 8: Verify Deployment

```bash
# Check all pods are running
kubectl get pods -n teamflow

# Check services
kubectl get svc -n teamflow

# Check deployment status
kubectl rollout status deployment/teamflow-backend -n teamflow
kubectl rollout status deployment/teamflow-frontend -n teamflow
```

---

## Common Pitfalls and Solutions

### Pitfall 1: Multi-line Commands Fail

**Problem:** Using heredoc (`<< EOF`) or multi-line echo commands causes terminal issues.

**Solution:**
- **ALWAYS use `nano` editor to create files** - heredoc does NOT work in Cloud Shell
- Copy content from code blocks and paste into nano
- Save with `Ctrl+O`, press `Enter`, then exit with `Ctrl+X`

**Example:**
```bash
# ❌ DON'T - Heredoc fails
cat > file.yaml << 'EOF'
content
EOF

# ✅ DO - Use nano instead
nano file.yaml
# Paste content, Ctrl+O, Enter, Ctrl+X
```

**CRITICAL:** For Cloud Shell deployment, NEVER paste YAML content directly into terminal. Always use `nano filename.yaml` to create the file first, then paste the content inside nano editor.

### Pitfall 2: Leading Spaces in YAML

**Problem:** Copy-pasting from terminal code blocks adds leading spaces that break YAML parsing.

**Error:** `error parsing YAML: mapping values are not allowed in this context`

**Solution:**
- **BEST: Write files directly using Write tool** - No leading space issues
- **Alternative: Use `nano`** to carefully edit files
- Check with `cat filename.yaml` before applying
- Use `sed -i 's/^ //' filename.yaml` to remove leading spaces

**Why this happens:** When you copy from a code block in terminal, the indentation gets preserved as actual leading spaces. When writing files directly (like `k8.yml`), there are no leading spaces to remove.

### Pitfall 3: ARM64 Architecture

**Problem:** Some packages don't work or default to wrong architecture.

**Solution:**
- Always specify `linux-arm64` in download URLs
- Use `uname -m` to verify architecture
- Oracle Cloud Shell is always ARM64

### Pitfall 4: Resource Limits (Always Free Tier)

**Problem:** OKE Always Free has limited resources:
- 4 OCPU, 24 GB memory (cluster total)
- 2 GB Block Volume storage

**Solution:**
- Use `replicas: 1` for Kafka
- Set resource limits carefully
- Monitor usage: `kubectl top nodes`

### Pitfall 5: Persistent Storage

**Problem:** PVCs may fail with `Insufficient cpu` or `Insufficient memory`.

**Solution:**
- Use smaller storage sizes (5Gi instead of 10Gi)
- Delete unused PVCs: `kubectl delete pvc --all -n kafka`
- Check storage class: `kubectl get storageclass`

### Pitfall 6: Kafka Version Not Supported

**Problem:** Using Kafka 3.7.0 with Strimzi 0.50 fails.

**Error:** `Unsupported Kafka.spec.kafka.version: 3.7.0. Supported versions are: [4.0.0, 4.0.1, 4.1.0, 4.1.1]`

**Solution:**
- Use Kafka 4.0.0 or later
- Check supported versions: `kubectl get kafka -n kafka -o yaml | grep -A 5 "Supported versions"`

### Pitfall 7: ZooKeeper Deprecated in Strimzi 0.46+

**Problem:** `spec.zookeeper` is deprecated. ZooKeeper-based clusters are not supported.

**Error:** `ZooKeeper-based Apache Kafka clusters are not supported anymore since Strimzi 0.46.0`

**Solution:**
- Use KRaft mode (Kafka Raft)
- Create a `KafkaNodePool` resource with `roles: [controller, broker]`
- Remove `spec.zookeeper` from Kafka resource
- Use Kafka 4.0.0+ which has KRaft enabled by default

### Pitfall 8: Wrong Pod Name for Topic Creation

**Problem:** ZooKeeper mode uses `teamflow-kafka-kafka-0`, KRaft mode uses `teamflow-kafka-kafka-pool-0`.

**Solution:**
- Always check pod name first: `kubectl get pods -n kafka`
- Use the correct pod name when creating topics
- KRaft mode: `kubectl exec -it teamflow-kafka-kafka-pool-0 -n kafka -- /bin/bash`

### Pitfall 9: Existing Kafka Resource Blocks Updates

**Problem:** Trying to update an existing Kafka resource with incompatible changes fails.

**Error:** `strict decoding error: unknown field "spec.kafka.nodeNamePrefix"`

**Solution:**
- Delete the old Kafka resource first: `kubectl delete kafka teamflow-kafka -n kafka`
- Apply the new configuration
- Or use `kubectl replace -f kafka-cluster.yaml` instead of apply

### Pitfall 10: Frontend Docker Build - Missing public Folder

**Problem:** Dockerfile tries to copy `/app/public` which doesn't exist after Next.js build.

**Error:** `failed to compute cache key: "/app/public": not found`

**Solution:**
- Remove the `COPY --from=builder /app/public ./public` line from Dockerfile
- Or make it optional if your project has static assets:
```dockerfile
# Copy public folder if it exists (optional)
COPY --from=builder /app/public ./public 2>/dev/null || true
```

### Pitfall 11: Frontend Build - Missing shadcn/ui Components

**Problem:** Missing shadcn/ui components (dialog, label, input, textarea, calendar, popover).

**Error:** `Module not found: Can't resolve '@/components/ui/dialog'`

**Solution:**
1. Create missing UI components as placeholders:
```bash
# Create components manually or use shadcn CLI
npx shadcn-ui@latest add dialog label input textarea calendar popover
```
2. Install required Radix packages:
```bash
npm install @radix-ui/react-dialog @radix-ui/react-label @radix-ui/react-popover date-fns
```

### Pitfall 12: Frontend Build - Python-style Docstrings in TypeScript

**Problem:** Files have Python-style `"""` docstrings which are invalid in TypeScript.

**Error:** `x Unterminated string constant`

**Solution:**
- Replace `"""` docstrings with JSDoc comments `/** */`
- Or remove docstrings entirely from TS/TSX files

### Pitfall 13: Frontend Build - ESLint/TypeScript Errors

**Problem:** Multiple type errors in TaskCard.tsx, TaskForm.tsx, RecurrenceDialog.tsx.

**Common Errors:**
- `Type 'null' is not assignable to type 'string | undefined'` → Return `undefined` instead of `null`
- `Property 'offsets' does not exist on type 'ReminderSettings'` → Use `offsets_minutes` (array of numbers)
- `Property 'mode' does not exist` → Use `_mode` (prefix with underscore for intentionally unused params)

**Solution:**
- Fix TypeScript types before building Docker image
- Run `npm run build` locally first to catch errors
- Use `as any` type assertion for complex type mismatches

### Pitfall 14: Frontend Build - API Type Mismatches

**Problem:** Form state uses camelCase but API expects snake_case.

**Error:** `Property 'daysOfWeek' does not exist in type 'RecurrenceRule'`

**Solution:**
- Transform form data before sending to API:
```typescript
recurrence_rule: recurrenceRule.frequency ? {
  frequency: recurrenceRule.frequency,
  interval: recurrenceRule.interval,
  days_of_week: recurrenceRule.daysOfWeek as any,  // API expects snake_case
  day_of_month: recurrenceRule.dayOfMonth,
  end_date: recurrenceRule.endDate,
  time_of_day: recurrenceRule.timeOfDay,
} : undefined
```
- Transform `offsets` (string array) to `offsets_minutes` (number array):
```typescript
offsets_minutes: reminderSettings.offsets.map(o => {
  const map: Record<string, number> = { "15m": 15, "1h": 60, "1d": 1440, "1w": 10080 };
  return map[o] || parseInt(o) || 0;
})
```

### Pitfall 15: ImagePullBackOff - Short Name Mode Enforcing (Kubernetes 1.34+)

**Problem:** Kubernetes 1.34+ enforces full image names with registry prefix.

**Error:** `short name mode is enforcing, but image name mrowaisabdullah/teamflow-backend:latest returns ambiguous list`

**Solution:**
- Always use full image name with `docker.io/` prefix in deployment YAMLs
- Update image references: `mrowaisabdullah/teamflow-backend:latest` → `docker.io/mrowaisabdullah/teamflow-backend:latest`

```yaml
# ❌ DON'T - Short name
image: mrowaisabdullah/teamflow-backend:latest

# ✅ DO - Full name with registry
image: docker.io/mrowaisabdullah/teamflow-backend:latest
```

### Pitfall 16: Backend CrashLoopBackOff - Invalid uvicorn --log-config

**Problem:** Backend container crashes immediately with uvicorn error about null log-config.

**Error:** `Error: Invalid value for '--log-config': Path 'null' does not exist.`

**Solution:**
- Override the container command in deployment to use explicit uvicorn args
- Remove or fix the LOG_CONFIG environment variable

```yaml
# Add explicit command to deployment
spec:
  containers:
  - name: backend
    image: docker.io/mrowaisabdullah/teamflow-backend:latest
    command: ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Pitfall 17: Architecture Mismatch - Cloud Shell vs OKE Nodes

**Problem:** Oracle Cloud Shell is ARM64, but OKE Always Free nodes can be AMD64. Images built for wrong architecture fail to run.

**Detection:**
```bash
# Check Cloud Shell architecture
uname -m  # Shows: aarch64 (ARM64)

# Check OKE node architecture
kubectl get nodes -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.nodeInfo.architecture}{"\n"}{end}'
# May show: amd64
```

**Solution:**
- Build multi-platform images or match target node architecture
- Use `docker buildx build --platform linux/amd64` for AMD64 nodes
- Use `docker buildx build --platform linux/arm64` for ARM64 nodes

```bash
# Build for AMD64 (most OKE nodes)
docker buildx build --platform linux/amd64 -t username/image:latest ./path --push

# Build for both architectures
docker buildx build --platform linux/amd64,linux/arm64 -t username/image:latest ./path --push
```

### Pitfall 18: Database Columns Missing After Deployment

**Problem:** After deploying new features (recurrence, reminders), the backend returns 500 errors because database columns don't exist.

**Error:** `column tasks.recurrence_rule does not exist`

**Solution:**
- Run database migrations before or after deploying new backend code
- For Neon PostgreSQL, use the SQL Editor to add missing columns

```sql
-- Run in Neon SQL Editor or via psql
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS recurrence_rule JSONB;
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS reminder_settings JSONB;
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS next_instance_id UUID REFERENCES tasks(id);
```

**Prevention:**
- Always run `alembic upgrade head` locally before deploying
- Create migration scripts as SQL files for easy execution
- Test migrations on a staging database first

---

## Environment Variables

For persistent sessions, add to `~/.bashrc`:

```bash
# Dapr CLI
export PATH="$HOME/dapr:$PATH"

# Helm
export PATH="$HOME:$PATH"

# Kubernetes config (if using custom location)
export KUBECONFIG="$HOME/.kube/config"
```

Apply changes:
```bash
source ~/.bashrc
```

---

## Cleaning Up

```bash
# Delete application
helm uninstall teamflow -n teamflow
# or
kubectl delete namespace teamflow

# Delete Kafka
kubectl delete kafka teamflow-kafka -n kafka
kubectl delete namespace kafka

# Uninstall Strimzi operator
helm uninstall strimzi-kafka-operator -n kafka

# Uninstall Dapr
dapr uninstall -k

# Delete all namespaces
kubectl delete namespace teamflow kafka dapr-system
```

---

## Troubleshooting Commands

```bash
# Check cluster health
kubectl get nodes
kubectl top nodes

# Check pod issues
kubectl describe pod <pod-name> -n <namespace>
kubectl logs <pod-name> -n <namespace>

# Check persistent volumes
kubectl get pv
kubectl get pvc -n <namespace>

# Check storage class
kubectl get storageclass

# Test connectivity
kubectl exec -it <pod-name> -n <namespace> -- /bin/sh
```

---

## Recommended Build Workflow

### ALWAYS Build Locally First

Before building Docker images, always run the build locally to catch errors:

```bash
# Frontend
cd teamflow-web/frontend
npm run build

# Backend
cd teamflow-web/backend
# Backend typically uses Python, verify with:
python -m pytest
```

**Why:** This saves significant time - Docker build takes 2-3 minutes, local build takes ~20 seconds.

### Fix TypeScript/ESLint Errors First

Common issues to fix before Docker build:
1. ✅ Fix all type errors (null vs undefined, property names)
2. ✅ Fix ESLint errors (unused variables, imports)
3. ✅ Ensure all dependencies are installed
4. ✅ Verify package-lock.json is in sync

### Docker Build Process

1. **Build locally first** → `npm run build`
2. **Build Docker image** → `docker build -t username/image:latest ./path`
3. **Test image locally** → `docker run -p 3000:3000 username/image:latest`
4. **Push to registry** → `docker push username/image:latest`

---

## Summary: Critical Commands

| Task | Command |
|------|---------|
| **Dapr CLI (no sudo)** | `wget -q .../install.sh -O - \| DAPR_INSTALL_DIR="$HOME/dapr" /bin/bash -s 1.14.0` |
| **Helm (no sudo)** | Manual binary extraction to `~/helm` |
| **Kafka** | Use Strimzi with KRaft mode, not Redpanda |
| **Kafka Version** | Must use 4.0.0, 4.0.1, 4.1.0, or 4.1.1 |
| **Kafka Config** | Create `KafkaNodePool` + `Kafka` resource |
| **Kafka Pod Name** | `teamflow-kafka-kafka-pool-0` (KRaft mode) |
| **File creation** | Use `nano filename.yaml` (heredoc fails in Cloud Shell) |
| **Add to PATH** | `export PATH="$HOME/dapr:$HOME:$PATH"` |
| **K8s 1.34+ images** | Must use `docker.io/` prefix (e.g., `docker.io/username/image:latest`) |
| **Check node arch** | `kubectl get nodes -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.nodeInfo.architecture}{"\n"}{end}'` |
| **Build AMD64 image** | `docker buildx build --platform linux/amd64 -t username/image:latest ./path --push` |
| **Fix uvicorn crash** | Add `command: ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]` |
| **Database migration** | Run SQL in Neon: `ALTER TABLE tasks ADD COLUMN IF NOT EXISTS recurrence_rule JSONB;` |
| **Expose frontend** | `kubectl apply -f expose-frontend-lb.yaml` (LoadBalancer service) |
| **Restart deployment** | `kubectl rollout restart deployment teamflow-frontend -n teamflow` |
| **Check pod logs** | `kubectl logs -l app=teamflow-backend -n teamflow --tail=50` |
| **Check pod error** | `kubectl describe pod <pod-name> -n teamflow` |

---

## Complete Deployment Checklist

- [ ] **Prerequisites**
  - [ ] Oracle Cloud account with OKE cluster created
  - [ ] Database URL (Neon PostgreSQL or similar)
  - [ ] OpenAI API key
  - [ ] JWT secret and Better Auth secret

- [ ] **Step 1: Cloud Shell Setup**
  - [ ] Access Cloud Shell from OCI Console
  - [ ] Run `oci ce cluster create-kubeconfig` to configure kubectl
  - [ ] Verify: `kubectl get nodes`

- [ ] **Step 2: Install Dapr CLI**
  - [ ] `wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - \| DAPR_INSTALL_DIR="$HOME/dapr" /bin/bash -s 1.14.0`
  - [ ] `export PATH="$HOME/dapr:$PATH"`
  - [ ] `dapr init -k --runtime-version 1.14.0`
  - [ ] Verify: `kubectl get pods -n dapr-system`

- [ ] **Step 3: Install Helm**
  - [ ] `wget https://get.helm.sh/helm-v3.20.0-linux-arm64.tar.gz`
  - [ ] `tar -zxvf helm-v3.20.0-linux-arm64.tar.gz`
  - [ ] `mv linux-arm64/helm ~/helm`
  - [ ] `export PATH="$HOME:$PATH"`
  - [ ] Verify: `helm version`

- [ ] **Step 4: Deploy Kafka (Strimzi KRaft Mode)**
  - [ ] `helm repo add strimzi https://strimzi.io/charts/`
  - [ ] `helm repo update`
  - [ ] `kubectl create namespace kafka`
  - [ ] `helm install strimzi-kafka-operator strimzi/strimzi-kafka-operator --namespace kafka`
  - [ ] Create `kafka-pool.yaml` with KafkaNodePool (replicas: 1, roles: [controller, broker])
  - [ ] Create `kafka-cluster.yaml` with Kafka resource (version: 4.0.0)
  - [ ] `kubectl apply -f kafka-pool.yaml && kubectl apply -f kafka-cluster.yaml`
  - [ ] Wait for pods: `kubectl get pods -n kafka -w`
  - [ ] Create topics inside pod: `kubectl exec -it teamflow-kafka-kafka-pool-0 -n kafka -- bin/kafka-topics.sh --create --topic task-events --partitions 3 --replication-factor 1 --bootstrap-server localhost:9092`

- [ ] **Step 5: Build Docker Images** (LOCAL MACHINE)
  - [ ] `cd teamflow-web/frontend && npm run build` (verify first!)
  - [ ] `docker buildx build --platform linux/amd64 -t mrowaisabdullah/teamflow-frontend:latest ./teamflow-web/frontend --push`
  - [ ] `docker buildx build --platform linux/amd64 -t mrowaisabdullah/teamflow-backend:latest ./teamflow-web/backend --push`
  - [ ] Verify images are public on Docker Hub

- [ ] **Step 6: Create Namespace and Secrets**
  - [ ] `kubectl create namespace teamflow`
  - [ ] `kubectl create secret generic teamflow-secrets --namespace teamflow --from-literal=database-url='YOUR_URL' --from-literal=openai-api-key='YOUR_KEY' --from-literal=jwt-secret='YOUR_SECRET' --from-literal=better-auth-secret='YOUR_SECRET'`

- [ ] **Step 7: Run Database Migrations**
  - [ ] Go to Neon Console → SQL Editor
  - [ ] Run: `ALTER TABLE tasks ADD COLUMN IF NOT EXISTS recurrence_rule JSONB;`
  - [ ] Run: `ALTER TABLE tasks ADD COLUMN IF NOT EXISTS reminder_settings JSONB;`
  - [ ] Run: `ALTER TABLE tasks ADD COLUMN IF NOT EXISTS next_instance_id UUID REFERENCES tasks(id);`

- [ ] **Step 8: Deploy Application**
  - [ ] Create `backend-deployment.yaml` with `docker.io/` prefix, command override, Dapr annotations
  - [ ] Create `frontend-deployment.yaml` with `docker.io/` prefix
  - [ ] `kubectl apply -f backend-deployment.yaml -n teamflow`
  - [ ] `kubectl apply -f frontend-deployment.yaml -n teamflow`

- [ ] **Step 9: Expose Application (LoadBalancer)**
  - [ ] Create `expose-frontend-lb.yaml` with LoadBalancer type
  - [ ] `kubectl apply -f expose-frontend-lb.yaml`
  - [ ] Get external IP: `kubectl get svc teamflow-frontend-lb -n teamflow`
  - [ ] Open http://EXTERNAL-IP in browser

- [ ] **Step 10: Verify Deployment**
  - [ ] `kubectl get pods -n teamflow` (all Running)
  - [ ] `kubectl get svc -n teamflow` (services exist)
  - [ ] Test creating a task in the UI
  - [ ] Check backend logs: `kubectl logs -l app=teamflow-backend -n teamflow --tail=20`

---

**Last Updated:** February 8, 2026
**Tested On:** Oracle Cloud Shell (ARM64, ap-mumbai-1) with OKE AMD64 nodes
