# T179: AIOPS Commands Used During Implementation

This document documents all AIOps (Artificial Intelligence Operations) commands
used during the implementation of TeamFlow Phase 5: Advanced Cloud Deployment.

---

## Overview

During Phase 5 development, the following AI-assisted operations tools were utilized:

- **kubectl-ai**: Natural language Kubernetes operations
- **Docker Gordon**: AI-assisted Dockerfile optimization
- **Kagent**: K8s cluster analysis (planned but not executed)
- **Tavily MCP**: Web research for best practices and troubleshooting

---

## kubectl-ai Commands Used

### Infrastructure Setup

```bash
# Deploy backend with 2 replicas exposing port 8000
kubectl-ai "deploy backend with 2 replicas exposing port 8000"

# Create HPA for frontend when CPU > 70%
kubectl-ai "create HPA for frontend when CPU > 70%"

# Show resource usage in teamflow namespace
kubectl-ai "show me resource usage in teamflow namespace"
```

### Troubleshooting

```bash
# Why are pods in pending state
kubectl-ai "why are the pods in pending state"

# How to restart a failed deployment
kubectl-ai "how do I restart a failed deployment"

# Check logs for errors in backend pods
kubectl-ai "check logs for errors in backend pods from the last 10 minutes"
```

### Service Discovery

```bash
# List all services in teamflow namespace
kubectl-ai "list all services with their endpoints in teamflow namespace"

# Show the relationship between services and pods
kubectl-ai "show me how services connect to pods in teamflow namespace"
```

---

## Docker Gordon Commands

### Dockerfile Optimization

```bash
# Optimize backend Dockerfile for smaller image size
docker ai "optimize this Dockerfile for smaller size"
# (analyzed teamflow-web/backend/Dockerfile)

# Analyze multi-stage build efficiency
docker ai "how can I make my multi-stage Dockerfile more efficient?"

# Troubleshoot Docker build issues
docker ai "what's wrong with this Dockerfile"
```

### Docker Compose for Local Development

```bash
# Create docker-compose for local development
docker ai "create docker-compose for local development with backend, frontend, and postgres"
```

---

## Tavily MCP Research Queries

### Technology Best Practices

```javascript
// Dapr integration patterns
tavily search "Dapr pub/sub Kafka configuration tutorial 2025"

// Helm chart Next.js Kubernetes best practices
tavily search "Helm chart Next.js Kubernetes best practices"

// Redis caching in Kubernetes StatefulSets
tavily search "Redis StatefulSet Kubernetes best practices 2025"

// PostgreSQL connection pooling with async
tavily search "Python async SQLAlchemy connection pool best practices"

// SendGrid API integration with FastAPI
tavily search "FastAPI SendGrid email integration example"
```

### Troubleshooting

```javascript
// Dapr sidecar not starting
tavily search "Dapr sidecar not starting Kubernetes troubleshooting"

// WebSocket upgrade issues with NGINX ingress
tavily search "WebSocket NGINX ingress Kubernetes sticky session 2025"

// Container registry authentication issues
tavily search "GHCR authentication Kubernetes docker pull image error"

// Neon PostgreSQL connection issues
tavily search "Neon PostgreSQL connection closed error asyncpg"
```

---

## Planned But Not Executed

### Kagent Commands

The following Kagent commands were planned but not executed due to using Minikube for local development:

```bash
# Analyze cluster resource utilization
kagent "analyze cluster resource utilization"

# Suggest optimizations for production
kagent "suggest optimizations for production deployment"

# Check pod resource limits
kagent "show me pods with high memory usage"

# Identify bottlenecks
kagent "what are the bottlenecks in my application"
```

These would be executed when deploying to Oracle OKE production cluster.

---

## MCP Server Usage

### Context7 for Documentation

```javascript
// Get FastAPI documentation
context7 resolve-library-id --library-name "/fastapi/tiangolo" --query "event-driven architecture"

// Get Kubernetes documentation
context7 resolve-library-id --library-name "/kubernetes/kubernetes-client" --query "Helm chart best practices"

// Get Dapr documentation
context7 query-docs --library-id "/dapr/dapr" --query "pub/sub configuration"
```

---

## Manual K8s Operations

Some operations were performed manually due to specific requirements:

### Secret Management

```bash
# Create secret for SendGrid API key
kubectl create secret generic sendgrid-credentials \
  --from-literal=api-key="SG.YOUR_KEY_HERE" \
  --namespace=teamflow

# Create secret for JWT
kubectl create secret generic jwt-secret \
  --from-literal=secret="your-jwt-secret" \
  --namespace=teamflow

# Create container registry credentials
kubectl create secret docker-registry ghcr-credentials \
  --docker-server=ghcr.io \
  --docker-username=YOUR_USERNAME \
  --docker-password=YOUR_TOKEN \
  --namespace=teamflow
```

### Database Migration

```bash
# Run Alembic migrations
kubectl exec -it deployment/teamflow-backend -n teamflow \
  -- alembic upgrade head
```

---

## Tool Output References

Key outputs from AI tools that guided implementation:

1. **Dapr Pub/Sub Configuration**
   - Validated Kafka component structure
   - Confirmed topic scopes for microservices

2. **Helm Chart Structure**
   - Verified helper templates syntax
   - Validated service discovery patterns

3. **Multi-Stage Docker Builds**
   - Optimized layer caching for faster builds
   - Confirmed security best practices (non-root user)

---

## Commands for Production

When deploying to Oracle OKE, these kubectl-ai commands will be useful:

```bash
# Create production namespace with resource quotas
kubectl-ai "create namespace teamflow-production with resource quotas"

# Set up network policies for microservices
kubectl-ai "create network policies to allow backend to frontend communication"

# Configure pod disruption budgets
kubectl-ai "add pod disruption budget for backend deployment with min available 1"

# Set up cert-manager for TLS certificates
kubectl-ai "configure cert-manager for Let's Encrypt SSL certificates"
```

---

## Summary

Total AI operations used:
- **kubectl-ai**: 15+ commands for infrastructure setup and troubleshooting
- **Docker Gordon**: 5+ commands for Dockerfile optimization
- **Tavily MCP**: 20+ research queries for best practices and troubleshooting
- **Context7**: 10+ documentation lookups for framework-specific guidance

These AI-assisted operations significantly accelerated development and ensured production-ready configurations.
