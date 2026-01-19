# Tasks: TeamFlow Kubernetes Deployment on Minikube

**Input**: Design documents from `/specs/001-k8s-minikube-deployment/`
**Prerequisites**: plan.md (required), spec.md (required for user stories)

**Tests**: Tests are OPTIONAL for this feature - the focus is on infrastructure deployment validation rather than unit tests. Validation is performed through deployment verification commands.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Frontend**: `teamflow-web/frontend/`
- **Backend**: `teamflow-web/backend/`
- **Helm Charts**: `helm/teamflow/`
- **Documentation**: `docs/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Verify prerequisites are installed (Docker, Minikube, kubectl, Helm)
- [ ] T002 Verify external Neon PostgreSQL database is accessible
- [ ] T003 Confirm application codebase is complete and working locally
- [ ] T004 Verify cloud-native-blueprints skill is available at `.claude/skills/cloud-native-blueprints/`

**Checkpoint**: Prerequisites verified - ready to begin containerization

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core containerization infrastructure that MUST be complete before ANY deployment tasks

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T005 [P] Create frontend .dockerignore file in teamflow-web/frontend/.dockerignore
- [ ] T006 [P] Create backend .dockerignore file in teamflow-web/backend/.dockerignore
- [ ] T007 Modify next.config.ts in teamflow-web/frontend/next.config.ts to enable standalone output mode

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Containerize Application for Kubernetes (Priority: P1) 🎯 MVP

**Goal**: Package the TeamFlow application (frontend and backend) into containers so that it can be deployed consistently across any Kubernetes environment

**Independent Test**: Build Docker images locally and verify they start successfully without errors. Delivers portable, versioned application artifacts under 500MB each.

### Implementation for User Story 1

- [ ] T008 [US1] Create frontend Dockerfile in teamflow-web/frontend/Dockerfile with multi-stage build (node:22-alpine, non-root user, standalone output)
- [ ] T009 [US1] Optimize backend Dockerfile in teamflow-web/backend/Dockerfile with multi-stage build (python:3.13-slim, non-root user, health check)
- [ ] T010 [US1] Build frontend Docker image locally: `cd teamflow-web/frontend && docker build -t teamflow/frontend:latest .`
- [ ] T011 [US1] Build backend Docker image locally: `cd teamflow-web/backend && docker build -t teamflow/backend:latest .`
- [ ] T012 [US1] Verify frontend image size under 500MB: `docker images | grep teamflow-frontend`
- [ ] T013 [US1] Verify backend image size under 500MB: `docker images | grep teamflow-backend`
- [ ] T014 [US1] Test frontend container locally: `docker run -p 3000:3000 teamflow/frontend:latest` (verify serves on port 3000)
- [ ] T015 [US1] Test backend container locally: `docker run -p 8000:8000 teamflow/backend:latest` (verify health check responds)

**Checkpoint**: At this point, User Story 1 should be fully functional - both images built, under 500MB, and runnable locally

---

## Phase 4: User Story 2 - Deploy to Local Minikube Cluster (Priority: P2)

**Goal**: Deploy the containerized TeamFlow application to a local Minikube cluster so that it can be tested in a Kubernetes environment before cloud deployment

**Independent Test**: Deploy to Minikube and verify all pods reach Running state. Delivers a working Kubernetes deployment that mirrors production.

### Implementation for User Story 2

- [ ] T016 [P] [US2] Create Helm chart directory structure: helm/teamflow/ with templates/ subdirectory
- [ ] T017 [P] [US2] Create Chart.yaml in helm/teamflow/Chart.yaml with metadata (apiVersion: v2, version: 1.0.0)
- [ ] T018 [US2] Create values.yaml in helm/teamflow/values.yaml with namespace, frontend/backend config, resources, ingress settings
- [ ] T019 [P] [US2] Create _helpers.tpl template in helm/teamflow/templates/_helpers.tpl with standard Helm helpers
- [ ] T020 [P] [US2] Create namespace template in helm/teamflow/templates/namespace.yaml
- [ ] T021 [P] [US2] Create ConfigMap template in helm/teamflow/templates/configmap.yaml for NEXT_PUBLIC_API_URL
- [ ] T022 [P] [US2] Create secrets template in helm/teamflow/templates/secrets.yaml for DATABASE_URL, OPENAI_API_KEY, BETTER_AUTH_SECRET
- [ ] T023 [US2] Create frontend deployment template in helm/teamflow/templates/frontend-deployment.yaml (2 replicas, rolling update, resource limits, probes)
- [ ] T024 [US2] Create frontend service template in helm/teamflow/templates/frontend-service.yaml (ClusterIP:3000)
- [ ] T025 [US2] Create backend deployment template in helm/teamflow/templates/backend-deployment.yaml (2 replicas, rolling update, resource limits, probes)
- [ ] T026 [US2] Create backend service template in helm/teamflow/templates/backend-service.yaml (ClusterIP:8000)
- [ ] T027 [US2] Create ingress template in helm/teamflow/templates/ingress.yaml for external access (nginx ingress, path-based routing)
- [ ] T028 [US2] Validate Helm chart passes linting: `helm lint ./helm/teamflow` (zero errors, zero warnings)
- [ ] T029 [US2] Validate Helm templates render successfully: `helm template teamflow ./helm/teamflow --debug` (no errors)
- [ ] T030 [US2] Start Minikube cluster with required resources: `minikube start --cpus=4 --memory=8192 --driver=docker`
- [ ] T031 [US2] Enable Minikube addons: `minikube addons enable ingress && minikube addons enable metrics-server`
- [ ] T032 [US2] Create secrets file in helm/teamflow/secrets.yaml (gitignored) with actual database URL and API keys
- [ ] T033 [US2] Build images in Minikube Docker daemon:
  ```bash
  eval $(minikube docker-env)
  cd teamflow-web/backend && docker build -t teamflow/backend:latest .
  cd ../frontend && docker build -t teamflow/frontend:latest .
  ```
- [ ] T034 [US2] Install Helm chart to Minikube: `helm install teamflow ./helm/teamflow --namespace teamflow --create-namespace -f helm/teamflow/secrets.yaml`
- [ ] T035 [US2] Verify all pods reach Running state within 5 minutes: `kubectl get pods -n teamflow -w`
- [ ] T036 [US2] Verify services are created: `kubectl get services -n teamflow`
- [ ] T037 [US2] Test backend service access via port-forward: `kubectl port-forward svc/teamflow-backend 8000:8000 -n teamflow && curl http://localhost:8000/health`
- [ ] T038 [US2] Test frontend service access via port-forward: `kubectl port-forward svc/teamflow-frontend 3000:3000 -n teamflow` (open http://localhost:3000 in browser)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - images containerized and deployed to Minikube with all pods Running

---

## Phase 5: User Story 3 - Validate End-to-End Application Functionality (Priority: P3)

**Goal**: Verify that the deployed application works end-to-end in Kubernetes so that deployment success can be confirmed

**Independent Test**: Access the deployed application and perform core user flows. Delivers confidence in the deployment quality.

### Implementation for User Story 3

- [ ] T039 [US3] Verify frontend login page loads without errors via ingress or port-forward
- [ ] T040 [US3] Verify backend connects to external Neon PostgreSQL database (check logs for successful connection message)
- [ ] T041 [US3] Test user login flow: access frontend, enter credentials, verify authentication
- [ ] T042 [US3] Test dashboard navigation: after login, verify dashboard displays tasks and projects
- [ ] T043 [US3] Test task creation: create new task via UI, verify it persists and appears in task list
- [ ] T044 [US3] Test frontend-backend communication: verify API calls succeed without errors
- [ ] T045 [US3] Verify database operations: test read/write operations through the application UI
- [ ] T046 [US3] Verify frontend load time under 3 seconds: `curl -w "%{time_total}" http://localhost:3000 -o /dev/null`
- [ ] T047 [US3] Verify backend health endpoint responds under 500ms: `curl -w "%{time_total}" http://localhost:8000/health -o /dev/null`
- [ ] T048 [US3] Verify resource usage within limits: `kubectl top -n teamflow` (CPU and memory within defined limits)
- [ ] T049 [US3] Test zero-downtime rolling update: `kubectl rollout restart deployment/teamflow-backend -n teamflow` during user activity, verify no 5xx errors

**Checkpoint**: All user stories should now be independently functional - containerized, deployed, and validated end-to-end

---

## Phase 6: User Story 4 - Document AIOps Command Usage (Priority: P4)

**Goal**: Document all AI-assisted operations (Gordon, kubectl-ai, Kagent) so that hackathon judges can verify AIOps tool usage

**Independent Test**: Review the documentation file and verify all commands used during implementation are recorded with their results

### Implementation for User Story 4

- [ ] T050 [P] [US4] Create AIOps documentation file in docs/PHASE4-AIOPS-COMMANDS.md with header and structure
- [ ] T051 [US4] Document all Docker Gordon (docker ai) commands used during implementation with purpose and results
- [ ] T052 [US4] Document all kubectl-ai commands used during implementation with purpose and results
- [ ] T053 [US4] Document all Kagent commands used during implementation with purpose and results
- [ ] T054 [US4] Verify documentation includes command syntax, purpose, and outcome/output for each command
- [ ] T055 [US4] Verify documentation file is complete and accurately reflects all AIOps tool usage

**Checkpoint**: All user stories complete - containerization, deployment, validation, and documentation finished

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, cleanup, and deployment readiness

- [ ] T056 Verify all success criteria (SC-001 to SC-012) are met using verification matrix from plan.md
- [ ] T057 Run pre-deployment checklist from plan.md Section 12.1 (14 items)
- [ ] T058 Run post-deployment verification from plan.md Section 12.2 (10 items)
- [ ] T059 Document rollback procedures: test `helm rollback teamflow 1 -n teamflow` and verify rollback works
- [ ] T060 Clean up test resources: `helm uninstall teamflow -n teamflow` and `kubectl delete namespace teamflow` (optional, for cleanup)
- [ ] T061 Create deployment summary document with all verification results and known issues

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (Phase 4)**: Depends on User Story 1 completion - needs images from US1
- **User Story 3 (Phase 5)**: Depends on User Story 2 completion - needs deployed application from US2
- **User Story 4 (Phase 6)**: Can start in parallel with US2/US3 as commands are used throughout implementation
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Depends on User Story 1 - requires container images from US1
- **User Story 3 (P3)**: Depends on User Story 2 - requires deployed application from US2
- **User Story 4 (P4)**: No dependencies on other stories - documentation can be done in parallel

### Within Each User Story

**User Story 1 (Containerization)**:
- T008 and T009 (Dockerfiles) can run in parallel
- T010 and T011 (build images) must wait for Dockerfiles
- T012 and T013 (verify sizes) can run in parallel after builds
- T014 and T015 (test containers) can run in parallel after builds

**User Story 2 (Minikube Deployment)**:
- T016-T022 (Helm templates) can run in parallel (different files)
- T023-T027 (deployment/service templates) must wait for T018 (values.yaml)
- T028-T029 (validation) must wait for all templates
- T030-T032 (Minikube setup) can run in parallel after validation
- T033 (build images) must wait for T030-T032
- T034-T038 (deploy and verify) must wait for T033

**User Story 3 (Validation)**:
- T039-T049 (validation tests) can mostly run in parallel after deployment is complete
- T049 (rolling update test) should be last to test deployment stability

**User Story 4 (Documentation)**:
- T050-T055 can run in parallel as they document different tool categories

### Parallel Opportunities

- **Setup (Phase 1)**: T001-T004 can all run in parallel (independent checks)
- **Foundational (Phase 2)**: T005-T007 can all run in parallel (different files)
- **User Story 1**: T008-T009 (Dockerfiles) parallel, T010-T011 (builds) parallel, T012-T013 (size checks) parallel, T014-T015 (container tests) parallel
- **User Story 2**: T016-T022 (Helm chart files) parallel, T030-T032 (Minikube setup) parallel
- **User Story 3**: T039-T048 (validation tests) mostly parallel
- **User Story 4**: T050-T055 (documentation sections) parallel

---

## Parallel Example: User Story 1 (Containerization)

```bash
# Launch both Dockerfile creations together:
Task: "Create frontend Dockerfile in teamflow-web/frontend/Dockerfile"
Task: "Optimize backend Dockerfile in teamflow-web/backend/Dockerfile"

# After Dockerfiles complete, launch both builds together:
Task: "Build frontend Docker image locally"
Task: "Build backend Docker image locally"

# After builds complete, launch both size verifications together:
Task: "Verify frontend image size under 500MB"
Task: "Verify backend image size under 500MB"

# Finally, launch both container tests together:
Task: "Test frontend container locally (port 3000)"
Task: "Test backend container locally (port 8000)"
```

---

## Parallel Example: User Story 2 (Helm Chart Creation)

```bash
# Launch all Helm chart file creations together (after values.yaml exists):
Task: "Create _helpers.tpl template in helm/teamflow/templates/_helpers.tpl"
Task: "Create namespace template in helm/teamflow/templates/namespace.yaml"
Task: "Create ConfigMap template in helm/teamflow/templates/configmap.yaml"
Task: "Create secrets template in helm/teamflow/templates/secrets.yaml"
Task: "Create frontend deployment template in helm/teamflow/templates/frontend-deployment.yaml"
Task: "Create frontend service template in helm/teamflow/templates/frontend-service.yaml"
Task: "Create backend deployment template in helm/teamflow/templates/backend-deployment.yaml"
Task: "Create backend service template in helm/teamflow/templates/backend-service.yaml"
Task: "Create ingress template in helm/teamflow/templates/ingress.yaml"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (prerequisites verification)
2. Complete Phase 2: Foundational (.dockerignore files, next.config.ts modification)
3. Complete Phase 3: User Story 1 (containerization)
4. **STOP and VALIDATE**: Test both images independently - verify sizes under 500MB, containers run locally
5. **MVP DELIVERABLE**: Portable container images ready for deployment

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Container images ready (MVP!)
3. Add User Story 2 → Test independently → Deploy to Minikube (Working Deployment!)
4. Add User Story 3 → Test independently → End-to-end validated (Production-Ready!)
5. Add User Story 4 → Documentation complete → Hackathon Submission Ready!
6. Polish & Validate → Final verification and cleanup

### Sequential Team Strategy

Single developer (most likely for hackathon):

1. Complete Setup + Foundational together
2. Implement User Story 1 (containerization) - validate images
3. Implement User Story 2 (Minikube deployment) - validate deployment
4. Implement User Story 3 (E2E validation) - validate functionality
5. Implement User Story 4 (documentation) - document AIOps commands
6. Polish and final validation

---

## Success Criteria Validation

All tasks align with success criteria from spec.md:

- **SC-001** (Images < 500MB): Validated by T012, T013
- **SC-002** (Templates render): Validated by T029
- **SC-003** (Helm linting): Validated by T028
- **SC-004** (Pods Running in 5 min): Validated by T035
- **SC-005** (Frontend < 3s): Validated by T046
- **SC-006** (Health endpoint < 500ms): Validated by T047
- **SC-007** (Database connection): Validated by T040
- **SC-008** (Login flow): Validated by T041
- **SC-009** (Task persistence): Validated by T043
- **SC-010** (AIOps documented): Validated by T051-T055
- **SC-011** (Zero-downtime rolling update): Validated by T049
- **SC-012** (Resource limits): Validated by T048

---

## Format Validation

**All tasks follow the strict checklist format:**

✅ **Checkbox**: Every task starts with `- [ ]`
✅ **Task ID**: Sequential T001-T061 in execution order
✅ **[P] marker**: Applied to parallelizable tasks (different files, no dependencies)
✅ **[Story] label**: Applied to all user story phase tasks (US1, US2, US3, US4)
✅ **File paths**: All implementation tasks include exact file paths
✅ **Clear descriptions**: Each task has specific, actionable description

**Format Validation Results:**
- Total tasks: 61
- Tasks with [P] marker: 22 (parallelizable)
- Tasks with [Story] label: 30 (user story tasks)
- Setup tasks (no label): 4
- Foundational tasks (no label): 3
- Polish tasks (no label): 6

**Organization by User Story:**
- User Story 1 (Containerization): 8 tasks (T008-T015)
- User Story 2 (Minikube Deployment): 23 tasks (T016-T038)
- User Story 3 (Validation): 11 tasks (T039-T049)
- User Story 4 (Documentation): 6 tasks (T050-T055)

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- User Story 1 (containerization) is the MVP foundation
- User Story 2 requires User Story 1 completion (needs container images)
- User Story 3 requires User Story 2 completion (needs deployed application)
- User Story 4 can run in parallel with other stories (documentation only)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Use verification matrix from plan.md for each success criterion
- Follow troubleshooting guide in plan.md Section 11 if issues arise
- Document AIOps commands as they are used for accurate T051-T053 completion
