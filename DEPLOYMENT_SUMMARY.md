# TeamFlow Deployment - Quick Start Guide

This guide will help you deploy TeamFlow to production in under 30 minutes using **automated CI/CD via GitHub Actions**.

## What You'll Deploy

- **Frontend**: Next.js 16 application on Vercel
- **Backend**: FastAPI application on HuggingFace Spaces
- **Database**: Neon PostgreSQL (free tier)

## Prerequisites Checklist

Before starting, ensure you have:

- [ ] GitHub account
- [ ] Vercel account (free)
- [ ] HuggingFace account (free)
- [ ] Neon account (free database)

---

## Phase 1: Set up Infrastructure (15 minutes)

### Step 1: Set up Database (5 minutes)

1. Go to [Neon Console](https://console.neon.tech)
2. Click **"Create a project"**
3. Copy the connection string (looks like `postgresql://...`)
4. Save it somewhere safe

### Step 2: Create HuggingFace Space (5 minutes)

1. Go to [HuggingFace Spaces](https://huggingface.co/spaces)
2. Click **"Create new Space"**
3. Fill in:
   - **Name**: `teamflow-backend` (or your preferred name)
   - **License**: MIT
   - **SDK**: Docker
   - **Hardware**: CPU basic (free)
   - **Visibility**: Public (or Private if you prefer)
4. Click **"Create Space"**
5. **Note your Space name**: It will be `YOUR_USERNAME/teamflow-backend`

### Step 3: Configure HuggingFace Space Environment Variables (5 minutes)

1. Go to your new Space page
2. Click **"Settings"** > **"Variables"** (or "Repository secrets")
3. Add these variables:

```
DATABASE_URL = <your Neon connection string from Step 1>
SECRET_KEY = <run: openssl rand -hex 32>
ENVIRONMENT = production
```

4. Click **"Save"**

> **GitHub Actions will automatically deploy your backend code to this Space. No manual cloning or file uploading needed!**

---

## Phase 2: Set up Vercel Project (5 minutes)

### Step 1: Install Vercel CLI (1 minute)

```bash
npm install -g vercel
```

### Step 2: Link and Deploy Frontend (4 minutes)

```bash
cd teamflow-web/frontend

# Login to Vercel
vercel login

# Link project (creates .vercel/project.json)
vercel link

# When prompted:
# - Link to existing project? No
# - Project name: teamflow-frontend
# - Directory: ./ (current)
# - Override settings? No

# Deploy to production
vercel --prod
```

### Step 3: Configure Vercel Environment Variables

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Select your project
3. Go to **Settings** > **Environment Variables**
4. Add:

```
NEXT_PUBLIC_API_URL = https://YOUR_USERNAME-teamflow-backend.hf.space
```

5. Click **"Save"**
6. Go to **Deployments** > **"Redeploy"**

### Step 4: Update CORS in HuggingFace Space

1. Go back to your HuggingFace Space > **Settings** > **Variables**
2. Add or update:

```
FRONTEND_URL = https://your-project.vercel.app
```

3. Click **"Save"**

---

## Phase 3: Set up GitHub Actions CI/CD (5 minutes)

### Step 1: Get Vercel Credentials

```bash
cd teamflow-web/frontend
vercel link

cat .vercel/project.json
# Copy these values:
# - orgId
# - projectId
```

### Step 2: Get Vercel Token

1. Go to [Vercel Tokens](https://vercel.com/account/tokens)
2. Click **"Create Token"**
3. Name it: `GitHub Actions`
4. Copy the token

### Step 3: Get HuggingFace Token (IMPORTANT - Required for Auto-Deploy)

> ⚠️ **CRITICAL**: You must generate and save this token to enable automatic deployment to HuggingFace Spaces via GitHub Actions. Without this token, the workflow will fail with permission errors.

1. Go to [HF Tokens](https://huggingface.co/settings/tokens)
2. Click **"New token"**
3. Type: **Write** permissions (required for pushing code to your Space)
   - ❌ Do NOT use "Read" permissions - this won't work
   - ✅ Must be "Write" to allow GitHub Actions to push to your Space
4. Copy the token immediately (starts with `hf_`)
   - **Save it securely** - you won't be able to see it again!
   - You'll need to add it to GitHub Secrets in the next step

### Step 4: Add GitHub Secrets

> 🔐 **All 6 secrets are required** for automated CI/CD to work properly.

1. Go to your GitHub repository
2. Click **Settings** > **Secrets and variables** > **Actions**
3. Click **"New repository secret"** and add:

| Secret Name | Value |
|-------------|-------|
| `VERCEL_TOKEN` | Your Vercel token from Step 2 |
| `VERCEL_ORG_ID` | Your Vercel org ID |
| `VERCEL_PROJECT_ID` | Your Vercel project ID |
| `HF_TOKEN` | Your HuggingFace token (starts with `hf_`) |
| `HF_SPACE_NAME` | `YOUR_USERNAME/teamflow-backend` |
| `BACKEND_API_URL` | `https://YOUR_USERNAME-teamflow-backend.hf.space` |

4. Click **"Add secret"** for each one

### Step 5: Trigger Automated Deployment

```bash
# Push any change to trigger deployment
git add .
git commit -m "Configure CI/CD automation"
git push origin 002-fullstack-web-crm
```

### Step 6: Monitor Deployment

1. Go to **Actions** tab in your GitHub repository
2. Click on the "Deploy TeamFlow Fullstack Application" workflow run
3. Watch the progress:
   - **deploy-frontend**: Builds and deploys to Vercel
   - **deploy-backend**: Clones HF Space, copies files, triggers restart
   - The workflow will **automatically restart** the HuggingFace Space
   - Wait ~5-10 minutes for HuggingFace Space to rebuild

**Important**: GitHub Actions will automatically trigger a rebuild of your HuggingFace Space using the API. You should see the message "✅ Space restart triggered successfully!" in the workflow logs.

---

## Phase 4: Verification (5 minutes)

### Test Backend

```bash
# Health check
curl https://YOUR_USERNAME-teamflow-backend.hf.space/health

# Should return: {"status":"healthy","service":"teamflow-backend"}

# API docs
open https://YOUR_USERNAME-teamflow-backend.hf.space/docs
```

### Test Frontend

```bash
# Open your Vercel URL
open https://your-project.vercel.app

# Check:
# - Browser console for errors
# - Network tab for API calls
# - User registration/login works
```

### Run Verification Script

```bash
# From project root
BACKEND_URL=https://YOUR_USERNAME-teamflow-backend.hf.space \
FRONTEND_URL=https://your-project.vercel.app \
./scripts/verify-deployment.sh
```

---

## How CI/CD Works

Once configured, **GitHub Actions will automatically deploy** both frontend and backend on every push to the `002-fullstack-web-crm` branch:

1. **Frontend**: Built and deployed to Vercel
2. **Backend**: Files copied to HuggingFace Space and pushed via Git
3. **No manual intervention needed** after initial setup!

### Workflow Overview

```
Push to Branch
       ↓
GitHub Actions Triggered
       ↓
┌──────────────────────────────────────┐
│  Frontend Job                        │
│  - Install dependencies              │
│  - Build Next.js app                 │
│  - Deploy to Vercel                  │
└──────────────────────────────────────┘
       ↓
┌──────────────────────────────────────┐
│  Backend Job                         │
│  - Clone HuggingFace Space           │
│  - Copy backend files                │
│  - Commit and push to HF Space       │
│  - Wait for rebuild (5-10 min)       │
│  - Verify health endpoint            │
└──────────────────────────────────────┘
```

---

## Manual Deployment (Fallback Only)

If GitHub Actions fails, you can deploy manually:

### Manual Backend Deployment

```bash
# Clone your HuggingFace Space
git clone https://huggingface.co/spaces/YOUR_USERNAME/teamflow-backend
cd teamflow-backend

# Copy backend files
cp -r /path/to/teamflow-web/backend/* .

# Commit and push
git add .
git commit -m "Manual backend deployment"
git push
```

### Manual Frontend Deployment

```bash
cd teamflow-web/frontend
vercel --prod
```

---

## URLs Summary

After successful deployment:

| Service | URL Pattern | Example |
|---------|-------------|---------|
| **Frontend** | `https://your-project.vercel.app` | `https://teamflow-abc123.vercel.app` |
| **Backend** | `https://YOUR_USERNAME-teamflow-backend.hf.space` | `https://johndoe-teamflow-backend.hf.space` |
| **API Docs** | Backend + `/docs` | `https://johndoe-teamflow-backend.hf.space/docs` |
| **Health** | Backend + `/health` | `https://johndoe-teamflow-backend.hf.space/health` |

---

## Troubleshooting Quick Reference

| Issue | Solution |
|-------|----------|
| **Backend not building** | Check `Dockerfile` copies `README.md` before `pip install` |
| **CORS errors** | Add Vercel URL to `FRONTEND_URL` in backend env vars |
| **API calls failing** | Check `NEXT_PUBLIC_API_URL` in Vercel env vars |
| **Database errors** | Verify `DATABASE_URL` has `?sslmode=require` |
| **Build timeout** | HuggingFace Spaces may take 5-10 minutes on first build |
| **HF_TOKEN permission denied** | Ensure token has **Write** permissions |
| **GitHub Actions fails** | Check that all secrets are set correctly |
| **Repository not found** | Space doesn't exist or `HF_SPACE_NAME` is wrong (see below) |

### Common Error: "Repository not found" from HuggingFace

**Error Message:**
```
fatal: repository 'https://huggingface.co/spaces/' not found
```

**This means one of three things:**

1. **`HF_SPACE_NAME` secret is not set** (most common)
   - Go to: GitHub repo → Settings → Secrets and variables → Actions
   - Add secret: `HF_SPACE_NAME` = `YOUR_USERNAME/teamflow-backend`
   - Example: `MrOwaisAbdullah/teamflow-backend`

2. **Space doesn't exist on HuggingFace**
   - Visit: `https://huggingface.co/spaces/YOUR_USERNAME/teamflow-backend`
   - If 404, you need to create the space first (see Phase 1, Step 2)

3. **Space name format is incorrect**
   - Must be: `username/space-name` (with forward slash)
   - Wrong: `teamflow-backend` or `https://huggingface.co/spaces/...`
   - Right: `MrOwaisAbdullah/teamflow-backend`

**Quick Fix:**
```bash
# 1. Check if your space exists
open https://huggingface.co/spaces/YOUR_USERNAME/teamflow-backend

# 2. If it exists, get the correct name from the URL
# Format is: huggingface.co/spaces/USERNAME/SPACE_NAME

# 3. Set HF_SPACE_NAME in GitHub Secrets
# Value: USERNAME/SPACE_NAME (from step 2)
```

---

## Cost Summary

All services use **free tiers**:

- **Vercel**: Free (Hobby plan)
- **HuggingFace Spaces**: Free (CPU basic)
- **Neon PostgreSQL**: Free (0.5GB storage)
- **GitHub Actions**: Free (public repos)
- **Total**: $0/month

---

## Next Steps

1. **Test Core Features**:
   - User registration/login
   - Create tasks and projects
   - Time tracking
   - Analytics dashboard

2. **Monitor Performance**:
   - Check Vercel Analytics
   - Monitor HuggingFace Space logs
   - Review Neon database usage

3. **Set Up Alerts**:
   - Configure error tracking
   - Set up uptime monitoring
   - Enable database alerts

4. **Customize**:
   - Add custom domain
   - Configure email notifications
   - Set up backup strategies

---

## Support Documentation

- **Full Deployment Guide**: [DEPLOYMENT.md](./DEPLOYMENT.md)
- **Environment Variables**: [teamflow-web/backend/README.md](./teamflow-web/backend/README.md)
- **GitHub Actions Workflow**: [.github/workflows/deploy.yml](./.github/workflows/deploy.yml)

---

## Success Criteria

Your deployment is successful when:

- [ ] Backend health endpoint returns `{"status":"healthy"}`
- [ ] API documentation is accessible at `/docs`
- [ ] Frontend loads without console errors
- [ ] API calls show in Network tab (200 status)
- [ ] User can log in and create tasks
- [ ] GitHub Actions workflow completes successfully
- [ ] All verification script tests pass

---

**Estimated Total Time**: 25-30 minutes
**Difficulty**: Beginner-friendly
**Cost**: Free

🎉 **Congratulations!** Your TeamFlow CRM is now live with automated CI/CD!
