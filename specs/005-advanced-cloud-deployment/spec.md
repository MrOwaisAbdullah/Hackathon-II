# Feature Specification: TeamFlow Advanced Cloud Deployment

**Feature Branch**: `005-advanced-cloud-deployment`
**Created**: 2026-01-29
**Status**: Draft
**Input**: User description: "Phase 5: TeamFlow Advanced Cloud Deployment - Implement event-driven microservices architecture with Dapr sidecar integration, Kafka/Redpanda event streaming, and cloud Kubernetes deployment. Add advanced features: recurring tasks, due date reminders, real-time sync. Deploy to Oracle OKE (Always Free tier) with CI/CD pipeline via GitHub Actions."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Recurring Task Automation (Priority: P1)

As a project manager, I want to set up tasks that automatically recur on a schedule so that I don't have to manually create the same task every week or month.

**Why this priority**: Recurring tasks are a fundamental project management feature. Teams frequently have repeatable work (weekly reports, monthly maintenance, daily check-ins) that should be automated. This delivers immediate productivity value.

**Independent Test**: Can be tested by creating a single recurring task and verifying that when marked complete, the next instance is automatically created with correct date calculations. Delivers hands-free task management for repeatable work.

**Acceptance Scenarios**:

1. **Given** a user creates a task with recurrence rule "weekly on Monday", **When** they mark that task complete, **Then** a new task instance is automatically created for the following Monday
2. **Given** a user creates a daily recurring task with an end date of December 31, **When** the task completes on December 31, **Then** no new instance is created (recurrence ends)
3. **Given** a recurring task is set for "every Friday at 2 PM", **When** the current instance is completed on Friday, **Then** the next instance appears for the following Friday at 2 PM

---

### User Story 2 - Due Date Reminders (Priority: P2)

As a team member, I want to receive automatic reminders before my tasks are due so that I never miss a deadline.

**Why this priority**: Missed deadlines are a primary source of project delays. Automated reminders help users stay on track without manual monitoring. This feature directly improves project reliability and team accountability.

**Independent Test**: Can be tested by creating a task with a due date, setting a reminder preference, and verifying that notification is sent at the specified time before the deadline. Delivers proactive deadline awareness.

**Acceptance Scenarios**:

1. **Given** a user sets a task due date for tomorrow at 5 PM and selects "1 day before" reminder, **When** today at 5 PM arrives, **Then** the user receives an email reminder about the upcoming deadline
2. **Given** a user sets a reminder for "15 minutes before" a task is due, **When** the deadline is 15 minutes away, **Then** a push notification appears on all their connected devices
3. **Given** a task due date passes without completion, **When** the system checks for overdue tasks, **Then** an escalation reminder is sent to both the assignee and their manager

---

### User Story 3 - Real-Time Task Updates (Priority: P3)

As a team member, I want to see task changes instantly across all my devices so that I'm always working with current information without refreshing.

**Why this priority**: Real-time collaboration prevents conflicts where multiple users unknowingly work on stale data. This is increasingly important as teams work remotely and across time zones.

**Independent Test**: Can be tested by having two users viewing the same task list, then having one user make a change, and verifying that the other user sees the update instantly without page refresh. Delivers confidence in data currency.

**Acceptance Scenarios**:

1. **Given** two users are viewing the same project dashboard, **When** user A creates a new task, **Then** user B sees the new task appear instantly in their view
2. **Given** a user has the application open on multiple devices (desktop and mobile), **When** they complete a task on desktop, **Then** the task shows as completed on mobile immediately
3. **Given** a user is viewing their task list, **When** someone assigns them a new task, **Then** a notification appears and the task list updates automatically

---

### User Story 4 - Cloud Deployment and Scaling (Priority: P4)

As a system administrator, I want the application deployed to cloud infrastructure so that it can scale to handle growing teams and provide high availability.

**Why this priority**: Cloud deployment enables the system to support real-world usage with multiple concurrent users, automatic scaling during peak times, and reliable uptime. This is foundational for production readiness.

**Independent Test**: Can be tested by deploying to a cloud Kubernetes cluster and verifying that the application is accessible, pods are running correctly, and the system responds to requests. Delivers production-ready infrastructure.

