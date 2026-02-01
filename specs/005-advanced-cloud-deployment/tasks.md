# Tasks: TeamFlow Advanced Cloud Deployment (Phase 5)

**Input**: Design documents from `/specs/005-advanced-cloud-deployment/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are included for TDD compliance as specified in the constitution.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `teamflow-web/backend/app/`
- **Frontend**: `teamflow-web/frontend/src/`
- **Microservices**: `teamflow-web/backend/microservices/`
- **Dapr Components**: `dapr-components/`
- **Helm Charts**: `helm/teamflow/templates/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 [P] Create `.env.example` file with all required environment variables for Dapr, Kafka, and cloud services
- [X] T002 [P] Create `dapr-components/` directory structure for component configurations
- [X] T003 [P] Create `k8s/` directory for raw Kubernetes manifests (backup to Helm)
- [X] T004 [P] Create `helm/teamflow/charts/` subdirectory for microservice Helm charts
- [X] T005 [P] Install Python dependencies: `dapr-dev`, `sendgrid`, `python-dateutil`, `structlog` in `teamflow-web/backend/pyproject.toml`
- [X] T006 [P] Install frontend dependencies: `reconnecting-websocket`, `eventemitter3`, `next-pwa` in `teamflow-web/frontend/package.json`
- [X] T007 [P] Create `teamflow-web/backend/app/dapr/` directory with `__init__.py` for Dapr integration layer
- [X] T008 Create `.github/workflows/phase5-cloud-deploy.yml` for CI/CD pipeline skeleton
- [X] T008a [P] [CLARIFICATION] Push notification approach: Use PWA (Progressive Web App) with Web Push API for browser-based push notifications - no external service (Firebase) required for Phase 5. Add service worker registration in `teamflow-web/frontend/src/app/layout.tsx`

**Checkpoint**: Project structure ready for Dapr and microservices implementation ✅

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T009 Create Dapr Pub/Sub component configuration in `dapr-components/pubsub.kafka.yaml` for Redpanda brokers
- [X] T010 Create Dapr State Store component in `dapr-components/state.postgresql.yaml` for Neon PostgreSQL caching
- [X] T011 Create Dapr Secret Store component in `dapr-components/secretstores.kubernetes.yaml` for K8s secrets
- [X] T012 [P] Create Dapr Cron Binding in `dapr-components/bindings/reminder-checker.cron.yaml` for scheduled reminder checks (every 5 minutes)
- [X] T013 [P] Create Dapr Cron Binding in `dapr-components/bindings/task-cleanup.cron.yaml` for daily task cleanup (2 AM)
- [X] T014 Implement `EventPublisher` class in `teamflow-web/backend/app/services/event_publisher.py` with Dapr HTTP client for Kafka publishing
- [X] T015 [P] Implement `RecurrenceCalculator` class in `teamflow-web/backend/app/services/recurrence_calculator.py` with dateutil.rrule for next instance calculation
- [X] T016 [P] Implement `ReminderScheduler` class in `teamflow-web/backend/app/services/reminder_scheduler.py` for calculating reminder times based on offsets
- [X] T017 Create base `DaprClient` wrapper in `teamflow-web/backend/app/dapr/pubsub.py` for async event publishing
- [X] T018 [P] Create base `DaprStateClient` in `teamflow-web/backend/app/dapr/state.py` for caching conversation state
- [X] T019 [P] Create base `DaprSecretClient` in `teamflow-web/backend/app/dapr/secrets.py` for retrieving secrets from K8s
- [X] T020 Add `/dapr/subscribe` endpoint to `teamflow-web/backend/app/main.py` returning subscription routes for all services
- [X] T021 Add `/health` and `/ready` endpoints to `teamflow-web/backend/app/main.py` for Kubernetes liveness/readiness probes
- [X] T022 Update `teamflow-web/backend/Dockerfile` with multi-stage build optimizing for Dapr sidecar integration
- [X] T023 Update `teamflow-web/frontend/Dockerfile` with production build optimizations and WebSocket support
- [X] T024 Create base Helm chart values in `helm/teamflow/values.yaml` with Dapr annotations placeholder
- [X] T025 Update `helm/teamflow/templates/backend-deployment.yaml` with Dapr sidecar annotations (`dapr.io/enabled: "true"`)
- [X] T026 Update `helm/teamflow/templates/frontend-deployment.yaml` with Dapr sidecar annotations
- [X] T027 Create Kubernetes namespace manifest in `k8s/base/namespace.yaml` for teamflow resources
- [X] T028 Create resource quota manifest in `k8s/base/resource-quotas.yaml` for Oracle OKE Always Free limits

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel ✅

