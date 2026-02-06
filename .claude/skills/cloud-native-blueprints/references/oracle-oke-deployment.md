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

### Option A: Using Helm Charts

```bash
# If you have Helm charts in your repo
helm install teamflow ./helm/teamflow \
  --namespace teamflow \
  --set backend.image.tag=latest \
  --set frontend.image.tag=latest
```

### Option B: Using kubectl

```bash
# Apply manifests
kubectl apply -f k8s/backend-deployment.yaml -n teamflow
kubectl apply -f k8s/frontend-deployment.yaml -n teamflow
kubectl apply -f k8s/services.yaml -n teamflow
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
- Use `nano` editor to create files
- Use `printf` or `echo` with single-line commands
- Copy content from code blocks and paste into nano

### Pitfall 2: Leading Spaces in YAML

**Problem:** Copy-pasting adds leading spaces that break YAML parsing.

**Error:** `error parsing YAML: mapping values are not allowed in this context`

**Solution:**
- Use `nano` to carefully edit files
- Check with `cat filename.yaml` before applying
- Use `sed -i 's/^ //' filename.yaml` to remove leading spaces

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

## Summary: Critical Commands

| Task | Command |
|------|---------|
| **Dapr CLI (no sudo)** | `wget -q .../install.sh -O - \| DAPR_INSTALL_DIR="$HOME/dapr" /bin/bash -s 1.14.0` |
| **Helm (no sudo)** | Manual binary extraction to `~/helm` |
| **Kafka** | Use Strimzi with KRaft mode, not Redpanda |
| **Kafka Version** | Must use 4.0.0, 4.0.1, 4.1.0, or 4.1.1 |
| **Kafka Config** | Create `KafkaNodePool` + `Kafka` resource |
| **Kafka Pod Name** | `teamflow-kafka-kafka-pool-0` (KRaft mode) |
| **File creation** | Use `nano filename.yaml` |
| **Add to PATH** | `export PATH="$HOME/dapr:$HOME:$PATH"` |

---

**Last Updated:** February 6, 2026
**Tested On:** Oracle Cloud Shell (ARM64, ap-mumbai-1)