**Acceptance Scenarios**:

1. **Given** a cloud Kubernetes cluster is provisioned, **When** the deployment pipeline runs, **Then** all application services (frontend, backend, microservices) are deployed and accessible
2. **Given** increased user load on the system, **When** CPU usage exceeds 70%, **Then** additional pods automatically scale up to handle the load
3. **Given** a deployment is in progress, **When** a new version is released, **Then** existing users experience no downtime (rolling updates)

---

### User Story 5 - Automated Deployment Pipeline (Priority: P5)

As a development team, I want automated CI/CD pipelines so that code changes are tested, scanned for vulnerabilities, and deployed consistently without manual intervention.

**Why this priority**: CI/CD automation reduces deployment errors, ensures code quality through automated testing, and enables rapid iteration. This accelerates development velocity while maintaining stability.

**Independent Test**: Can be tested by pushing a code change and observing the full pipeline execution: build, test, security scan, and deployment. Delivers consistent, reliable deployment workflow.

**Acceptance Scenarios**:

1. **Given** a developer pushes code to the feature branch, **When** the CI pipeline runs, **Then** all tests pass and the code is built into a container image
2. **Given** a container image is built, **When** the security scanning stage runs, **Then** vulnerabilities are reported and builds with critical vulnerabilities are blocked
3. **Given** code passes all checks, **When** deployed to staging, **Then** integration tests run and production deployment requires manual approval

---

### Edge Cases

- What happens when Kafka event streaming fails and events cannot be published?
- How does the system handle when a user's email provider is down for reminder notifications?
- What happens when a recurring task's next calculated date falls on a non-working day (weekend/holiday)?
- How does the system behave when cloud cluster resource limits are exhausted?
- What happens when a WebSocket connection drops during real-time updates?
- How does the CI/CD pipeline handle deployment rollbacks when a release fails?
- What happens when the Dapr sidecar crashes but the main application continues running?
- How does the system handle database migration failures during deployment?

## Requirements *(mandatory)*

### Functional Requirements

#### Dapr Integration Requirements

- **FR-001**: All application services MUST run with Dapr sidecar enabled for event publishing and state management
- **FR-002**: System MUST publish events to Kafka topics for all task state changes (create, update, assign, complete, delete)
- **FR-003**: System MUST support Dapr state store for caching frequently accessed data (conversation state, user sessions)
- **FR-004**: System MUST use Dapr secret store for retrieving sensitive configuration (API keys, database credentials)
- **FR-005**: System MUST implement Dapr cron bindings for scheduled reminder checks

#### Event Streaming Requirements

- **FR-006**: System MUST create and maintain Kafka topics: task-events, reminders, time-logged
- **FR-007**: System MUST publish task events with schema including: event_type, task_id, project_id, user_id, timestamp, and relevant data
- **FR-008**: System MUST consume events from task-events topic to trigger downstream services (notifications, recurrence, sync)
- **FR-009**: System MUST handle event processing failures with retry logic and dead letter queue
- **FR-010**: System MUST support event replay for recovery scenarios

#### Microservices Requirements

- **FR-011**: Notification service MUST consume reminder events and send notifications via configured channels (email, push)
- **FR-012**: Recurring task service MUST consume task completion events and create next instance when applicable
- **FR-013**: Real-time sync service MUST consume task events and broadcast updates to connected WebSocket clients
- **FR-014**: Each microservice MUST be independently scalable based on load
- **FR-015**: Microservices MUST handle idempotent event processing (duplicate events must not cause duplicate actions)

#### Recurring Tasks Requirements

- **FR-016**: System MUST support recurrence rules for: daily, weekly, monthly, and custom intervals
- **FR-017**: Recurrence rule MUST include: frequency, interval, days of week, end date (optional), and maximum occurrences (optional)
- **FR-018**: When a recurring task is marked complete, system MUST automatically create next instance based on recurrence rule
- **FR-019**: System MUST display recurrence indicator on task cards and detail views
- **FR-020**: Users MUST be able to modify or stop recurrence at any time

#### Reminder Requirements

