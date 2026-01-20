# Cloud-Native Technologies Learning Guide
## Understanding Docker, Kubernetes, Dapr, and Kafka for Beginners

---

## 🎯 The Big Picture: Why Do We Need All This?

Imagine you built a restaurant (your TeamFlow app):
- **Your Code** = The Recipe (how to cook)
- **Docker** = The Kitchen (standardized cooking environment)
- **Kubernetes** = The Restaurant Manager (handles multiple kitchens, staff)
- **Helm** = The Restaurant Blueprint (how to set up new locations)
- **Dapr** = The Waiter (handles communication between kitchen and customers)
- **Kafka** = The Order Queue (manages who ordered what, when)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        YOUR TEAMFLOW APPLICATION                         │
│                                                                         │
│   📝 Code (Next.js + FastAPI)                                           │
│         ↓                                                               │
│   📦 Docker (Package it)                                                │
│         ↓                                                               │
│   ☸️ Kubernetes (Run it at scale)                                        │
│         ↓                                                               │
│   🎭 Dapr (Make services talk)  ←→  📨 Kafka (Handle events)            │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 1️⃣ Docker - The Container Technology

### What is Docker?

Docker is like a **shipping container** for software. Just like shipping containers can carry any goods and fit on any ship, Docker containers can run any application on any computer.

### The Problem Docker Solves

**Before Docker:**
```
Developer: "It works on my machine! 🤷‍♂️"
Server: "Well, it doesn't work here! 😤"
```

**After Docker:**
```
Developer: "Here's my container with EVERYTHING inside"
Server: "Runs perfectly! 🎉"
```

### Key Concepts

| Concept | Analogy | Description |
|---------|---------|-------------|
| **Image** | Recipe | A template with all instructions to create a container |
| **Container** | Cooked Dish | A running instance of an image |
| **Dockerfile** | Recipe Card | Text file with instructions to build an image |
| **Registry** | Recipe Book | Storage for images (Docker Hub, GitHub Container Registry) |

### Visual: How Docker Works

```
┌──────────────────────────────────────────────────────────────────┐
│                         YOUR COMPUTER                             │
│                                                                   │
│  ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐ │
│  │   Container 1   │   │   Container 2   │   │   Container 3   │ │
│  │   ┌─────────┐   │   │   ┌─────────┐   │   │   ┌─────────┐   │ │
│  │   │ Next.js │   │   │   │ FastAPI │   │   │   │ Postgres│   │ │
│  │   │   App   │   │   │   │   API   │   │   │   │    DB   │   │ │
│  │   └─────────┘   │   │   └─────────┘   │   │   └─────────┘   │ │
│  │   + Node.js     │   │   + Python      │   │   + Linux       │ │
│  │   + npm deps    │   │   + pip deps    │   │   + data files  │ │
│  └─────────────────┘   └─────────────────┘   └─────────────────┘ │
│                                                                   │
│  ═══════════════════════ DOCKER ENGINE ═══════════════════════   │
│                                                                   │
│  ═══════════════════ OPERATING SYSTEM (Windows/Mac/Linux) ═════  │
└──────────────────────────────────────────────────────────────────┘
```

### Your TeamFlow Dockerfiles Explained

**Backend Dockerfile (FastAPI):**
```dockerfile
# Start with Python base image (like getting a pre-setup kitchen)
FROM python:3.13-slim

# Set working directory (create a cooking station)
WORKDIR /app

# Copy requirements (list of ingredients needed)
COPY pyproject.toml ./

# Install dependencies (buy the ingredients)
RUN pip install uv && uv sync

# Copy your code (bring in the recipe)
COPY app/ ./app/

# Expose port (open the serving window)
EXPOSE 8000

# Start the server (start cooking!)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Commands You'll Use

```bash
# Build an image from Dockerfile
docker build -t teamflow/backend:latest .

# Run a container from image
docker run -p 8000:8000 teamflow/backend:latest

# List running containers
docker ps

# Stop a container
docker stop <container_id>