---

## Phase 3: User Story 1 - Recurring Task Automation (Priority: P1) 🎯 MVP

**Goal**: Automatically create next instance of recurring tasks when current instance is completed

**Independent Test**: Create a single recurring task with rule "weekly on Monday", mark it complete, verify next instance appears for following Monday with correct due date

### Tests for User Story 1 (TDD Compliance) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T029 [P] [US1] Unit test for recurrence calculation in `teamflow-web/backend/tests/test_recurrence_calculator.py` - test daily recurrence with interval
- [X] T030 [P] [US1] Unit test for recurrence calculation in `teamflow-web/backend/tests/test_recurrence_calculator.py` - test weekly recurrence with specific days
- [X] T031 [P] [US1] Unit test for recurrence calculation in `teamflow-web/backend/tests/test_recurrence_calculator.py` - test monthly recurrence with day of month
- [X] T032 [P] [US1] Unit test for recurrence calculation in `teamflow-web/backend/tests/test_recurrence_calculator.py` - test end date constraint
- [X] T033 [P] [US1] Unit test for recurrence calculation in `teamflow-web/backend/tests/test_recurrence_calculator.py` - test max occurrences constraint
- [X] T034 [P] [US1] Integration test in `teamflow-web/backend/tests/test_recurring_task_service.py` - test task completion event triggers next instance creation
- [X] T035 [P] [US1] Integration test in `teamflow-web/backend/tests/test_recurring_task_service.py` - test non-recurring task completion does NOT create instance
- [X] T036 [P] [US1] Integration test in `teamflow-web/backend/tests/test_recurring_task_service.py` - test recurrence stops when end date reached

### Implementation for User Story 1

- [X] T037 [P] [US1] Create Alembic migration in `teamflow-web/backend/alembic/versions/001_add_recurrence_reminder_fields.py` - add `recurrence_rule`, `reminder_settings`, `next_instance_id` columns to tasks table
- [X] T038 [P] [US1] Create Alembic migration in `teamflow-web/backend/alembic/versions/002_create_task_events.py` - create `task_events` table for event log
- [X] T039 [P] [US1] Create `RecurrenceRule` Pydantic model in `teamflow-web/backend/app/models/recurrence.py` with validation for frequency, interval, days_of_week, end_date, max_occurrences, time_of_day (optional - for "every Friday at 2 PM" scenario)
- [X] T040 [P] [US1] Create `ReminderSettings` Pydantic model in `teamflow-web/backend/app/models/reminder.py` with validation for offsets, channels, custom_message
- [X] T041 [P] [US1] Create `TaskEvent` Pydantic model in `teamflow-web/backend/app/models/event.py` with CloudEvents envelope fields
- [X] T042 [US1] Update `Task` model in `teamflow-web/backend/app/models/task.py` - add `recurrence_rule`, `reminder_settings`, `next_instance_id` fields
- [X] T043 [US1] Update `TaskService` in `teamflow-web/backend/app/services/task_service.py` - emit `task.completed` event on task completion with recurrence_rule payload
- [X] T044 [US1] Update `TaskService` in `teamflow-web/backend/app/services/task_service.py` - set `next_instance_id` when creating recurring task instance
- [X] T045 [US1] Create `RecurringTaskService` FastAPI app in `teamflow-web/backend/microservices/recurring_task_service/main.py`
- [X] T046 [US1] Add `/dapr/subscribe` endpoint in `recurring_task_service/main.py` - subscribe to `task-events` topic for `completed` events
- [X] T047 [US1] Add `/events/task-events` route in `recurring_task_service/main.py` - consume task completion events, filter for recurring tasks
- [X] T048 [US1] Implement recurrence logic in `recurring_task_service/main.py` - calculate next instance date using `RecurrenceCalculator`
- [X] T049 [US1] Implement next instance creation in `recurring_task_service/main.py` - call backend API to create new task with same fields
- [X] T050 [US1] Add `/health` and `/ready` endpoints in `recurring_task_service/main.py` for Kubernetes probes
- [X] T051 [US1] Create `Dockerfile` in `teamflow-web/backend/microservices/recurring_task_service/` with multi-stage Python 3.13-slim build
- [X] T052 [US1] Create Helm chart in `helm/teamflow/charts/recurring-task-service/` with deployment, service, HPA manifests
- [X] T053 [US1] Add Dapr annotations to `recurring-task-service` deployment - enable sidecar with app-id `recurring-task-service`
- [X] T054 [US1] Create `RecurrenceDialog.tsx` component in `teamflow-web/frontend/src/components/tasks/` for recurrence rule configuration UI
- [X] T055 [US1] Update `TaskForm.tsx` in `teamflow-web/frontend/src/components/tasks/` - integrate `RecurrenceDialog` component
- [X] T056 [US1] Add recurrence fields to `TaskForm.tsx` - frequency dropdown, interval input, days of week multi-select, end date picker
- [X] T057 [US1] Update Task type in `teamflow-web/frontend/src/types/index.ts` - include `recurrence_rule`, `reminder_settings`, `next_instance_id` fields
- [X] T058 [US1] Add recurrence indicator badge to `TaskCard.tsx` - display recurring icon when `recurrence_rule` is present
- [X] T059 [US1] Add logging for recurring task operations using structlog - log next instance creation with task_id, calculated_date
- [X] T059a [US1] Implement weekend/holiday business day handling in `RecurrenceCalculator.calculate_next_instance()` - if next calculated date falls on Saturday/Sunday, skip to Monday; if falls on holiday, skip to next business day (configurable via user preference)

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Due Date Reminders (Priority: P2)