- **FR-021**: Users MUST be able to set reminder offsets: 15 minutes, 1 hour, 1 day, 1 week before due date
- **FR-022**: System MUST check for due reminders every 5 minutes using scheduled triggers
- **FR-023**: System MUST send reminders via email for all users
- **FR-024**: System MUST support push notifications for users with connected mobile devices
- **FR-025**: Reminder preferences MUST be customizable per task

#### Real-Time Updates Requirements

- **FR-026**: Frontend MUST establish WebSocket connection for receiving live task updates
- **FR-027**: Backend MUST broadcast task changes to all connected clients via WebSocket
- **FR-028**: System MUST automatically reconnect WebSocket connections when they drop
- **FR-029**: Real-time updates MUST include: task created, updated, assigned, completed, deleted
- **FR-030**: System MUST handle multiple concurrent connections from the same user across devices

#### Cloud Deployment Requirements

- **FR-031**: System MUST be deployable to cloud Kubernetes clusters (Oracle OKE, Google GKE, Azure AKS)
- **FR-032**: Deployment MUST support zero-downtime rolling updates for all services
- **FR-033**: System MUST configure horizontal pod autoscaling for backend and microservices
- **FR-034**: System MUST support environment-specific configuration (development, staging, production)
- **FR-035**: Application MUST be accessible via ingress with TLS certificates in production

#### CI/CD Requirements

- **FR-036**: Pipeline MUST trigger on every push to main and feature branches
- **FR-037**: Pipeline MUST execute: build, test, security scan, deploy staging, integration tests
- **FR-038**: Pipeline MUST require manual approval for production deployment
- **FR-039**: Security scanning MUST check container images for vulnerabilities (critical, high, medium severity)
- **FR-040**: Pipeline MUST support rollback to previous version if deployment fails

#### Monitoring and Observability Requirements

- **FR-041**: System MUST expose health check endpoints for all services
- **FR-042**: System MUST log events with sufficient detail for troubleshooting (request ID, user ID, timestamp, error details)
- **FR-043**: System MUST track and report metrics for: pod resource usage, request latency, error rates, event processing lag
- **FR-044**: Alerts MUST be configured for: service downtime, high error rates, security vulnerabilities, deployment failures

### Key Entities

- **Task Event**: Record of a task state change including event type, task details, user who triggered change, timestamp, and metadata
- **Recurrence Rule**: Configuration for repeating tasks including frequency, interval, constraints (end date, max count, specific days)
- **Reminder Settings**: Per-user and per-task configuration for when and how to send deadline notifications
- **WebSocket Connection**: Active real-time connection from a client device with associated user session and subscribed topics
- **Kafka Topic**: Event stream containing messages of a specific type (task-events, reminders, time-logged)
- **Microservice Deployment**: Kubernetes deployment with Dapr annotations, resource limits, health probes, and scaling configuration
- **Pipeline Execution**: CI/CD run with stages: build, test, security scan, deploy, including status, artifacts, and logs

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All services deploy successfully to cloud Kubernetes within 10 minutes of triggering deployment
- **SC-002**: System supports 100 concurrent users with sub-second response times for task operations
- **SC-003**: Real-time updates propagate to all connected clients within 2 seconds of data change
- **SC-004**: 95% of users receive reminder notifications before their task deadlines (measured by delivery success rate)
- **SC-005**: Recurring tasks create next instance within 30 seconds of completion
- **SC-006**: CI/CD pipeline completes full execution (build to staging deployment) in under 15 minutes
- **SC-007**: Security scanning identifies and reports 100% of vulnerabilities in container images
- **SC-008**: System maintains 99.5% uptime during normal operations (excluding planned maintenance)
- **SC-009**: Horizontal pod autoscaling adds capacity within 2 minutes of sustained 70% CPU usage
- **SC-010**: Zero downtime deployments - users experience no errors during rolling updates

## Assumptions

