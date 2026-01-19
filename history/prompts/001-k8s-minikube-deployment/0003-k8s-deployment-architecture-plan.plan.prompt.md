---
id: "0003"
title: "k8s deployment architecture plan"
stage: plan
date: 2026-01-18
surface: agent
model: claude-opus-4-5
feature: "001-k8s-minikube-deployment"
branch: 001-k8s-minikube-deployment
user: mrowaisabdullah
command: "/sp.plan"
labels: ["plan", "kubernetes", "minikube", "architecture", "helm"]
links:
  spec: specs/001-k8s-minikube-deployment/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-k8s-minikube-deployment/plan.md
  - history/prompts/001-k8s-minikube-deployment/0003-k8s-deployment-architecture-plan.plan.prompt.md
tests:
  - Plan completeness validated against spec requirements
  - Technical decisions documented with rationale
  - Implementation phases defined with dependencies
---

## Prompt

User invoked /sp.plan to create a comprehensive architecture plan for TeamFlow Kubernetes deployment on Minikube. The prompt included:

**Mandatory Requirements:**
- Use cloud-native-blueprints skill templates and patterns
- Research first using MCP tools (Context7 for docs, Tavily for best practices)
- Create production-ready Helm charts with multi-stage Docker builds
- Document all AIOps commands (Gordon, kubectl-ai, Kagent)
- Address all functional requirements and success criteria from spec.md

**Research Required:**
- Context7: Helm and Kubernetes documentation
- Tavily: Docker multi-stage build best practices, Next.js standalone deployment, Minikube deployment patterns

**Plan Requirements:**
- 13-section architecture document covering:
  1. Architecture Overview (system context, high-level architecture, component responsibilities, data flow)
  2. Implementation Phases (4 phases with detailed task breakdown)
  3. Technical Decisions (with rationale for each choice)
  4. Edge Case Handling (strategies for identified edge cases)
  5. File Structure (complete file tree with descriptions)
  6. Verification Matrix (mapping success criteria to commands)
  7. Risk Assessment (probability, impact, mitigation)
  8. Implementation Order (dependency graph and sequential execution)
  9. Technical Context (constitution compliance, tech stack, dependencies)
  10. Rollback Procedures (Helm rollback, image rollback, cleanup)
  11. Troubleshooting Guide (common issues and useful commands)
  12. Success Criteria Validation (pre and post deployment checklists)
  13. Next Steps

## Response snapshot

Created comprehensive architecture plan (specs/001-k8s-minikube-deployment/plan.md) with 13 complete sections:

**Key Deliverables:**

1. **Architecture Overview** (Section 1)
   - System context diagram showing Minikube cluster structure
   - Component responsibilities table
   - Data flow diagram from browser through Ingress to services and external database

2. **Implementation Phases** (Section 2)
   - Phase 1: Containerization (5 tasks) - Frontend/backend Dockerfiles, .dockerignore, next.config.ts modification, image validation
   - Phase 2: Helm Chart Development (11 tasks) - Complete chart structure with all templates
   - Phase 3: Minikube Deployment (7 tasks) - Cluster setup, image builds, deployment, verification
   - Phase 4: Validation & Documentation (3 tasks) - E2E testing, AIOps documentation, success criteria verification

3. **Technical Decisions** (Section 3)
   - Base images: node:22-alpine (frontend), python:3.13-slim (backend) with rationale
   - Health check strategy with liveness/readiness probe configurations
   - Resource allocation: Frontend (500m CPU/512Mi limits), Backend (1000m CPU/1Gi limits)
   - Secret management using Kubernetes Secrets with separate values file
   - Service exposure: ClusterIP + Ingress (not LoadBalancer or NodePort)
   - Replica strategy: 2 replicas with zero-downtime rolling update (maxUnavailable: 0, maxSurge: 1)

4. **Complete Docker Multi-Stage Builds:**

Frontend Dockerfile (3-stage):
```dockerfile
# Stage 1: Dependencies
FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json* ./
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

Backend Dockerfile (3-stage):
```dockerfile
# Stage 1: Dependencies
FROM python:3.13-slim AS deps
WORKDIR /app
COPY pyproject.toml uv.lock* ./
RUN pip install --no-cache-dir uv && uv sync

# Stage 2: Builder
FROM python:3.13-slim AS builder
WORKDIR /app
COPY --from=deps /app/.venv ./app/.venv
COPY pyproject.toml uv.lock* ./
COPY . .
RUN uv sync

# Stage 3: Runner
FROM python:3.13-slim AS runner
WORKDIR /app
RUN addgroup --system --gid 1001 appuser && \
    adduser --system --uid 1001 appuser
COPY --from=builder /app/.venv ./app/.venv
COPY --chown=appuser:appuser /app/app ./app
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s \
  CMD python -c "import httpx; httpx.get('http://localhost:8000/health').raise_for_status(200)"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

5. **Helm Chart Structure:**
- Complete Chart.yaml (v2, version 1.0.0)
- Comprehensive values.yaml with resource limits, health probes, ingress configuration
- All templates: namespace, deployments, services, configmap, secrets, ingress, _helpers
- Pre-deployment validation commands (helm lint, helm template)