# View container logs
docker logs <container_id>
```

---

## 2️⃣ Kubernetes (K8s) - The Container Orchestrator

### What is Kubernetes?

Kubernetes is like an **army general** for your containers. It:
- Decides where to place containers (scheduling)
- Makes sure they're healthy (monitoring)
- Replaces them if they die (self-healing)
- Scales up/down based on demand (autoscaling)

### The Problem Kubernetes Solves

**With Docker Alone:**
- You: "I'll run 3 containers manually"
- Container crashes at 3 AM
- You: "😴 ZZZ... app is down"

**With Kubernetes:**
- K8s: "Container crashed? I'll restart it automatically"
- K8s: "Traffic spike? I'll spin up more containers"
- You: "😴 ZZZ... app is running perfectly"

### Key Concepts

| Concept | Analogy | Description |
|---------|---------|-------------|
| **Cluster** | Army Base | Collection of machines running K8s |
| **Node** | Soldier | Single machine in the cluster |
| **Pod** | Squad | Smallest unit, usually 1 container |
| **Deployment** | Mission Plan | Defines how many pods and their config |
| **Service** | Communication Channel | How pods talk to each other |
| **Ingress** | Main Gate | Routes external traffic to services |
| **Namespace** | Division | Logical separation within cluster |

### Visual: Kubernetes Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           KUBERNETES CLUSTER                                 │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                         CONTROL PLANE (The Brain)                       ││
│  │   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   ││
│  │   │ API Server  │  │ Scheduler   │  │ Controller  │  │    etcd     │   ││
│  │   │ (Command    │  │ (Where to   │  │ (Maintains  │  │ (Database   │   ││
│  │   │  Center)    │  │  put pods)  │  │  state)     │  │  of state)  │   ││
│  │   └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                    ↕                                        │
│  ┌──────────────────────┐  ┌──────────────────────┐  ┌────────────────────┐ │
│  │       NODE 1         │  │       NODE 2         │  │       NODE 3       │ │
│  │                      │  │                      │  │                    │ │
│  │  ┌────────────────┐  │  │  ┌────────────────┐  │  │  ┌──────────────┐  │ │
│  │  │   Pod: Frontend│  │  │  │   Pod: Backend │  │  │  │ Pod: Backend │  │ │
│  │  │   ┌──────────┐ │  │  │  │   ┌──────────┐ │  │  │  │ ┌──────────┐ │  │ │
│  │  │   │ Next.js  │ │  │  │  │   │ FastAPI  │ │  │  │  │ │ FastAPI  │ │  │ │
│  │  │   └──────────┘ │  │  │  │   └──────────┘ │  │  │  │ └──────────┘ │  │ │
│  │  └────────────────┘  │  │  └────────────────┘  │  │  └──────────────┘  │ │
│  │                      │  │                      │  │                    │ │
│  │  ┌────────────────┐  │  │  ┌────────────────┐  │  │                    │ │
│  │  │   Pod: Frontend│  │  │  │   Pod: Backend │  │  │                    │ │
│  │  │   (replica 2)  │  │  │  │   (replica 3)  │  │  │                    │ │
│  │  └────────────────┘  │  │  └────────────────┘  │  │                    │ │
│  └──────────────────────┘  └──────────────────────┘  └────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Your Deployment Example (backend-deployment.yaml)

```yaml
apiVersion: apps/v1
kind: Deployment           # 👈 Type of K8s object
metadata:
  name: backend            # 👈 Name for this deployment
  namespace: teamflow      # 👈 Which namespace (division)
spec:
  replicas: 2              # 👈 Run 2 copies (for redundancy)
  selector:
    matchLabels:
      app: backend         # 👈 How to find our pods
  template:
    spec:
      containers:
      - name: backend
        image: teamflow/backend:latest  # 👈 Which Docker image
        ports:
        - containerPort: 8000           # 👈 Port to expose
        resources:
          limits:
            cpu: "1"                    # 👈 Max CPU allowed
            memory: "1Gi"               # 👈 Max memory allowed
```

### Minikube: Your Local Kubernetes

Minikube runs a mini Kubernetes cluster on your laptop:

```bash
# Start local cluster
minikube start --cpus=4 --memory=8192

# Check cluster status
minikube status

# Open dashboard (visual interface)
minikube dashboard

