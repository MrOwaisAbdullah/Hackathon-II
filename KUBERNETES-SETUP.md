# TeamFlow Kubernetes Deployment - How to Run Locally

## Prerequisites

- ✅ Minikube installed (at `~/.local/bin/minikube` in WSL)
- ✅ Helm installed (at `~/.local/bin/helm` in WSL)
- ✅ Docker Desktop running
- ✅ TeamFlow deployed on Minikube

---

## Option 1: Using WSL Terminal (Recommended)

### Step 1: Open WSL Terminal
- Press `Win + R`, type `wsl`, and press Enter
- OR open Windows Terminal and switch to WSL tab

### Step 2: Navigate to Project Directory
```bash
cd "/mnt/d/GIAIC/Quarter 4/Hackathon II"
```

### Step 3: Start Frontend Service Tunnel
```bash
~/.local/bin/minikube service teamflow-frontend -n teamflow
```

This will show a URL like: `http://127.0.0.1:34925`

**Keep this terminal open!** The tunnel must stay running.

### Step 4: Access Application
1. Open your browser
2. Go to the URL shown in the terminal
3. Navigate to `/login`

**Test Credentials:**
- Email: `admin@test.com`
- Password: `password123`

---

## Option 2: Using Windows PowerShell (With Alias)

### Step 1: Add Minikube to Windows PATH

#### Method A: Add to System PATH (Permanent)
1. Search for "Environment Variables" in Windows
2. Click "Edit the system environment variables"
3. Click "Environment Variables..."
4. Under "User variables", click "New"
5. Add:
   - Variable name: `MINIKUBE_HOME`
   - Variable value: `C:\Users\YOUR_USERNAME\.local\bin`
6. Edit `Path` variable and add: `%MINIKUBE_HOME%`
7. Restart PowerShell

#### Method B: Create PowerShell Alias (Current Session Only)
Run this in PowerShell:
```powershell
function minikube { & "/mnt/c/Users/YOUR_USERNAME/.local/bin/minikube.exe" $args }
function helm { & "/mnt/c/Users/YOUR_USERNAME/.local/bin/helm.exe" $args }
```

Replace `YOUR_USERNAME` with your actual Windows username (e.g., `owais_abdullah`)

### Step 2: Run Service Commands
```powershell
cd "D:\GIAIC\Quarter 4\Hackathon II"
minikube service teamflow-frontend -n teamflow
```

---

## Option 3: WSL Quick Commands (Create Alias)

### Step 1: Open WSL Terminal
```bash
# Navigate to project
cd "/mnt/d/GIAIC/Quarter 4/Hackathon II"

# Create convenience script
cat > run-frontend.sh << 'EOF'
#!/bin/bash
~/.local/bin/minikube service teamflow-frontend -n teamflow
EOF

chmod +x run-frontend.sh
```

### Step 2: Run Frontend
```bash
./run-frontend.sh
```

---

## Quick Reference Commands

### Check Kubernetes Status
```bash
# In WSL
~/.local/bin/kubectl get pods -n teamflow
~/.local/bin/kubectl get services -n teamflow

# Check backend logs
~/.local/bin/kubectl logs -f deployment/teamflow-backend -n teamflow

# Check frontend logs
~/.local/bin/kubectl logs -f deployment/teamflow-frontend -n teamflow
```

### Restart Services
```bash
# Restart frontend
~/.local/bin/kubectl rollout restart deployment teamflow-frontend -n teamflow

# Restart backend
~/.local/bin/kubectl rollout restart deployment/teamflow-backend -n teamflow
```

### Scale Replicas
```bash
~/.local/bin/kubectl scale deployment teamflow-frontend -n teamflow --replicas=3
~/.local/bin/kubectl scale deployment teamflow-backend -n teamflow --replicas=3
```

### Minikube Management
```bash
# Start Minikube (if stopped)
~/.local/bin/minikube start

# Stop Minikube (when done)
~/.local/bin/minikube stop

# Check Minikube status
~/.local/bin/minikube status
```

---

## Troubleshooting

### Issue: "minikube command not found"
**Solution:** Use the full path: `~/.local/bin/minikube` (in WSL) or add to PATH

### Issue: "Service tunnel not accessible"
**Solution:** The tunnel URL changes when Minikube restarts. Run the service command again for the new URL.

### Issue: "Login not working"
**Solution:**
1. Check backend is running: `~/.local/bin/kubectl get pods -n teamflow`
2. Check backend logs: `~/.local/bin/kubectl logs -f deployment/teamflow-backend -n teamflow`
3. Make sure you're accessing through the Minikube service tunnel, not localhost:3000

### Issue: "Frontend showing old code"
**Solution:** Restart frontend deployment:
```bash
~/.local/bin/kubectl rollout restart deployment teamflow-frontend -n teamflow
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Your Browser                              │
└──────────────────────┬──────────────────────────────────────┘
                       │ http://127.0.0.1:34925/
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  Minikube Service Tunnel → Frontend Pod (Next.js)          │
└──────────────────────────┬────────────────────────────────┘
                           │ /api/v1/*
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Next.js API Route: /api/[...path]/route.ts                │
│  → Proxies to: http://teamflow-backend.teamflow.svc.cluster.local:8000
└──────────────────────────┬────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Backend Pod (FastAPI)                                       │
│  → Database: Neon PostgreSQL (external)                     │
└─────────────────────────────────────────────────────────────┘
```

---

## Database Connection

**Using:** Neon PostgreSQL (External)
```
Connection String: postgresql://neondb_owner:***@ep-shiny-hall-a1mjei2a-pooler.ap-southeast-1.aws.neon.tech/neondb
```

**Migrations:** ✅ Already run (tables created)

---

## Project Structure

```
Hackathon II/
├── helm/teamflow/              # Kubernetes Helm charts
├── teamflow-web/
│   ├── frontend/               # Next.js application
│   │   ├── src/app/api/[...path]/route.ts  # API proxy
│   └── backend/                # FastAPI application
└── Kubernetes-SETUP.md         # This file
```

---

## Common Commands Summary

```bash
# In WSL Terminal from project root:

# 1. Start frontend service (keep terminal open)
~/.local/bin/minikube service teamflow-frontend -n teamflow

# 2. Check all pods
~/.local/bin/kubectl get pods -n teamflow

# 3. View logs
~/.local/bin/kubectl logs -f deployment/teamflow-backend -n teamflow
~/.local/bin/kubectl logs -f deployment/teamflow-frontend -n teamflow

# 4. Restart deployments
~/.local/bin/kubectl rollout restart deployment teamflow-frontend -n teamflow
~/.local/bin/kubectl rollout restart deployment/teamflow-backend -n teamflow

# 5. Scale up/down
~/.local/bin/kubectl scale deployment teamflow-backend -n teamflow --replicas=3
```

---

## Need Help?

1. Check Minikube is running: `~/.local/bin/minikube status`
2. Check pods are ready: `~/.local/bin/kubectl get pods -n teamflow`
3. Check for errors: `~/.local/bin/kubectl logs deployment/teamflow-backend -n teamflow --tail=50`

---

**Last Updated:** January 19, 2026
**Environment:** WSL2 + Docker Desktop + Minikube
