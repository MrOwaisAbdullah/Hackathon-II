# TeamFlow Backend - How to Run

## Overview
The backend is a FastAPI application deployed on Minikube Kubernetes cluster. It connects to Neon PostgreSQL for data storage.

---

## Prerequisites
- ✅ Minikube installed (at `~/.local/bin/minikube` in WSL)
- ✅ Backend deployed on Minikube
- ✅ Neon PostgreSQL database configured
- ✅ Database migrations run

---

## Method 1: Access Through Frontend Proxy (Recommended)

The backend is **not directly accessible** from your browser. All API requests go through the frontend's API proxy:

```
Browser → Frontend API Proxy → Backend
```

**To test the backend API:**
1. Start the frontend service (see `FRONTEND-RUN.md`)
2. Open browser to the frontend URL
3. The frontend will proxy API requests to the backend

**Test API endpoint:**
```
POST http://127.0.0.1:XXXXX/api/v1/auth/login
Content-Type: application/json

{
  "email": "admin@test.com",
  "password": "password123"
}
```

---

## Method 2: WSL Terminal - Direct Access

### Step 1: Open WSL
- Press `Win + R`
- Type `wsl` and press Enter

### Step 2: Navigate to Project
```bash
cd "/mnt/d/GIAIC/Quarter 4/Hackathon II"
```

### Step 3: Start Backend Service Tunnel
```bash
~/.local/bin/minikube service teamflow-backend -n teamflow
```

This will show a URL like: `http://127.0.0.1:34825`

### Step 4: Test Backend Directly
```bash
# Test health endpoint
curl http://127.0.0.1:34825/health

# Test login endpoint
curl -X POST http://127.0.0.1:34825/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@test.com","password":"password123"}'
```

---

## Method 3: kubectl Port Forwarding

### Step 1: Open WSL Terminal

### Step 2: Port Forward Backend
```bash
~/.local/bin/kubectl port-forward -n teamflow svc/teamflow-backend 8000:8000
```

### Step 3: Access Backend
Now accessible at: `http://localhost:8000`

Test:
```bash
curl http://localhost:8000/health
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@test.com","password":"password123"}'
```

**Stop:** Press `Ctrl+C`

---

## Database Connection

**Using:** Neon PostgreSQL (External)

**Connection String:**
```
postgresql://neondb_owner:npg_4u6wxICjUqTW@ep-shiny-hall-a1mjei2a-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require
```

**Migrations:** ✅ Already run (tables created)

---

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new agency with admin user
- `POST /api/v1/auth/login` - Login and get JWT token
- `POST /api/v1/auth/logout` - Logout (requires JWT)

### Tasks
- `GET /api/v1/tasks/` - List all tasks
- `POST /api/v1/tasks/` - Create new task
- `GET /api/v1/tasks/{id}` - Get task by ID
- `PUT /api/v1/tasks/{id}` - Update task
- `DELETE /api/v1/tasks/{id}` - Delete task

### Projects
- `GET /api/v1/projects/` - List all projects
- `POST /api/v1/projects/` - Create new project
- `GET /api/v1/projects/{id}` - Get project by ID
- `PUT /api/v1/projects/{id}` - Update project
- `DELETE /api/v1/projects/{id}` - Delete project

### Health & Metrics
- `GET /health` - Health check endpoint
- `GET /metrics` - Prometheus metrics

---

## Environment Variables

Configured via Kubernetes Secrets (`teamflow-secrets`):

| Variable | Description | Current Value |
|----------|-------------|---------------|
| `DATABASE_URL` | Neon PostgreSQL connection | `postgresql://neondb_owner:***@ep-shiny-hall...` |
| `OPENAI_API_KEY` | OpenAI API key | Configured |
| `SECRET_KEY` | JWT secret key | Configured |
| `BETTER_AUTH_SECRET` | Better Auth secret | Configured |
| `FRONTEND_URL` | CORS allowed origins | `http://localhost:3000,...` |

---

## Troubleshooting

### Issue: "Backend pods not ready"
**Solution:**
```bash
~/.local/bin/kubectl get pods -n teamflow -l app.kubernetes.io/component=backend
```

### Issue: "Database connection errors"
**Solution:** Check Neon database is accessible:
```bash
# Test connection from local machine
psql "postgresql://neondb_owner:npg_4u6wxICjUqTW@ep-shiny-hall-a1mjei2a-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"
```

### Issue: "API returning 500 errors"
**Solution:** Check backend logs:
```bash
~/.local/bin/kubectl logs -f deployment/teamflow-backend -n teamflow --tail=50
```

### Issue: "CORS errors"
**Solution:** Already configured via `FRONTEND_URL` env var. Add your frontend URL to the list if needed.