# Access a service
minikube service teamflow-frontend -n teamflow
```

---

## 3️⃣ Helm - The Kubernetes Package Manager

### What is Helm?

Helm is like **npm/pip for Kubernetes**. Instead of writing 20 YAML files manually, you create a template once and reuse it.

### The Problem Helm Solves

**Without Helm:**
```
- backend-deployment.yaml
- backend-service.yaml
- frontend-deployment.yaml
- frontend-service.yaml
- configmap.yaml
- secrets.yaml
- ingress.yaml
... 15 more files ...
😵 Managing all these files is a nightmare!
```

**With Helm:**
```bash
helm install teamflow ./helm/teamflow
# ✨ All files deployed with one command!
```

### Why Helm?

| Without Helm | With Helm |
|--------------|-----------|
| Copy-paste YAML files everywhere | Templates with variables |
| Change values in 10 places | Change once in `values.yaml` |
| No versioning | `helm upgrade`/`helm rollback` |
| No reusability | Share as "charts" |

### Helm Chart Structure

```
helm/teamflow/
├── Chart.yaml          # 📋 Chart metadata (name, version)
├── values.yaml         # ⚙️ Default configuration values
└── templates/          # 📝 Template files
    ├── deployment.yaml # (uses {{ .Values.x }})
    ├── service.yaml
    └── ingress.yaml
```

### Example: values.yaml + Template

**values.yaml:**
```yaml
backend:
  replicas: 2
  image: teamflow/backend
  tag: v1.0.0
```

**deployment.yaml template:**
```yaml
spec:
  replicas: {{ .Values.backend.replicas }}  # 👈 Gets value: 2
  containers:
    - image: {{ .Values.backend.image }}:{{ .Values.backend.tag }}
```

### Common Helm Commands

```bash
# Install a chart
helm install teamflow ./helm/teamflow -n teamflow

# Upgrade (update existing release)
helm upgrade teamflow ./helm/teamflow -n teamflow

# Rollback to previous version
helm rollback teamflow 1

# List installed releases
helm list -n teamflow