**Goal**: Send automatic email/push notifications before task deadlines based on user preferences

**Independent Test**: Create task with due date tomorrow and reminder "1 day before", verify email received at correct time

### Tests for User Story 2 (TDD Compliance) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T060 [P] [US2] Unit test in `teamflow-web/backend/tests/test_reminder_scheduler.py` - test reminder time calculation for "15m" offset
- [X] T061 [P] [US2] Unit test in `teamflow-web/backend/tests/test_reminder_scheduler.py` - test reminder time calculation for "1h" offset
- [X] T062 [P] [US2] Unit test in `teamflow-web/backend/tests/test_reminder_scheduler.py` - test reminder time calculation for "1d" offset
- [X] T063 [P] [US2] Unit test in `teamflow-web/backend/tests/test_reminder_scheduler.py` - test reminder time calculation for "1w" offset
- [X] T064 [P] [US2] Unit test in `teamflow-web/backend/tests/test_reminder_scheduler.py` - test multiple reminder offsets create multiple reminder events
- [X] T065 [P] [US2] Integration test in `teamflow-web/backend/tests/test_notification_service.py` - test reminder event triggers email send
- [X] T066 [P] [US2] Integration test in `teamflow-web/backend/tests/test_notification_service.py` - test failed email send triggers retry with backoff

### Implementation for User Story 2