6. **Verification Matrix** (Section 6)
- Mapped all 12 success criteria (SC-001 to SC-012) to specific commands
- Expected results defined for each verification step
- Performance targets: < 500MB images, < 5min startup, < 3s frontend load, < 500ms health endpoint

7. **Risk Assessment** (Section 7)
- 9 risks identified with probability/impact/mitigation
- Key risks: Image size exceeds 500MB, Database connection fails, Ingress routing issues
- Mitigation strategies documented

8. **Dependency Graph** (Section 8)
- Mermaid diagram showing task dependencies
- Sequential execution order for all 4 phases (26 tasks total)
- Critical path: Phase 1 → Phase 2 → Phase 3 → Phase 4

9. **Troubleshooting Guide** (Section 11)
- Common issues: Pods stuck Pending, Health checks failing, Frontend-backend communication, Database connection
- Useful commands for debugging (port-forward, logs, describe, exec, kubectl top)

10. **Pre/Post Deployment Checklists** (Section 12)
- 14-item pre-deployment checklist
- 10-item post-deployment verification checklist

**Research Performed:**
- Tavily search for Docker multi-stage build best practices (successful)
- Tavily search for Next.js standalone Docker Kubernetes deployment (successful)
- Tavily search for Minikube Helm deployment best practices (successful)
- Context7 calls attempted but failed with validation errors (worked around with Tavily)

**Technical Decisions Documented:**
- Base image selection with specific rationale for each choice
- Health check strategy aligned with clarification responses
- Resource allocation based on application requirements
- Zero-downtime rolling update strategy (SC-011 compliant)
- Exponential backoff retry for database reconnection (FR-032 compliant)
- CPU throttling and memory OOM kill behavior (FR-014 compliant)

## Outcome

- **Impact**: Created comprehensive 1105-line architecture plan with 13 complete sections covering all aspects of Kubernetes deployment from containerization through validation
- **Tests**: Plan completeness validated - all functional requirements addressed, all success criteria mapped to verification commands, all edge cases have mitigation strategies
- **Files**: specs/001-k8s-minikube-deployment/plan.md (1105 lines), history/prompts/001-k8s-minikube-deployment/0003-k8s-deployment-architecture-plan.plan.prompt.md
- **Next**: Ready for `/sp.tasks` to generate actionable implementation tasks with test cases and dependencies
- **Reflection**: Architecture plan successfully bridges specification to implementation with complete Docker multi-stage build examples, full Helm chart structure, detailed verification procedures, and comprehensive troubleshooting guide. All clarifications from previous phase integrated into technical decisions.

## Architectural Decisions Detected

**Decision 1: Multi-Stage Docker Build Strategy**
- Impact: High - Affects all containerization (FR-001 to FR-010), image size compliance (SC-001)
- Alternatives: Single-stage build (larger images), BuildKit-only optimization (less explicit)
- Scope: Cross-cutting - Both frontend and backend containerization

**Decision 2: ClusterIP + Ingress Service Exposure**
- Impact: High - Affects external access strategy (FR-016), Minikube compatibility
- Alternatives: LoadBalancer (requires cloud provider), NodePort (port conflicts)
- Scope: Cross-cutting - Service exposure and ingress configuration

**Decision 3: Zero-Downtime Rolling Update Strategy**
- Impact: High - Affects availability during updates (SC-011)
- Alternatives: Recreate strategy (downtime), Blue-Green deployment (higher resource cost)
- Scope: Deployment configuration for both frontend and backend

**Decision 4: Exponential Backoff Database Retry**
- Impact: Medium - Affects database connectivity resilience (FR-032)
- Alternatives: Immediate failure (user error), Linear retry (less efficient), Circuit breaker (more complex)
- Scope: Backend database connection logic

**ADR Suggestion**: 📋 Architectural decision detected: Multi-stage Docker build strategy with Alpine base images and non-root users for optimized, secure containers. Document reasoning and tradeoffs? Run `/sp.adr docker-multi-stage-build-strategy`

**ADR Suggestion**: 📋 Architectural decision detected: ClusterIP services with NGINX Ingress for Minikube-compatible external access. Document reasoning and tradeoffs? Run `/sp.adr ingress-service-exposure-strategy`

**ADR Suggestion**: 📋 Architectural decision detected: Zero-downtime rolling updates with maxUnavailable: 0 for high availability. Document reasoning and tradeoffs? Run `/sp.adr zero-downtime-rolling-update-strategy`

## Evaluation notes (flywheel)

- Failure modes observed: Context7 MCP validation errors (2 separate calls) - worked around using Tavily MCP which succeeded for all research queries
- Graders run and results (PASS/FAIL): Architecture plan completeness - PASSED (all 13 sections complete, all functional requirements addressed, all success criteria mapped)
- Prompt variant (if applicable): None
- Next experiment (smallest change to try): None required - plan creation successful on first attempt