1. **Existing Infrastructure**: Phases I-IV are complete with working Docker images, Helm charts, and Minikube deployment
2. **External Database**: Neon PostgreSQL database is already provisioned and accessible
3. **Cloud Account**: User has or will create an account with Oracle Cloud (for OKE Always Free tier) or equivalent cloud provider
4. **Container Registry**: User has access to a container registry (Docker Hub, GitHub Container Registry, or cloud provider registry)
5. **Email Service**: User has or will set up an email service provider for sending reminder notifications (e.g., SendGrid, AWS SES, or equivalent)
6. **Development Environment**: Developer has Docker, kubectl, and helm CLIs installed and working
7. **Network Connectivity**: Internet access is available for pulling base images, Helm charts, and cloud provider APIs
8. **Kafka Choice**: Using Redpanda for Kafka implementation (simpler than Strimzi, no ZooKeeper dependency)
9. **Dapr Version**: Using Dapr 1.14+ for sidecar integration
10. **Kubernetes Version**: Using Kubernetes 1.29+ for cloud deployment

## Constraints

1. **Timeline**: Must complete implementation according to project schedule (check with team for current deadline)
2. **Budget**: Must use free-tier cloud resources where possible (Oracle OKE Always Free provides 4 OCPUs, 24GB RAM)
3. **Technology Stack**: Must use existing technology choices (Next.js, FastAPI, Neon DB, Docker, Kubernetes)
4. **Dapr Integration**: Must use Dapr building blocks for pub/sub, state, secrets, and bindings (no custom event streaming implementation)
5. **Backward Compatibility**: Changes must be compatible with existing Phase IV Minikube deployment
6. **Security**: Must not expose secrets in git repository; use Kubernetes secrets or external secret managers
7. **Container Size**: Docker images should remain under 500MB for efficient deployment
8. **Multi-Region**: Initial deployment will be single-region; multi-region is out of scope for this phase
9. **Database Migrations**: Must support incremental database migrations without data loss
10. **Testing**: Must include automated tests for all new functionality

## Dependencies

1. **Phase IV Completion**: Local Kubernetes deployment with Minikube must be working
2. **Dapr CLI**: Dapr CLI must be installed for local testing
3. **Helm Charts**: Existing Helm charts from Phase IV will be extended with Dapr annotations
4. **Kafka Cluster**: Redpanda cluster must be deployed (local Minikube or cloud)
5. **Email Provider**: Email service API credentials must be configured
6. **Cloud Credentials**: Kubernetes cluster credentials and cloud provider API keys
7. **Container Registry**: Access to push and pull container images
8. **Domain Name**: Optional custom domain for ingress (can use default cluster domain initially)
9. **Monitoring Tools**: Optional Prometheus/Grafana setup for observability
10. **Notification Service**: Push notifications handled via PWA (Progressive Web App) with Web Push API - no external service required

## Out of Scope

The following items are explicitly out of scope for this feature:

1. **Multi-Cloud Deployment**: Deployment spanning multiple cloud providers simultaneously
2. **Service Mesh**: Istio, Linkerd, or other service mesh technologies (Dapr provides service-to-service communication)
3. **Advanced Monitoring**: Distributed tracing (OpenTelemetry), APM tools (Datadog, New Relic) - basic metrics only
4. **Database Replication**: Multi-region database replication or read replicas
5. **Advanced Caching**: Redis or other caching layers beyond Dapr state store
6. **Message Queue Alternatives**: RabbitMQ, AWS SQS, or other message brokers (Kafka/Redpanda only)
7. **Custom Dapr Components**: Building custom Dapr components (using standard components only)
8. **Internationalization (i18n)**: Multi-language support beyond existing Phase III capabilities
9. **Mobile Applications**: Native mobile apps (web application must be mobile-responsive)
10. **Advanced Security**: Zero-trust networking, advanced threat detection, compliance certifications

## Notes

### Architecture Overview

This phase transforms the TeamFlow application from a monolithic Kubernetes deployment to an event-driven microservices architecture:

**Phase IV Architecture (Current)**:
- Frontend (Next.js) → Backend (FastAPI) → Database (Neon PostgreSQL)
- Direct synchronous calls between services
- Basic Kubernetes deployment with Minikube

**Phase V Architecture (Target)**:
- Frontend (Next.js + WebSocket) ↔ Backend (FastAPI + Dapr) ↔ Event Bus (Kafka/Redpanda)
- Event-driven communication between decoupled services
- Three additional microservices: Notification, Recurring Task, Real-Time Sync
- Cloud Kubernetes deployment with CI/CD automation