- [X] T067 [P] [US2] Create Alembic migration in `teamflow-web/backend/alembic/versions/003_create_reminder_events.py` - create `reminder_events` table for tracking sent reminders
- [X] T068 [P] [US2] Create `ReminderEvent` Pydantic model in `teamflow-web/backend/app/models/reminder_event.py` with status tracking (pending/sent/failed)
- [X] T069 [US2] Create `SendGridEmailClient` in `teamflow-web/backend/microservices/notification_service/email_client.py` with async send method
- [X] T070 [US2] Create `NotificationService` FastAPI app in `teamflow-web/backend/microservices/notification_service/main.py`
- [X] T071 [US2] Add `/dapr/subscribe` endpoint in `notification_service/main.py` - subscribe to `reminders` topic
- [X] T072 [US2] Add `/events/reminders` route in `notification_service/main.py` - consume reminder events from Kafka
- [X] T073 [US2] Implement email sending in `notification_service/main.py` - call `SendGridEmailClient` with task details and due date
- [X] T074 [US2] Add error handling and retry logic in `notification_service/main.py` - queue failed emails for retry with exponential backoff
- [X] T075 [US2] Add `/health` endpoint in `notification_service/main.py` - check SendGrid API connectivity
- [X] T076 [US2] Add `/ready` endpoint in `notification_service/main.py` for Kubernetes readiness probe
- [X] T077 [US2] Create `Dockerfile` in `teamflow-web/backend/microservices/notification_service/` with multi-stage Python build
- [X] T078 [US2] Create Helm chart in `helm/teamflow/charts/notification-service/` with deployment, service, HPA manifests
- [X] T079 [US2] Add Dapr annotations to `notification-service` deployment - enable sidecar with app-id `notification-service`
- [X] T080 [US2] Create Kubernetes secret manifest in `k8s/secrets/sendgrid-credentials.yaml` - store SENDGRID_API_KEY
- [X] T081 [US2] Update `ReminderScheduler` in `teamflow-web/backend/app/services/reminder_scheduler.py` - calculate reminder times based on task due_at and reminder_settings.offsets
- [X] T082 [US2] Update `TaskService` in `teamflow-web/backend/app/services/task_service.py` - call `ReminderScheduler` on task create/update to generate reminder events
- [X] T083 [US2] Publish reminder events to `reminders` topic via `EventPublisher` in `TaskService`
- [X] T084 [US2] Create `ReminderSettings.tsx` component in `teamflow-web/frontend/src/components/notifications/` for reminder preference UI
- [X] T085 [US2] Update `TaskForm.tsx` in `teamflow-web/frontend/src/components/tasks/` - integrate `ReminderSettings` component
- [X] T086 [US2] Add reminder fields to `TaskForm.tsx` - multi-select for offsets (15m, 1h, 1d, 1w), channels (email, push), custom message input
- [X] T087 [US2] Update task API client in `teamflow-web/frontend/src/services/api.ts` - include `reminder_settings` in create/update task requests
- [X] T088 [US2] Add reminder indicator to `TaskCard.tsx` - display bell icon when `reminder_settings` is present
- [X] T089 [US2] Add logging for reminder operations - log reminder scheduled, sent, failed events with task_id, remind_at

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Real-Time Task Updates (Priority: P3)

**Goal**: Instant task changes broadcast to all connected clients via WebSocket without page refresh

**Independent Test**: Two users viewing same task list - user A creates task, user B sees it appear instantly without refresh

### Tests for User Story 3 (TDD Compliance) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T090 [P] [US3] Unit test in `teamflow-web/backend/tests/test_connection_manager.py` - test WebSocket connection registration
- [X] T091 [P] [US3] Unit test in `teamflow-web/backend/tests/test_connection_manager.py` - test WebSocket broadcast to single user
- [X] T092 [P] [US3] Unit test in `teamflow-web/backend/tests/test_connection_manager.py` - test WebSocket broadcast to all users
- [X] T093 [P] [US3] Unit test in `teamflow-web/backend/tests/test_connection_manager.py` - test WebSocket disconnection cleanup
- [X] T094 [P] [US3] Integration test in `teamflow-web/frontend/tests/useTaskEvents.test.ts` - test WebSocket connection establishment
- [X] T095 [P] [US3] Integration test in `teamflow-web/frontend/tests/useTaskEvents.test.ts` - test task_created event triggers UI update
- [X] T096 [P] [US3] Integration test in `teamflow-web/frontend/tests/useTaskEvents.test.ts` - test task_updated event triggers UI update
- [X] T097 [P] [US3] Integration test in `teamflow-web/frontend/tests/useTaskEvents.test.ts` - test WebSocket reconnection after disconnect

### Implementation for User Story 3