# Uninstall
helm uninstall teamflow -n teamflow
```

---

## 4️⃣ Kafka - The Event Streaming Platform

### What is Kafka?

Kafka is like a **super-powered message board** where services can post messages and other services can read them - even if they weren't online when the message was posted!

### The Problem Kafka Solves

**Without Kafka (Direct Communication):**
```
Backend: "Hey Notification Service, send an email!"
Notification Service: *crashes*
Backend: "oh no, my request is lost forever 😢"
```

**With Kafka:**
```
Backend: "I'll post this event to Kafka"
Kafka: "I'll store it safely ✅"
*Notification Service comes back online*
Notification Service: "Oh, there's a message! I'll process it now"
```

### Key Concepts

| Concept | Analogy | Description |
|---------|---------|-------------|
| **Producer** | Author | Service that publishes messages |
| **Consumer** | Reader | Service that reads messages |
| **Topic** | Channel | Category for messages |
| **Partition** | Lane | Parallel processing within a topic |
| **Offset** | Bookmark | Position in the message queue |
| **Consumer Group** | Book Club | Group of consumers sharing work |

### Visual: How Kafka Works

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                              KAFKA CLUSTER                                    │
│                                                                              │
│  ┌────────────┐      ┌─────────────────────────────────────────────────────┐ │
│  │  Producer  │      │                    TOPIC: task-events               │ │
│  │  (Backend) │─────▶│  ┌─────────────────────────────────────────────────┐│ │
│  └────────────┘      │  │ Partition 0: [msg1] [msg2] [msg3] [msg4] ───▶   ││ │
│                      │  └─────────────────────────────────────────────────┘│ │
│  ┌────────────┐      │  ┌─────────────────────────────────────────────────┐│ │
│  │  Producer  │      │  │ Partition 1: [msg5] [msg6] [msg7] ───▶          ││ │
│  │  (Timer)   │─────▶│  └─────────────────────────────────────────────────┘│ │
│  └────────────┘      └─────────────────────────────────────────────────────┘ │
│                                            │                                  │
│                          ┌─────────────────┼─────────────────┐               │
│                          ↓                 ↓                 ↓               │
│                   ┌────────────┐    ┌────────────┐    ┌────────────┐        │
│                   │  Consumer  │    │  Consumer  │    │  Consumer  │        │
│                   │ Recurring  │    │ Notification│   │   Audit    │        │
│                   │  Service   │    │  Service   │    │  Service   │        │
│                   └────────────┘    └────────────┘    └────────────┘        │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Your Kafka Topics in TeamFlow

| Topic | When Events Are Published | Who Listens |
|-------|---------------------------|-------------|
| `task-events` | Task created, updated, completed, deleted | Recurring Service, Audit Service |
| `reminders` | Due date approaching | Notification Service |
| `time-logged` | Time entry added | Billing Dashboard |

### Redpanda vs Kafka

| Feature | Apache Kafka | Redpanda |
|---------|--------------|----------|
| Complexity | Complex (needs ZooKeeper) | Simple (single binary) |
| Resource Usage | High | Low |
| Compatibility | Original | 100% Kafka-compatible |
| Best For | Production | Hackathon/Development |

---

## 5️⃣ Dapr - The Distributed Application Runtime

### What is Dapr?

Dapr is like a **universal translator and helper** that sits next to your app and handles all the complex stuff:
- Talking to message queues (Kafka, RabbitMQ)
- Storing state (Redis, PostgreSQL)
- Calling other services
- Managing secrets

### The Problem Dapr Solves

**Without Dapr:**
```python
from kafka import KafkaProducer  # Need Kafka library
producer = KafkaProducer(
    bootstrap_servers="kafka:9092",
    security_protocol="SASL_SSL",  # Complex config
    sasl_mechanism="SCRAM-SHA-256",
    sasl_plain_username="user",
    sasl_plain_password="pass"
)
# If you switch to RabbitMQ later, rewrite EVERYTHING!
```

**With Dapr:**
```python
import httpx
await httpx.post(
    "http://localhost:3500/v1.0/publish/my-pubsub/my-topic",
    json={"hello": "world"}
)
# Switch to RabbitMQ? Just change the YAML config, not your code!
```

### Dapr Building Blocks

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DAPR BUILDING BLOCKS                               │
│                                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────┐ │
│  │   🔔 PUB/SUB     │  │   📦 STATE      │  │   🔐 SECRETS                 │ │
│  │                 │  │                 │  │                             │ │
│  │ Publish events  │  │ Store/retrieve  │  │ Access API keys,           │ │
│  │ to Kafka,       │  │ data from       │  │ passwords from             │ │
│  │ RabbitMQ, etc   │  │ Redis, Postgres │  │ K8s, Vault, etc            │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────────────────┘ │
│                                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────┐ │
│  │   📞 SERVICE     │  │   ⏰ BINDINGS   │  │   🔄 ACTORS                 │ │
│  │   INVOCATION    │  │   (Input/Output)│  │                             │ │
│  │                 │  │                 │  │ Virtual actors for          │ │
│  │ Call other      │  │ Cron triggers,  │  │ stateful patterns          │ │
│  │ services with   │  │ event triggers, │  │ (timers, reminders)        │ │
│  │ retry, mTLS     │  │ webhooks        │  │                             │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Visual: Dapr Sidecar Pattern

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              POD                                             │
│                                                                             │
│   ┌─────────────────────────────────┐    ┌─────────────────────────────────┐│
│   │                                 │    │                                 ││
│   │         YOUR APP                │    │         DAPR SIDECAR            ││
│   │         (FastAPI)               │◄──►│         (Helper)                ││
│   │                                 │    │                                 ││
│   │  - Your business logic          │    │  - Handles Kafka publishing     ││
│   │  - No infrastructure code       │    │  - Handles secret fetching      ││
│   │  - Just HTTP calls to Dapr      │    │  - Handles service discovery    ││
│   │                                 │    │                                 ││
│   └─────────────────────────────────┘    └─────────────────────────────────┘│
│                                                        │                    │
│                                                        ↓                    │
│                                          ┌─────────────────────────────────┐│
│                                          │  KAFKA, REDIS, SECRETS, etc.    ││
│                                          └─────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────────┘
```

