# TeamFlow Frontend - How to Run

## Overview
The frontend is a Next.js application deployed on Minikube Kubernetes cluster. It uses an API proxy to communicate with the backend.

---

## Prerequisites
- ✅ Minikube installed (at `~/.local/bin/minikube` in WSL)
- ✅ Frontend deployed on Minikube
- ✅ Docker Desktop running

---

## Method 1: Windows Batch File (Easiest)

### Steps:
1. **Double-click** `start-frontend.bat` in the project root
2. A terminal window will open
3. Wait for the URL to appear (e.g., `http://127.0.0.1:34925`)
4. **Keep the window open** - the service tunnel must stay running
5. Open your browser and navigate to the URL

### Stop the Service:
- Close the terminal window, OR
- Press `Ctrl+C` in the terminal

---

## Method 2: WSL Terminal

### Step 1: Open WSL
- Press `Win + R`
- Type `wsl` and press Enter

### Step 2: Navigate to Project
```bash
cd "/mnt/d/GIAIC/Quarter 4/Hackathon II"
```

### Step 3: Start Service Tunnel
```bash
~/.local/bin/minikube service teamflow-frontend -n teamflow
```

### Step 4: Access Application
- The terminal will show a URL like: `http://127.0.0.1:34925`
- Open this URL in your browser

---

## URL Changes
**Important:** The Minikube service tunnel URL **changes every time** you restart:
- Minikube restart
- Pod restart
- Computer restart

Always run the service command again to get the current URL.

---

## Browser Access
Once running, access:
- **Home Page:** `http://127.0.0.1:XXXXX/` (URL from terminal)
- **Login Page:** `http://127.0.0.1:XXXXX/login`
- **Dashboard:** `http://127.0.0.0.1:XXXXX/dashboard`

**Test Credentials:**
```
Email: admin@test.com
Password: password123
```

---

## How It Works (Technical Details)

```
Browser
  ↓
http://127.0.0.1:34925/api/v1/auth/login
  ↓
Minikube Service Tunnel (port forward)
  ↓
Frontend Pod (Next.js)
  ↓
API Route: /api/[...path]/route.ts
  ↓
Proxies to: http://teamflow-backend.teamflow.svc.cluster.local:8000/api/v1/auth/login
  ↓
Backend Pod (FastAPI)
  ↓
Returns JWT token + user data
  ↓
Browser receives login success
```

**Key Point:** The browser only sees `http://127.0.0.1:34925` - it doesn't need to know about Kubernetes!

---

## Troubleshooting

### Issue: "minikube command not found"
**Solution:** Use the full path: `~/.local/bin/minikube`

### Issue: "Service tunnel not accessible"
**Solution:**
1. Make sure Minikube is running: `~/.local/bin/minikube status`
2. Check frontend pods are ready: `~/.local/bin/kubectl get pods -n teamflow`
3. Try restarting the service command

### Issue: "Login not working"
**Solution:**
1. Check backend is running: `~/.local/bin/kubectl get pods -n teamflow`
2. Check frontend logs: `~/.local/bin/kubectl logs -f deployment/teamflow-frontend -n teamflow`
3. Check backend logs: `~/.local/bin/kubectl logs -f deployment/teamflow-backend -n teamflow`

### Issue: "Page not loading / shows old code"
**Solution:** Restart the frontend deployment:
```bash
~/.local/bin/kubectl rollout restart deployment teamflow-frontend -n teamflow
```
Wait 30 seconds and refresh the browser.

### Issue: "URL changed after restart"
**Solution:** Run the service command again to get the new URL.

---

## Common Commands

### Check Frontend Status
```bash
# Check pods
~/.local/bin/kubectl get pods -n teamflow -l app.kubernetes.io/component=frontend

# View logs
~/.local/bin/kubectl logs -f deployment/teamflow-frontend -n teamflow

# Check replica count
~/.local/bin/kubectl get deployment teamflow-frontend -n teamflow
```

### Scale Frontend
```bash
# Scale to 3 replicas
~/.local/bin/kubectl scale deployment teamflow-frontend -n teamflow --replicas=3

# Scale back to 1
~/.local/bin/kubectl scale deployment teamflow-frontend -n teamflow --replicas=1
```

### Restart Frontend
```bash
~/.local/bin/kubectl rollout restart deployment teamflow-frontend -n teamflow
```

---

## File Locations

- **Source Code:** `teamflow-web/frontend/`
- **API Proxy:** `teamflow-web/frontend/src/app/api/[...path]/route.ts`
- **Dockerfile:** `teamflow-web/frontend/Dockerfile`
- **Helm Chart:** `helm/teamflow/templates/frontend-deployment.yaml`

---

## Development Notes

### Making Changes to Frontend Code
1. Edit files in `teamflow-web/frontend/src/`
2. Rebuild Docker image:
   ```bash
   cd "/mnt/d/GIAIC/Quarter 4/Hackathon II"
   eval "$(minikube docker-env)"
   docker build -t teamflow/frontend:latest -f teamflow-web/frontend/Dockerfile teamflow-web/frontend/
   ```
3. Restart deployment:
   ```bash
   ~/.local/bin/kubectl rollout restart deployment teamflow-frontend -n teamflow
   ```

### Updating Next.js Environment Variables
1. Edit `helm/teamflow/values.yaml`
2. Upgrade Helm release:
   ```bash
   ~/.local/bin/helm upgrade teamflow "/mnt/d/GIAIC/Quarter 4/Hackathon II/helm/teamflow" --namespace teamflow
   ```
3. Restart deployment

---

## Summary

1. **Start:** Run `start-frontend.bat` OR use WSL command
2. **Access:** Open URL shown in terminal
3. **Login:** Use `admin@test.com` / `password123`
4. **Stop:** Close the terminal window

**Remember:** Keep the service tunnel terminal open while using the application!

---

**Last Updated:** January 19, 2026
**Environment:** WSL2 + Docker Desktop + Minikube