- [X] T098 [P] [US3] Create `ConnectionManager` class in `teamflow-web/backend/microservices/realtime_sync_service/connection_manager.py` with WebSocket connection pooling
- [X] T099 [P] [US3] Create `WebSocketConnection` class in `teamflow-web/backend/microservices/realtime_sync_service/connection_manager.py` with connection metadata
- [X] T100 [US3] Create `RealtimeSyncService` FastAPI app in `teamflow-web/backend/microservices/realtime_sync_service/main.py`
- [X] T101 [US3] Add `/dapr/subscribe` endpoint in `realtime_sync_service/main.py` - subscribe to `task-updates` and `task-events` topics
- [X] T102 [US3] Add `/events/task-updates` route in `realtime_sync_service/main.py` - consume task update events from Kafka
- [X] T103 [US3] Add `/events/task-events` route in `realtime_sync_service/main.py` - consume all task events for broadcasting
- [X] T104 [US3] Implement event broadcasting in `realtime_sync_service/main.py` - use `ConnectionManager.broadcast()` to send to connected clients
- [X] T105 [US3] Add `WebSocket` endpoint `/ws/tasks` in `realtime_sync_service/main.py` - accept connections with JWT token auth
- [X] T106 [US3] Implement JWT validation in `/ws/tasks` endpoint - extract user_id from token, register connection
- [X] T107 [US3] Add heartbeat ping mechanism in `/ws/tasks` endpoint - send ping every 30s, expect pong within 60s
- [X] T108 [US3] Add `/health` endpoint in `realtime_sync_service/main.py` - report active connections count
- [X] T109 [US3] Add `/ws/health` endpoint in `realtime_sync_service/main.py` - WebSocket-specific health check
- [X] T110 [US3] Create `Dockerfile` in `teamflow-web/backend/microservices/realtime_sync_service/` with multi-stage Python build
- [X] T111 [US3] Create Helm chart in `helm/teamflow/charts/realtime-sync-service/` with deployment, service, HPA manifests
- [X] T112 [US3] Create Kubernetes Service manifest for `realtime-sync-service` - type ClusterIP, port 8000
- [X] T113 [US3] Note: Do NOT add Dapr sidecar to `realtime-sync-service` - use direct K8s service for WebSocket (Dapr doesn't support WebSocket upgrade)
- [X] T114 [US3] Update `helm/teamflow/templates/ingress.yaml` - add WebSocket route with `/ws` path and sticky sessions
- [X] T115 [US3] Create `TaskEventStream` class in `teamflow-web/frontend/src/services/websocket.ts` with auto-reconnect logic
- [X] T116 [US3] Implement `connect()` method in `TaskEventStream` - establish WebSocket connection with JWT token
- [X] T117 [US3] Implement exponential backoff reconnect in `TaskEventStream` - retry with 2^n second delays on disconnect
- [X] T118 [US3] Create `useTaskEvents` hook in `teamflow-web/frontend/src/hooks/useTaskEvents.ts` - subscribe to WebSocket events
- [X] T119 [US3] Create `useRealtimeTasks` hook in `teamflow-web/frontend/src/hooks/useRealtimeTasks.ts` - auto-updating task list
- [X] T120 [US3] Update `TaskList.tsx` in `teamflow-web/frontend/src/components/tasks/` - integrate `useRealtimeTasks` hook
- [X] T121 [US3] Add event handlers in `TaskList.tsx` - update local state on task_created, task_updated, task_deleted events
- [X] T122 [US3] Add connection status indicator to UI - show "Connected", "Reconnecting...", "Disconnected" states
- [X] T123 [US3] Add logging for WebSocket operations - log connection, disconnection, broadcast events

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: User Story 4 - Cloud Deployment (Priority: P4)

**Goal**: Deploy full stack to Oracle OKE Always Free tier with production configuration

**Independent Test**: Deploy to Oracle OKE cluster, verify all pods running, application accessible via ingress

- [X] T124 [US4] Follow `docs/EXTERNAL-SERVICES-SETUP.md` - create Oracle Cloud account (30-45 min)
- [X] T125 [US4] Follow `docs/EXTERNAL-SERVICES-SETUP.md` - create OCI compartment and get OCID
- [X] T126 [US4] Follow `docs/EXTERNAL-SERVICES-SETUP.md` - create OKE cluster with Always Free tier resources
- [X] T127 [US4] Follow `docs/EXTERNAL-SERVICES-SETUP.md` - configure kubectl with OKE cluster credentials
- [X] T128 [US4] Follow `docs/EXTERNAL-SERVICES-SETUP.md` - deploy Redpanda to OKE via Helm with resource limits
- [X] T129 [US4] Follow `docs/EXTERNAL-SERVICES-SETUP.md` - create Kafka topics (task-events, reminders, time-logged, task-updates)
- [X] T130 [US4] Initialize Dapr on OKE cluster with `dapr init -k --runtime-version 1.14.0`
- [X] T131 [US4] Create production values file in `helm/teamflow/values-production.yaml` with Oracle OKE resource limits
- [X] T132 [US4] Build and push backend image to GHCR: `docker push ghcr.io/yourusername/teamflow-backend:latest`
- [X] T133 [US4] Build and push frontend image to GHCR: `docker push ghcr.io/yourusername/teamflow-frontend:latest`
- [X] T134 [US4] Build and push microservice images to GHCR - notification, recurring-task, realtime-sync services
- [X] T135 [US4] Create GitHub Container Registry secret in Kubernetes: `kubectl create secret docker-registry ghcr-credentials`
- [X] T136 [US4] Install Dapr components on OKE: `kubectl apply -f dapr-components/` (all component YAML files)
- [X] T137 [US4] Deploy application to OKE via Helm: `helm install teamflow ./helm/teamflow --namespace teamflow --create-namespace -f values-production.yaml`
- [X] T138 [US4] Create Kubernetes Ingress manifest in `helm/teamflow/templates/ingress.yaml` for external access
- [X] T139 [US4] Configure TLS certificate for ingress using Let's Encrypt or Oracle OKE certificate manager
- [X] T140 [US4] Verify deployment: `kubectl get pods -n teamflow` - all pods Running state
- [X] T141 [US4] Verify Redpanda topics: `kubectl exec -it redpanda-0 -n kafka -- rpk topic list`
- [X] T144 [US4] Verify Dapr components: `kubectl get components -n teamflow`
- [X] T145 [US4] Test end-to-end: create task via API, verify event appears in Kafka topic
- [X] T146 [US4] Test recurring task: create recurring task, complete it, verify next instance created
- [X] T147 [US4] Test reminders: create task with due date and reminder, verify email received
- [X] T148 [US4] Test real-time sync: open two browser windows, verify changes appear instantly in both
- [X] T149 [US4] Configure Horizontal Pod Autoscaler in Helm chart - add HPA for backend and microservices
- [X] T150 [US4] Set up Prometheus/Grafana for monitoring (optional but recommended)

**Checkpoint**: Cloud deployment complete and validated

---

## Phase 7: User Story 5 - Automated Deployment Pipeline (Priority: P5)

**Goal**: CI/CD automation via GitHub Actions with build, test, security scan, and deployment stages

**Independent Test**: Push code change to feature branch, observe full pipeline execution: build → test → scan → deploy staging

- [X] T151 [US5] Create GitHub Actions workflow skeleton in `.github/workflows/deploy.yml`
- [X] T152 [US5] Add workflow trigger on push to main and feature branches
- [X] T153 [US5] Add workflow trigger on pull_request to main branch
- [X] T154 [US5] Create Stage 1: "Build and Test" job - run backend pytest tests
- [X] T155 [US5] Create Stage 1: "Build and Test" job - run frontend vitest tests in parallel
- [X] T156 [US5] Create Stage 2: "Security Scan" job - build backend Docker image
- [X] T157 [US5] Create Stage 2: "Security Scan" job - run Trivy scanner on backend image (CRITICAL, HIGH severity)
- [X] T158 [US5] Create Stage 2: "Security Scan" job - upload Trivy results to GitHub Security tab
- [X] T159 [US5] Create Stage 3: "Build Images" job - login to GHCR registry using GitHub token
- [X] T160 [US5] Create Stage 3: "Build Images" job - build and push backend image with SHA tag
- [X] T161 [US5] Create Stage 3: "Build Images" job - build and push frontend image with SHA tag (parallel)
- [X] T162 [US5] Create Stage 3: "Build Images" job - build and push microservice images (parallel)
- [X] T163 [US5] Create Stage 4: "Deploy Staging" job - configure kubectl with GitHub Secret KUBE_CONFIG
- [X] T164 [US5] Create Stage 4: "Deploy Staging" job - Helm upgrade to teamflow-staging namespace
- [X] T165 [US5] Create Stage 5: "Integration Tests" job - run Playwright E2E tests against staging environment
- [X] T166 [US5] Create Stage 6: "Deploy Production" job - add manual approval gate using GitHub environments
- [X] T167 [US5] Create Stage 6: "Deploy Production" job - Helm upgrade to teamflow-production namespace with production values
- [X] T168 [US5] Add GitHub Secrets configuration documentation to `docs/EXTERNAL-SERVICES-SETUP.md`
- [X] T169 [US5] Store KUBE_CONFIG as GitHub Secret (base64-encoded kubeconfig file)
- [X] T170 [US5] Store SENDGRID_API_KEY as GitHub Secret
- [X] T171 [US5] Store OCI_API_KEY as GitHub Secret (optional, for cluster management)
- [X] T172 [US5] Add workflow status badge to README.md
- [X] T173 [US5] Test pipeline: push to feature branch, verify all stages execute
- [X] T174 [US5] Test security scan: push image with intentional vulnerability, verify scan catches it
- [X] T175 [US5] Test staging deployment: verify staging namespace receives deployment
- [X] T176 [US5] Test production approval: verify manual approval gate requires click
- [X] T177 [US5] Document rollback procedure: `helm rollback teamflow 1 -n teamflow-production`

**Checkpoint**: All user stories complete with full CI/CD automation

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T178 [P] Update README.md with Phase 5 architecture diagram and setup instructions
- [X] T179 [P] Create `docs/AIOPS-COMMANDS-USED.md` - document all kubectl-ai, Kagent, and Gordon commands used during implementation
- [X] T180 [P] Create `docs/DEPLOYMENT-TROUBLESHOOTING.md` - common deployment issues and solutions
- [X] T181 [P] Update `CLAUDE.md` with Phase 5 specific commands and patterns
- [X] T182 Code cleanup - remove TODO comments, consolidate duplicate code
- [X] T183 Performance optimization - add database indexes for recurrence queries
- [X] T184 [P] Add additional unit tests for edge cases (weekend recurrence handling, timezone issues)
- [X] T185 [P] Security hardening - verify no secrets in git, validate all K8s secrets are used
- [X] T186 [P] Run `quickstart.md` validation - test local development setup from scratch
- [X] T187 [P] Load testing - use k6 or Locust to verify 100 concurrent users with sub-second response times per SC-002
- [X] T187a [P] E2E test in `teamflow-web/backend/tests/e2e/test_recurring_task_journey.spec.ts` - test complete recurring task lifecycle (create → complete → next instance appears)
- [X] T187b [P] E2E test in `teamflow-web/backend/tests/e2e/test_reminder_delivery.spec.ts` - test reminder delivery (create task with due date + reminder, verify email sent via SendGrid test API)
- [X] T187c [P] E2E test in `teamflow-web/frontend/tests/e2e/test_realtime_sync.spec.ts` - test real-time updates (two users, one creates task, other sees it instantly)
- [X] T188 Create PHR for tasks phase completion using `.specify/scripts/bash/create-phr.sh`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User Story 1 (Recurring Tasks - P1): Can start after Foundational
  - User Story 2 (Reminders - P2): Can start after Foundational (independent of US1)
  - User Story 3 (Real-Time Sync - P3): Can start after Foundational (independent of US1, US2)
  - User Story 4 (Cloud Deploy - P4): Depends on US1, US2, US3 completion (need all services running)
  - User Story 5 (CI/CD - P5): Depends on US4 completion (need cloud deployment target)
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable
- **User Story 4 (P4)**: Requires US1, US2, US3 to be implemented - Deploys all services to cloud
- **User Story 5 (P5)**: Requires US4 to be implemented - Needs running cluster for deployment target

### Within Each User Story

- Tests (T029-T036 for US1) MUST be written and FAIL before implementation
- Database migrations (T037-T038 for US1) before models
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows):
  - US1, US2, US3 can be developed simultaneously by different developers
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Microservice Docker builds can run in parallel
- Helm chart creation can run in parallel

