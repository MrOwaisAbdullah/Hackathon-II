# Understanding Claude Code Skills & Cloud-Native Blueprints
## How to Create Agent Skills for +200 Bonus Points

---

## 🎯 What is a Claude Code Skill?

A **Claude Code Skill** is a reusable instruction package that teaches Claude how to perform specialized tasks. Think of it as a "cookbook" that Claude reads when it encounters specific situations.

### The Problem Skills Solve

**Without a Skill:**
```
User: "Deploy my app to Kubernetes"
Claude: "Let me figure this out from scratch..." 
        (May make mistakes, inconsistent approach)
```

**With a Skill:**
```
User: "Deploy my app to Kubernetes"
Claude: *Reads kubernetes-deploy skill*
        "I have a proven blueprint for this!"
        (Follows tested patterns, consistent every time)
```

---

## 📁 Skill Structure

Every skill is a folder with this structure:

```
.claude/skills/
└── my-skill-name/
    ├── SKILL.md              # REQUIRED - Main instructions
    ├── scripts/              # Optional - Executable code
    │   └── deploy.py
    ├── references/           # Optional - Documentation
    │   └── helm-patterns.md
    └── assets/               # Optional - Templates/files
        └── templates/
            └── deployment.yaml
```

### The SKILL.md File (REQUIRED)

This is the only required file. It has two parts:

```markdown
---
name: kubernetes-deploy
description: Deploy applications to Kubernetes clusters using Helm charts. 
  Use when deploying containers, creating services, or managing K8s resources.
---

# Kubernetes Deployment Skill

## Purpose
Deploy applications to Kubernetes with battle-tested patterns.

## When to Use
- Deploying Docker containers to K8s
- Creating Helm charts
- Setting up Ingress, Services, Deployments

## Steps
1. First, check if Helm chart exists...
2. Create namespace if needed...
[etc.]
```

### Key Points:

| Part | Purpose |
|------|---------|
| **YAML Frontmatter** | `name` and `description` - Claude uses this to decide WHEN to use the skill |
| **Markdown Body** | Detailed instructions - Only loaded AFTER Claude decides to use the skill |

---

## 🌐 What are "Cloud-Native Blueprints"?

**Blueprints** = Reusable infrastructure patterns that:
1. Turn complex infrastructure (Helm, K8s, Dapr) into simple building blocks
2. Have clear inputs/outputs
3. Can be triggered by natural language

### The Hackathon Requirement

From the hackathon document:
> **"+200 pts: Create and use Cloud-Native Blueprints via Agent Skills"**

This means creating Claude Skills that contain:
- **Helm chart templates** for deploying the TeamFlow app
- **Kubernetes manifests** for common deployments
- **Dapr component configurations** for event-driven architecture
- **kubectl-ai/Gordon command patterns**

---

## 🎓 How Claude Discovers & Uses Skills

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SKILL LIFECYCLE                                    │
│                                                                             │
│  1. DISCOVERY                                                               │
│     ┌──────────────────────────────────────────────────────────────────┐   │
│     │ Claude reads ALL skill descriptions from .claude/skills/         │   │
│     │ Only the name + description (~100 words each)                    │   │
│     └──────────────────────────────────────────────────────────────────┘   │
│                                    ↓                                        │
│  2. MATCHING                                                                │
│     ┌──────────────────────────────────────────────────────────────────┐   │
│     │ User: "Deploy my app to Kubernetes using a Helm chart"          │   │
│     │ Claude: "Does this match any skill description?"                 │   │
│     │         → kubernetes-deploy skill matches! ✅                     │   │
│     └──────────────────────────────────────────────────────────────────┘   │
│                                    ↓                                        │
│  3. LOADING                                                                 │
│     ┌──────────────────────────────────────────────────────────────────┐   │
│     │ Claude reads the FULL SKILL.md body                              │   │
│     │ Also available: scripts/, references/, assets/                    │   │
│     └──────────────────────────────────────────────────────────────────┘   │
│                                    ↓                                        │
│  4. EXECUTION                                                               │
│     ┌──────────────────────────────────────────────────────────────────┐   │
│     │ Claude follows the skill's instructions                          │   │
│     │ Uses scripts, templates, and references as needed                │   │
│     └──────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Creating Your Cloud-Native Blueprint Skills