### Implementation Phases

**Phase 5-A**: Local Dapr + Kafka Development (3-4 days)
- Install Dapr CLI and initialize on Minikube
- Deploy Kafka/Redpanda cluster locally
- Create Dapr components (pubsub, state, secrets, cron bindings)
- Update backend with Dapr client integration
- Implement event publishing for all task operations
- Develop and test microservices locally
- Add advanced features (recurring tasks, reminders, real-time sync)

**Phase 5-B**: Cloud Deployment (2-3 days)
- Create cloud account (Oracle OKE recommended for Always Free tier)
- Provision Kubernetes cluster
- Build and push container images to registry
- Deploy Kafka/Redpanda to cloud
- Deploy application with Helm charts
- Configure ingress and TLS certificates
- Verify end-to-end functionality

**Phase 5-C**: CI/CD Pipeline (2 days)
- Create GitHub Actions workflow
- Configure build, test, and security scan stages
- Set up staging deployment with integration tests
- Add manual approval gate for production
- Configure deployment notifications
- Test full pipeline execution
- Document rollback procedures

### Technology Choices

**Kafka/Redpanda vs Strimzi**: Redpanda is recommended because it eliminates ZooKeeper dependency, has simpler deployment, and is fully Kafka-compatible. This reduces complexity for hackathon timeline while providing production-ready event streaming.

**Oracle OKE vs Other Cloud Providers**: Oracle OKE Always Free tier offers 4 OCPUs and 24GB RAM at no cost, making it ideal for hackathon. Alternatives include Google GKE ($74.40 one-time credit) and Azure AKS (free control plane), but both incur ongoing costs.

**CI/CD Tools**: GitHub Actions is chosen because it integrates directly with the repository, provides generous free tier for public repositories, and supports all required stages (build, test, scan, deploy).

### Bonus Points Opportunities

| Bonus Feature | Points | Implementation Path |
|---------------|--------|-------------------|
| **Reusable Intelligence** | +200 | Create agent skills for Dapr/Kafka patterns in `.claude/skills/` |
| **Cloud-Native Blueprints** | +200 | Document K8s deployment blueprints with templates |
| **Multi-language (Urdu)** | +100 | Extend Phase III chatbot with Urdu language support |
| **Voice Commands** | +200 | Add Web Speech API integration for task commands |

### Testing Strategy

**Unit Testing**: Test individual functions (event publishing, recurrence calculation, reminder scheduling)
**Integration Testing**: Test event flow from publication through Kafka to consumer services
**End-to-End Testing**: Test complete user journeys (create recurring task → complete → next instance created)
**Load Testing**: Verify system handles 100 concurrent users with acceptable performance
**Security Testing**: Validate secrets management, vulnerability scanning, and access controls

### Troubleshooting

**Dapr Sidecar Issues**:
- Check if Dapr is installed: `dapr status -k`
- Verify annotations in pod spec: `kubectl describe pod <pod-name>`
- Check Dapr sidecar logs: `kubectl logs <pod-name> -c daprd`

**Kafka Connection Issues**:
- Verify Kafka is running: `kubectl get pods -l app=kafka`
- Check Kafka topics: `kubectl get kafkatopics`
- Test connectivity from pod: `kubectl exec -it <pod-name> -- nc -zv <kafka-service> 9092`

**Real-Time Updates Not Working**:
- Check WebSocket connection in browser developer tools Network tab
- Verify real-time sync service is consuming events
- Check backend logs for WebSocket connection errors

**Deployment Failures**:
- Check pod status: `kubectl get pods -n teamflow`
- Describe failed pod: `kubectl describe pod <pod-name> -n teamflow`
- View pod logs: `kubectl logs <pod-name> -n teamflow`
- Check resource usage: `kubectl top pods -n teamflow`

**CI/CD Pipeline Failures**:
- Check GitHub Actions logs for specific stage failure
- Verify container registry credentials are correctly configured
- Test deployment locally before pushing to repository
- Check Kubernetes cluster connectivity from GitHub Actions runner