---

## Parallel Example: User Story 1 (Recurring Tasks)

```bash
# Launch all tests for User Story 1 together:
Task T029: "Unit test for recurrence calculation in teamflow-web/backend/tests/test_recurrence_calculator.py - test daily recurrence"
Task T030: "Unit test for recurrence calculation in teamflow-web/backend/tests/test_recurrence_calculator.py - test weekly recurrence"
Task T031: "Unit test for recurrence calculation in teamflow-web/backend/tests/test_recurrence_calculator.py - test monthly recurrence"
Task T032: "Unit test for recurrence calculation in teamflow-web/backend/tests/test_recurrence_calculator.py - test end date constraint"
Task T033: "Unit test for recurrence calculation in teamflow-web/backend/tests/test_recurrence_calculator.py - test max occurrences constraint"

# Launch all models for User Story 1 together:
Task T037: "Create Alembic migration 001_add_recurrence_reminder_fields.py"
Task T038: "Create Alembic migration 002_create_task_events.py"
Task T039: "Create RecurrenceRule Pydantic model in teamflow-web/backend/app/models/recurrence.py"
Task T040: "Create ReminderSettings Pydantic model in teamflow-web/backend/app/models/reminder.py"
Task T041: "Create TaskEvent Pydantic model in teamflow-web/backend/app/models/event.py"
```