### Example 1: Kubernetes Deploy Skill

**Purpose:** Standardize how Claude deploys apps to Kubernetes

```
.claude/skills/kubernetes-deploy/
├── SKILL.md
├── assets/
│   └── templates/
│       ├── deployment.yaml
│       ├── service.yaml
│       └── ingress.yaml
└── references/
    └── common-issues.md
```

**SKILL.md:**
```markdown
---
name: kubernetes-deploy
description: Deploy containerized applications to Kubernetes using Helm or raw manifests. 
  Use when: (1) deploying Docker images to K8s, (2) creating/updating Helm charts, 
  (3) configuring Services, Deployments, or Ingress.
---

# Kubernetes Deployment Skill

## Purpose
Deploy applications to Kubernetes clusters with production-ready configurations.

## Quick Reference

### Minikube Deployment Steps
1. Ensure Minikube is running: `minikube status`
2. Use Minikube's Docker: `eval $(minikube docker-env)`
3. Build image: `docker build -t app-name:latest .`
4. Apply manifests or install Helm chart

### Helm Chart Creation
Use templates from `assets/templates/` as starting points:
- Copy deployment.yaml template
- Update image, ports, and resources
- Set proper labels and selectors

## Template Files

### Deployment Template
```yaml
# Use: assets/templates/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Values.name }}
spec:
  replicas: {{ .Values.replicas }}
  template:
    spec:
      containers:
      - name: {{ .Values.name }}
        image: {{ .Values.image }}
        ports:
        - containerPort: {{ .Values.port }}
```

## Common Issues
See `references/common-issues.md` for troubleshooting.
```

---

### Example 2: Dapr Integration Skill

**Purpose:** Help Claude configure Dapr components correctly

```
.claude/skills/dapr-integration/
├── SKILL.md
├── assets/
│   └── components/
│       ├── pubsub-kafka.yaml
│       ├── state-postgres.yaml
│       └── secrets-k8s.yaml
└── references/
    └── building-blocks.md
```

**SKILL.md:**
```markdown
---
name: dapr-integration
description: Configure Dapr for microservices communication. Use when: (1) setting up 
  Pub/Sub messaging, (2) configuring state stores, (3) enabling service invocation,
  (4) managing secrets with Dapr, or (5) scheduling jobs with Dapr Jobs API.
---

# Dapr Integration Skill

## Quick Start

### Install Dapr on Kubernetes
```bash
dapr init -k --runtime-version 1.14.0
```

### Verify Installation
```bash
dapr status -k
kubectl get pods -n dapr-system
```

## Component Templates

### Kafka Pub/Sub
Use `assets/components/pubsub-kafka.yaml`:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
spec:
  type: pubsub.kafka
  metadata:
    - name: brokers
      value: "kafka-broker:9092"
```

### PostgreSQL State Store
Use `assets/components/state-postgres.yaml` for state management.

## Publishing Events (Python)
```python
import httpx

DAPR_PORT = 3500

async def publish_event(topic: str, data: dict):
    await httpx.post(
        f"http://localhost:{DAPR_PORT}/v1.0/publish/kafka-pubsub/{topic}",
        json=data
    )
```

## Subscribing to Events
Add subscription endpoint in your FastAPI app:
```python
@app.get("/dapr/subscribe")
async def subscribe():
    return [{"pubsubname": "kafka-pubsub", "topic": "task-events", "route": "/events"}]
```
```

---

### Example 3: AIOps Commands Skill

**Purpose:** Document and standardize AI-assisted operations

```
.claude/skills/aiops-kubernetes/
├── SKILL.md
└── references/
    ├── kubectl-ai-commands.md
    ├── kagent-commands.md
    └── gordon-commands.md