### How You'll Use Dapr in TeamFlow

```python
# 1. Publishing an event (instead of using Kafka client directly)
async def on_task_completed(task_id: int):
    await httpx.post(
        "http://localhost:3500/v1.0/publish/kafka-pubsub/task-events",
        json={"event": "completed", "task_id": task_id}
    )

# 2. Subscribing to events (Dapr calls YOUR endpoint)
@app.post("/events/task-events")
async def handle_event(data: dict):
    if data["event"] == "completed":
        await create_next_recurring_task(data["task_id"])
    return {"status": "OK"}

# 3. Reading secrets
async def get_openai_key():
    response = await httpx.get(
        "http://localhost:3500/v1.0/secrets/kubernetes-secrets/OPENAI_API_KEY"
    )
    return response.json()["OPENAI_API_KEY"]
```

---

## 6️⃣ How Everything Works Together

### Complete Flow: Creating a Recurring Task

```
User clicks "Create Task"
           │
           ↓
┌─────────────────┐
│    FRONTEND     │ (Next.js in Docker container)
│    Container    │
└────────┬────────┘
         │ HTTP Request
         ↓
┌─────────────────┐
│    BACKEND      │ (FastAPI in Docker container)
│    Container    │
└────────┬────────┘
         │ Via Dapr Sidecar
         ↓
┌─────────────────┐
│      DAPR       │ "Publish to task-events topic"
│    SIDECAR      │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│     KAFKA       │ (Stores the event)
│     TOPIC       │
└────────┬────────┘
         │ Dapr delivers to subscribers
         ↓
┌─────────────────┐
│   RECURRING     │ "Oh, a task was completed!"
│    SERVICE      │ "Let me create the next occurrence"
└─────────────────┘
```

### The Deployment Journey

```
1. DEVELOPMENT (Your Laptop)
   ├── Write code
   └── Test with docker-compose

2. CONTAINERIZATION (Docker)
   ├── Build Docker images
   └── Push to registry

3. LOCAL K8S (Minikube)
   ├── Deploy Helm charts
   ├── Install Dapr
   └── Test everything locally

4. CLOUD K8S (AKS/GKE)
   ├── Create cloud cluster
   ├── Deploy same Helm charts
   ├── Configure domain/SSL
   └── Set up monitoring

5. CI/CD (GitHub Actions)
   ├── Automatic testing
   ├── Automatic image building
   └── Automatic deployment
```

---

## 7️⃣ Quick Reference Commands

### Docker
```bash
docker build -t name .      # Build image
docker run -p 8000:8000 img # Run container
docker ps                   # List running
docker logs container_id    # View logs
```

### Kubernetes (kubectl)
```bash
kubectl get pods -n teamflow       # List pods
kubectl logs pod-name -n teamflow  # View logs
kubectl describe pod pod-name      # Pod details
kubectl apply -f file.yaml         # Apply config
kubectl delete -f file.yaml        # Remove
```

### Helm
```bash
helm install name ./chart    # Install
helm upgrade name ./chart    # Upgrade
helm rollback name 1         # Rollback
helm list                    # List releases
helm uninstall name          # Remove
```

### Minikube
```bash
minikube start               # Start cluster
minikube dashboard           # Open GUI
minikube service svc-name    # Access service
minikube stop                # Stop cluster
```

### Dapr
```bash
dapr init -k                 # Install on K8s
dapr run --app-id myapp ...  # Run app with Dapr
dapr list                    # List running apps
```

---

## 🎓 Learning Path (Recommended Order)

1. **Week 1: Docker Basics**
   - [ ] Build your first Dockerfile
   - [ ] Run containers locally
   - [ ] Understand images vs containers

2. **Week 2: Kubernetes Basics**
   - [ ] Start Minikube
   - [ ] Deploy a simple pod
   - [ ] Understand Services and Ingress

3. **Week 3: Helm**
   - [ ] Create a simple Helm chart
   - [ ] Deploy with `helm install`
   - [ ] Modify values and upgrade

4. **Week 4: Dapr + Kafka**
   - [ ] Install Dapr on Minikube
   - [ ] Publish/subscribe to events
   - [ ] Connect services via Dapr