### Issue: "502 Bad Gateway / 503 Service Unavailable"
**Solution:**
1. Check pods are running: `~/.local/bin/kubectl get pods -n teamflow`
2. Check services: `~/.local/bin/kubectl get svc -n teamflow`
3. Restart backend: `~/.local/bin/kubectl rollout restart deployment/teamflow-backend -n teamflow`

### Issue: "Database tables not found"
**Solution:** Run migrations:
```bash
cd teamflow-web/backend
DATABASE_URL="postgresql://neondb_owner:npg_4u6wxICjUqTW@ep-shiny-hall-a1mjei2a-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require" alembic upgrade head
```

---

## Common Commands

### Check Backend Status
```bash
# Check pods
~/.local/bin/kubectl get pods -n teamflow -l app.kubernetes.io/component=backend

# View logs
~/.local/bin/kubectl logs -f deployment/teamflow-backend -n teamflow

# Check replica count
~/.local/bin/kubectl get deployment teamflow-backend -n teamflow
```

### Scale Backend
```bash
# Scale to 3 replicas
~/.local/bin/kubectl scale deployment teamflow-backend -n teamflow --replicas=3

# Scale back to 1
~/.local/bin/kubectl scale deployment teamflow-backend -n teamflow --replicas=1
```

### Restart Backend
```bash
~/.local/bin/kubectl rollout restart deployment teamflow-backend -n teamflow
```

### View Logs
```bash
# Follow logs
~/.local/bin/kubectl logs -f deployment/teamflow-backend -n teamflow

# Last 50 lines
~/.local/bin/kubectl logs deployment/teamflow-backend -n teamflow --tail=50

# Logs from specific pod
~/.local/bin/kubectl logs -f teamflow-backend-xxxxx -n teamflow
```

### Exec into Pod
```bash
# Get shell access to a pod
~/.local/bin/kubectl exec -it -n teamflow deployment/teamflow-backend -- sh

# Run Python command in pod
~/.local/bin/kubectl exec -n teamflow deployment/teamflow-backend -- python -c "print('Hello')"
```

---

## File Locations

- **Source Code:** `teamflow-web/backend/`
- **Main App:** `teamflow-web/backend/app/main.py`
- **Dockerfile:** `teamflow-web/backend/Dockerfile`
- **Helm Chart:** `helm/teamflow/templates/backend-deployment.yaml`
- **Config:** `teamflow-web/backend/app/core/config.py`
- **Database Models:** `teamflow-web/backend/app/models/`
- **API Endpoints:** `teamflow-web/backend/app/api/endpoints/`

---

## Development Notes

### Making Changes to Backend Code
1. Edit files in `teamflow-web/backend/app/`
2. Rebuild Docker image:
   ```bash
   cd "/mnt/d/GIAIC/Quarter 4/Hackathon II"
   eval "$(minikube docker-env)"
   docker build -t teamflow/backend:latest -f teamflow-web/backend/Dockerfile teamflow-web/backend/
   ```
3. Restart deployment:
   ```bash
   ~/.local/bin/kubectl rollout restart deployment teamflow-backend -n teamflow
   ```

### Running Migrations
If database schema changes:
```bash
cd teamflow-web/backend
DATABASE_URL="postgresql://neondb_owner:npg_4u6wxICjUqTW@ep-shiny-hall-a1mjei2a-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require" alembic upgrade head
```

### Creating New Migration
```bash
cd teamflow-web/backend
alembic revision --autogenerate -m "description of changes"
```

### Updating Environment Variables
1. Edit `helm/teamflow/values.yaml`
2. Upgrade Helm release:
   ```bash
   ~/.local/bin/helm upgrade teamflow "/mnt/d/GIAIC/Quarter 4/Hackathon II/helm/teamflow" --namespace teamflow
   ```

---

## Performance Monitoring

### Check Resource Usage
```bash
# Pod resource usage
~/.local/bin/kubectl top pods -n teamflow

# Node resource usage
~/.local/bin/kubectl top nodes
```

### Check Metrics
```bash
# Prometheus metrics endpoint
curl http://127.0.0.1:34825/metrics
```

---

## Backup & Recovery

### Backup Database
```bash
# Using pg_dump with Neon
pg_dump "postgresql://neondb_owner:npg_4u6wxICjUqTW@ep-shiny-hall-a1mjei2a-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require" > backup.sql
```

### Restore Database
```bash
psql "postgresql://neondb_owner:npg_4u6wxICjUqTW@ep-shiny-hall-a1mjei2a-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require" < backup.sql
```

---

## Summary

1. **Access Methods:**
   - **Recommended:** Through frontend API proxy (see `FRONTEND-RUN.md`)
   - **Direct:** Using WSL service tunnel
   - **Local:** Using kubectl port-forward

2. **Database:** Neon PostgreSQL (external)

3. **Test Credentials:** `admin@test.com` / `password123`

4. **Service Tunnel URL changes** - Run command again for new URL

---

**Last Updated:** January 19, 2026
**Environment:** WSL2 + Docker Desktop + Minikube