---

## Parallel Example: All User Stories (After Foundation)

```bash
# Once Foundational phase (T009-T028) is complete, launch all three user stories in parallel:

# Developer A: User Story 1 (Recurring Tasks) - T029-T059
# Developer B: User Story 2 (Reminders) - T060-T089
# Developer C: User Story 3 (Real-Time Sync) - T090-T123

# All three stories complete independently, then:
# Developer D: User Story 4 (Cloud Deploy) - T124-T150
# Developer E: User Story 5 (CI/CD) - T151-T177
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T008)
2. Complete Phase 2: Foundational (T009-T028) - CRITICAL BLOCKER
3. Complete Phase 3: User Story 1 (T029-T059)
4. **STOP and VALIDATE**: Test recurring task independently
5. Deploy to Minikube for validation
6. Demo recurring task creation → completion → next instance appears

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo (Cloud!)
6. Add User Story 5 → Test independently → Deploy/Demo (CI/CD!)
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T028)
2. Once Foundational is done:
   - Developer A: User Story 1 (Recurring Tasks) - T029-T059
   - Developer B: User Story 2 (Reminders) - T060-T089
   - Developer C: User Story 3 (Real-Time Sync) - T090-T123
3. Stories complete and integrate independently
4. Developer D: User Story 4 (Cloud Deployment) - T124-T150
5. Developer E: User Story 5 (CI/CD Pipeline) - T151-T177

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing (TDD red-green-refactor)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- **Critical Path**: Foundational (T009-T028) → US1/US2/US3 (parallel) → US4 → US5

---

## Task Count Summary

- **Phase 1 (Setup)**: 8 tasks
- **Phase 2 (Foundational)**: 20 tasks (BLOCKS all user stories)
- **Phase 3 (US1 - Recurring Tasks)**: 32 tasks (includes tests)
- **Phase 4 (US2 - Reminders)**: 30 tasks (includes tests)
- **Phase 5 (US3 - Real-Time Sync)**: 36 tasks (includes tests)
- **Phase 6 (US4 - Cloud Deploy)**: 27 tasks
- **Phase 7 (US5 - CI/CD)**: 27 tasks
- **Phase 8 (Polish)**: 14 tasks

**Total**: 194 tasks across 8 phases

**Estimated Timeline**:
- Phase 1: 0.5 day
- Phase 2: 1 day (CRITICAL PATH)
- Phase 3-5 (US1-US3): 4-6 days (can run in parallel with 3 developers)
- Phase 6 (US4): 2 days
- Phase 7 (US5): 1 day
- Phase 8: 0.5 day

**Total**: 9-11 days for single developer, 5-7 days with parallel team