---

## 📚 Recommended Resources & Sources

This guide is validated with official documentation and best practices from:

### Docker
| Resource | URL | Best For |
|----------|-----|----------|
| **Multi-Stage Builds** | [docs.docker.com/build/building/multi-stage/](https://docs.docker.com/build/building/multi-stage/) | Optimizing image size |
| **Build Best Practices** | [docs.docker.com/build/building/best-practices/](https://docs.docker.com/build/building/best-practices/) | Production Dockerfiles |
| **Next.js Docker 2025** | [Medium - Dockerizing Next.js in 2025](https://medium.com/front-end-world/dockerizing-a-next-js-application-in-2025-bacdca4810fe) | Modern Next.js deployment |
| **Docker Concepts** | [docs.docker.com/guides/reactjs/containerize](https://docs.docker.com/guides/reactjs/containerize) | Container fundamentals |

### Kubernetes & Minikube
| Resource | URL | Best For |
|----------|-----|----------|
| **Minikube Start Guide** | [minikube.sigs.k8s.io/docs/start/](https://minikube.sigs.k8s.io/docs/start/) | Local cluster setup |
| **kubectl Installation** | [kubernetes.io/docs/tasks/tools/](https://kubernetes.io/docs/tasks/tools/) | CLI setup |
| **Kubernetes Tutorials** | [kubernetes.io/docs/tutorials](https://kubernetes.io/docs/tutorials) | Interactive learning |
| **Minikube on Linux** | [WafaiCloud - Getting Started](https://wafaicloud.com/blog/getting-started-with-minikube-on-linux/) | Linux-specific setup |
| **Learning Environment** | [kubernetes.io/docs/setup/learning-environment](https://kubernetes.io/docs/setup/learning-environment) | Minikube overview |

### Helm
| Resource | URL | Best For |
|----------|-----|----------|
| **Helm Installation** | [helm.sh/docs/intro/install/](https://helm.sh/docs/intro/install/) | Installing Helm CLI |
| **Chart Template Guide** | [helm.sh/docs/chart_template_guide/getting_started](https://helm.sh/docs/chart_template_guide/getting_started) | Creating charts |
| **Helm Charts 2025** | [Atmosly - Helm Charts Guide](http://atmosly.com/knowledge/helm-charts-in-kubernetes-definitive-guide-for-2025) | Current best practices |
| **Helm Tutorial** | [Testkube - Complete Guide](https://testkube.io/blog/helm-charts-tutorial-complete-guide-to-kubernetes-testing-deployment) | Step-by-step tutorial |

### Dapr & Kafka
| Resource | URL | Best For |
|----------|-----|----------|
| **Dapr Documentation** | [docs.dapr.io](https://docs.dapr.io) | Complete Dapr guide |
| **Dapr Getting Started** | [docs.dapr.io/getting-started](https://docs.dapr.io/getting-started) | First-time setup |
| **Redpanda Quickstart** | [docs.redpanda.com](https://docs.redpanda.com) | Kafka alternative |
| **Kafka Concepts** | [Confluent Kafka Docs](https://docs.confluent.io/kafka/) | Event streaming |

### TeamFlow Project Resources
| Resource | Location | Description |
|----------|----------|-------------|
| **Local Dev Guide** | `LOCAL-DEV-GUIDE.md` | Step-by-step deployment |
| **Architecture Plan** | `specs/001-k8s-minikube-deployment/plan.md` | Design decisions |
| **Cloud-N Blueprints** | `.claude/skills/cloud-native-blueprints/` | K8s/Helm patterns |
| **Helm Charts** | `helm/teamflow/` | Production templates |

### AIOps Tools
| Tool | Purpose | Usage |
|------|---------|-------|
| **kubectl-ai** | Natural language K8s operations | `kubectl-ai "deploy backend with 2 replicas"` |
| **Docker Gordon** | AI Dockerfile optimization | `docker ai "optimize this Dockerfile"` |
| **Kagent** | Cluster analysis | `kagent "analyze cluster health"` |

**Last Updated:** January 20, 2026
**Validated With:** Tavily MCP, Context7 MCP, and official documentation

---