```

**SKILL.md:**
```markdown
---
name: aiops-kubernetes
description: AI-assisted Kubernetes operations using kubectl-ai, kagent, and Docker 
  AI (Gordon). Use when: (1) deploying with natural language, (2) troubleshooting K8s issues, 
  (3) optimizing Dockerfiles, (4) analyzing cluster health.
---

# AIOps Kubernetes Skill

## Tools Overview

| Tool | Purpose | When to Use |
|------|---------|-------------|
| kubectl-ai | Natural language K8s commands | Deploying, scaling, debugging |
| kagent | Cluster analysis and optimization | Health checks, resource planning |
| Gordon | Docker AI assistance | Dockerfile optimization, container help |

## kubectl-ai Commands

### Deployment
```bash
kubectl-ai "deploy backend with 3 replicas exposing port 8000"
kubectl-ai "create horizontal pod autoscaler for backend when CPU > 70%"
```

### Troubleshooting
```bash
kubectl-ai "why are the pods in pending state"
kubectl-ai "show logs from backend pods with errors"
kubectl-ai "what's using the most memory in teamflow namespace"
```

## Docker Gordon Commands
```bash
docker ai "optimize this Dockerfile for smaller image size"
docker ai "what's the best base image for a Python FastAPI app"
docker ai "create multi-stage build for this project"
```

## Best Practices
1. Always document commands used (for hackathon submission)
2. Start with kubectl-ai for quick operations
3. Use kagent for deeper analysis
4. Pair with Minikube for zero-cost testing
```

---

## 📋 Creating Your Skills: Step by Step

### Step 1: Plan What Skills You Need

For the TeamFlow hackathon, consider these skills:

| Skill Name | Purpose | Bonus Value |
|------------|---------|-------------|
| `kubernetes-deploy` | Helm charts, K8s manifests | Part of +200 |
| `dapr-integration` | Dapr components, event patterns | Part of +200 |
| `aiops-kubernetes` | kubectl-ai, kagent, Gordon commands | Part of +200 |
| `docker-build` | Dockerfile optimization patterns | Part of +200 |

### Step 2: Create Skill Directory

```bash
# Navigate to skills directory
cd .claude/skills

# Create new skill folder
mkdir kubernetes-deploy
cd kubernetes-deploy

# Create required file
touch SKILL.md

# Create optional directories
mkdir assets references scripts
```

### Step 3: Write SKILL.md

1. **Start with frontmatter** (critical for triggering)
2. **Add clear purpose section**
3. **Include practical examples**
4. **Reference assets/scripts**

### Step 4: Add Assets (Templates)

Put reusable templates in `assets/`:
- Helm chart templates
- K8s YAML manifests
- Dapr component files
- Dockerfile templates

### Step 5: Test the Skill

1. Ask Claude something that should trigger the skill
2. Verify Claude loads and follows the skill
3. Iterate on instructions if needed

---

## 🎯 What This Means for Your Hackathon

**To get the +200 bonus points:**

1. **Create 2-3 Cloud-Native skills** in `.claude/skills/`:
   - `kubernetes-deploy` - For K8s/Helm deployment patterns
   - `dapr-integration` - For Dapr configuration patterns
   - `aiops-kubernetes` - For AI-assisted operations

2. **Include useful templates** in each skill:
   - Helm chart templates
   - Dapr component YAMLs
   - Common kubectl-ai/Gordon commands

3. **Actually use the skills** during development:
   - Document when skills were triggered
   - Show how they helped streamline deployment

4. **Demonstrate value**:
   - Skills should be reusable across projects
   - They should encode your "hard-won knowledge"

---

## 📚 Summary

| Concept | Meaning |
|---------|---------|
| **Claude Code Skill** | Folder with SKILL.md that teaches Claude specialized tasks |
| **Cloud-Native Blueprint** | Skill that packages infrastructure patterns (Helm, K8s, Dapr) |
| **Frontmatter** | YAML section with name + description (triggers the skill) |
| **Assets** | Template files that Claude uses in output |
| **References** | Documentation Claude reads for context |
| **Scripts** | Executable code for deterministic operations |

---

*This guide is part of the TeamFlow hackathon project. Create your skills in `.claude/skills/` to earn the +200 bonus points.*
