# TeamFlow Deployment Guide

Complete deployment guide for TeamFlow fullstack CRM application to Vercel (frontend) and HuggingFace Spaces (backend).

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Part 1: Backend Deployment (HuggingFace Spaces)](#part-1-backend-deployment-huggingface-spaces)
- [Part 2: Frontend Deployment (Vercel)](#part-2-frontend-deployment-vercel)
- [Part 3: GitHub Actions CI/CD](#part-3-github-actions-cicd)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

## Overview

**Architecture:**
- **Frontend**: Next.js 16 deployed on Vercel
- **Backend**: FastAPI deployed on HuggingFace Spaces
- **Database**: Neon PostgreSQL (free tier)
- **CI/CD**: GitHub Actions for automated deployments

**Deployment Flow:**
```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   GitHub    │ ──────> │  Vercel     │ ──────> │  Frontend   │
│  Repository │         │  (Frontend)  │         │  (Next.js)  │
│   (Push)    │         └──────────────┘         └─────────────┘
└─────────────┘                 ▲
      │                         │
      │                         │
      ▼                         │
┌─────────────┐         ┌──────────────┐
│  GitHub     │ ──────> │ HuggingFace │
│  Actions    │         │   Spaces     │
│  (CI/CD)    │         │   (Backend)  │
└─────────────┘         └──────────────┘
                                 │
                                 ▼
                          ┌─────────────┐
                          │    Neon     │
                          │ PostgreSQL  │
                          └─────────────┘
```

**Key Benefits of Automated CI/CD:**
- ✅ No manual cloning or pushing to HuggingFace
- ✅ Consistent deployments across environments
- ✅ Automatic health checks after deployment
- ✅ Single git push deploys both frontend and backend

## Prerequisites

### Accounts Required
- [GitHub Account](https://github.com/signup)
- [Vercel Account](https://vercel.com/signup)
- [HuggingFace Account](https://huggingface.co/join)
- [Neon Database Account](https://neon.tech/signup) (free)

### Tools Required
```bash
# Git
git --version

# Node.js 20+
node --version

# Python 3.13+
python --version

# Vercel CLI
npm install -g vercel
```

## Part 1: Backend Deployment (HuggingFace Spaces)

### Step 1: Create Neon PostgreSQL Database

1. Go to [Neon Console](https://console.neon.tech)
2. Create a new project
3. Copy your connection string (looks like: `postgresql://user:pass@ep-xyz.aws.neon.tech/teamflow?sslmode=require`)
4. Save it for later use

### Step 2: Create HuggingFace Space

1. Go to [HuggingFace Spaces](https://huggingface.co/spaces)
2. Click "Create new Space"
3. Configure:
   - **Owner**: Your username
   - **Space name**: `teamflow-backend` (or your preferred name)
   - **SDK**: Docker
   - **Hardware**: CPU basic (free)
   - **Visibility**: Public (or Private)
4. Click "Create Space"

### Step 3: Deploy Backend to HuggingFace

**Recommended: GitHub Actions (Automatic)**

After configuring GitHub Actions (see Part 3 below), the backend will be deployed automatically when you push to the `002-fullstack-web-crm` branch. No manual steps needed!

**Manual Deployment (Fallback Only)**

If GitHub Actions is not configured, you can deploy manually:

**Option A: Using Git**

```bash
# Clone your HuggingFace Space
git clone https://huggingface.co/spaces/YOUR_USERNAME/teamflow-backend
cd teamflow-backend

# Copy backend files
cp -r /path/to/teamflow-web/backend/* .

# Commit and push
git add .
git commit -m "Initial backend deployment"
git push
```

**Option B: Using Web Interface**

1. Go to your Space on HuggingFace
2. Click "Files" > "Upload files"
3. Upload these files from `teamflow-web/backend/`:
   - `Dockerfile`
   - `README.md` (with YAML frontmatter)
   - `pyproject.toml`
   - `app/` directory (entire folder)
   - `alembic/` directory (if using migrations)

> **Note**: For production use, configure GitHub Actions for automatic deployments. This eliminates the need for manual cloning and pushing.

### Step 4: Configure Environment Variables

In your HuggingFace Space:

1. Go to **Settings** > **Variables**
2. Add these secrets:

| Variable | Value | Required |
|----------|-------|----------|
| `DATABASE_URL` | Your Neon connection string | Yes |
| `SECRET_KEY` | Generate with: `openssl rand -hex 32` | Yes |
| `ENVIRONMENT` | `production` | No |
| `FRONTEND_URL` | Your Vercel URL (later) | No |

3. Click "Save"

### Step 5: Verify Backend Deployment

1. Wait for the Space to build (2-5 minutes)
2. Check the logs for any errors
3. Test endpoints:
   ```bash
   # Health check
   curl https://YOUR_USERNAME-teamflow-backend.hf.space/health

   # API Documentation
   # Open in browser: https://YOUR_USERNAME-teamflow-backend.hf.space/docs
   ```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "teamflow-backend"
}
```

### Step 6: Generate HuggingFace Token (CRITICAL for Auto-Deploy)

> ⚠️ **IMPORTANT**: This token is required for GitHub Actions to automatically deploy your backend to HuggingFace Spaces. You must add it to GitHub Secrets (see Part 3, Step 1).

1. Go to [HuggingFace Settings > Tokens](https://huggingface.co/settings/tokens)
2. Click **"New token"**
3. Configure:
   - **Type**: **Write** (required - Read permissions won't work!)
   - **Name**: `GitHub Actions` (or any descriptive name)
4. Click **"Generate token"**
5. **Copy the token immediately** (starts with `hf_`)
   - ⚠️ You won't be able to see it again after leaving the page
   - Save it securely - you'll add it to GitHub Secrets next

> **Why Write permissions?** GitHub Actions needs to push code changes to your HuggingFace Space repository. Read-only permissions will cause the deployment to fail.

## Part 2: Frontend Deployment (Vercel)

### Step 1: Install Vercel CLI

```bash
npm install -g vercel
```

### Step 2: Deploy Frontend

From the `teamflow-web/frontend` directory:

```bash
cd teamflow-web/frontend

# Login to Vercel
vercel login

# Deploy (follow prompts)
vercel

# Production deployment
vercel --prod
```

### Step 3: Configure Environment Variables in Vercel

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Select your project
3. Go to **Settings** > **Environment Variables**
4. Add:

| Variable | Value | Environment |
|----------|-------|-------------|
| `NEXT_PUBLIC_API_URL` | `https://YOUR_USERNAME-teamflow-backend.hf.space` | Production |

5. Click **Save**
6. **Redeploy** your application (variables only apply on new deployments)

### Step 4: Update CORS in Backend

Go back to your HuggingFace Space settings and update `FRONTEND_URL`:

```
FRONTEND_URL=https://your-project.vercel.app
```

Or add it to the list:
```
FRONTEND_URL=https://your-project.vercel.app,https://localhost:3000
```

### Step 5: Verify Frontend Deployment

1. Open your Vercel URL
2. Check browser console for errors
3. Test API calls in Network tab
4. Verify authentication flow works

## Part 3: GitHub Actions CI/CD

### Step 1: Configure GitHub Secrets (CRITICAL STEP)

> 🔐 **All 6 secrets are required** for automated CI/CD to work. Without these, the GitHub Actions workflow will fail.

Go to your GitHub repository > **Settings** > **Secrets and variables** > **Actions**

Click **"New repository secret"** for each of the following:

| Secret Name | Value | How to Get | Importance |
|-------------|-------|------------|------------|
| `HF_TOKEN` | Your HuggingFace token (from Part 1, Step 6) | Starts with `hf_` | **CRITICAL** - Required to push code to HF Space |
| `VERCEL_TOKEN` | Your Vercel token | Vercel Dashboard > Settings > Tokens | Required for Vercel deployment |
| `VERCEL_ORG_ID` | Your Vercel org ID | `vercel link` or `.vercel/project.json` | Required for Vercel deployment |
| `VERCEL_PROJECT_ID` | Your Vercel project ID | `vercel link` or `.vercel/project.json` | Required for Vercel deployment |
| `HF_SPACE_NAME` | `YOUR_USERNAME/teamflow-backend` | Your HF Space name (from Part 1, Step 2) | Required to identify target Space |
| `BACKEND_API_URL` | `https://YOUR_USERNAME-teamflow-backend.hf.space` | Your HF Space URL | Used for health verification |

**Detailed Steps:**

1. Click **"New repository secret"**
2. **Name**: Enter the secret name (e.g., `HF_TOKEN`)
3. **Value**: Paste the token value
4. Click **"Add secret"**
5. Repeat for all 6 secrets

> ⚠️ **Common Mistake**: Forgetting to add `HF_TOKEN` or using Read permissions instead of Write. This will cause the workflow to fail with "permission denied" errors.

### Step 2: Link Vercel Project

```bash
cd teamflow-web/frontend

# Link project to get IDs
vercel link

# This creates .vercel/project.json with:
# - orgId
# - projectId
```

Copy these values to GitHub secrets.

### Step 3: Verify CI/CD Workflow

1. Push to `002-fullstack-web-crm` branch
2. Go to **Actions** tab in GitHub
3. Watch the workflow run
4. Check deployment status

## Verification

### Backend Checklist

- [ ] HuggingFace Space is running
- [ ] Health endpoint returns 200: `/health`
- [ ] API docs accessible: `/docs`
- [ ] Database connection works
- [ ] CORS allows frontend URL

### Frontend Checklist

- [ ] Vercel deployment successful
- [ ] Environment variables set correctly
- [ ] API calls work (check Network tab)
- [ ] Authentication flow works
- [ ] No console errors

### Integration Tests

```bash
# Test backend health
curl https://YOUR_USERNAME-teamflow-backend.hf.space/health

# Test API endpoint
curl https://YOUR_USERNAME-teamflow-backend.hf.space/api/v1/health

# Test frontend
open https://your-project.vercel.app
```

## Troubleshooting

### Backend Issues

**Issue: "Missing configuration in README"**
- **Fix**: Ensure `README.md` has YAML frontmatter at the TOP

**Issue: "OSError: Readme file does not exist"**
- **Fix**: Ensure `Dockerfile` copies `README.md` before `pip install -e .`

**Issue: "ModuleNotFoundError"**
- **Fix**: Check all import paths use `app.` prefix (e.g., `from app.core.config import settings`)

**Issue: "Database connection failed"**
- **Fix**: Verify `DATABASE_URL` format and SSL mode: `?sslmode=require`

**Issue: "CORS errors"**
- **Fix**: Add your Vercel URL to `FRONTEND_URL` in HF Space settings

### Frontend Issues

**Issue: "API calls failing"**
- **Fix**: Check `NEXT_PUBLIC_API_URL` is set correctly in Vercel environment variables

**Issue: "Build errors"**
- **Fix**: Ensure all dependencies in `package.json` are compatible with Next.js 16

**Issue: "Environment variables undefined"**
- **Fix**: Redeploy after adding variables (Vercel requires rebuild)

### CI/CD Issues

**Issue: "VERCEL_TOKEN not provided"**
- **Fix**: Verify secret name matches exactly: `VERCEL_TOKEN`

**Issue: "HF_TOKEN invalid"**
- **Fix**: Ensure token has **Write** permissions

**Issue: "Space not found"**
- **Fix**: Verify `HF_SPACE_NAME` format: `username/space-name`

### Database Issues

**Issue: "Connection closed" errors**
- **Fix**: Add `pool_pre_ping=True` to database engine configuration

**Issue: "SSL required"**
- **Fix**: Ensure `DATABASE_URL` includes `?sslmode=require`

## Post-Deployment

### Monitoring

- **Backend**: Check HuggingFace Space logs
- **Frontend**: Check Vercel Analytics
- **Database**: Monitor Neon console
- **CI/CD**: Check GitHub Actions workflow runs

### Updates

**Automatic Updates (Recommended)**

With GitHub Actions configured, both services update automatically:

```bash
# Make changes to code
git add .
git commit -m "Your commit message"
git push origin 002-fullstack-web-crm

# GitHub Actions will:
# 1. Build and deploy frontend to Vercel
# 2. Deploy backend to HuggingFace Spaces
# 3. Verify deployment health
```

**Manual Updates (Fallback)**

If GitHub Actions fails or you need immediate deployment:

```bash
# Frontend
cd teamflow-web/frontend
vercel --prod

# Backend (see manual deployment steps above)
```

### How Automatic Deployment Works

```
┌─────────────────────────────────────────────────────────┐
│                     Push Code                           │
│                    (git push)                           │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│              GitHub Actions Triggered                   │
│         (on push to 002-fullstack-web-crm)             │
└─────────────────────────┬───────────────────────────────┘
                          │
          ┌───────────────┴───────────────┐
          ▼                               ▼
┌─────────────────────┐         ┌─────────────────────┐
│   Frontend Job      │         │   Backend Job       │
│  - Install deps     │         │  - Clone HF Space   │
│  - Build Next.js    │         │  - Copy backend     │
│  - Deploy to Vercel │         │  - Push to HF       │
└─────────────────────┘         └─────────────────────┘
          │                               │
          ▼                               ▼
┌─────────────────────┐         ┌─────────────────────┐
│  Frontend Live      │         │  Backend Live       │
│  (Vercel)           │         │  (HuggingFace)      │
└─────────────────────┘         └─────────────────────┘
```

### Rollback

**Backend:**
```bash
git revert <commit-hash>
git push
```

**Frontend:**
```bash
vercel rollback
```

## Support

For issues:
1. Check logs in HuggingFace Space
2. Check Vercel deployment logs
3. Review GitHub Actions workflow runs
4. Verify environment variables are set correctly

## URLs Summary

After successful deployment:

| Service | URL |
|---------|-----|
| **Frontend** | `https://your-project.vercel.app` |
| **Backend** | `https://YOUR_USERNAME-teamflow-backend.hf.space` |
| **API Docs** | `https://YOUR_USERNAME-teamflow-backend.hf.space/docs` |
| **Health Check** | `https://YOUR_USERNAME-teamflow-backend.hf.space/health` |
| **Database** | Neon Console |

---

**Congratulations!** Your TeamFlow CRM is now live on Vercel and HuggingFace Spaces. 🎉
