# TeamFlow Deployment Checklist

Use this checklist to ensure a successful deployment. Print this out and check off each item.

## Pre-Deployment Checklist

### Prerequisites
- [ ] GitHub account created
- [ ] Vercel account created (free tier)
- [ ] HuggingFace account created
- [ ] Neon database account created
- [ ] Git installed locally
- [ ] Node.js 20+ installed
- [ ] Python 3.13+ installed
- [ ] Vercel CLI installed (`npm install -g vercel`)

### Code Preparation
- [ ] All changes committed to git
- [ ] Branch `002-fullstack-web-crm` is up to date
- [ ] Frontend builds locally (`npm run build`)
- [ ] Backend starts locally (`uvicorn app.main:app`)
- [ ] Tests pass locally (`pytest` in backend)

---

## Backend Deployment Checklist

### Step 1: Database Setup (Neon)
- [ ] Logged into [Neon Console](https://console.neon.tech)
- [ ] Created a new project
- [ ] Copied connection string
- [ ] Connection string format: `postgresql://...?sslmode=require`
- [ ] Saved connection string securely

### Step 2: HuggingFace Space Creation
- [ ] Navigated to [HuggingFace Spaces](https://huggingface.co/spaces)
- [ ] Clicked "Create new Space"
- [ ] Set Space name: `teamflow-backend` (or preferred)
- [ ] Selected **Docker** SDK
- [ ] Selected **CPU basic** hardware
- [ ] Set visibility (Public/Private)
- [ ] Clicked "Create Space"
- [ ] Space URL available: `https://YOUR_USERNAME-teamflow-backend.hf.space`

### Step 3: Backend Code Deployment
- [ ] Cloned HuggingFace Space locally
- [ ] Copied `Dockerfile` to Space
- [ ] Copied `README.md` (with YAML frontmatter) to Space
- [ ] Copied `pyproject.toml` to Space
- [ ] Copied `app/` directory to Space
- [ ] Copied `alembic/` directory to Space (if using migrations)
- [ ] Committed changes: `git add . && git commit -m "Initial deploy"`
- [ ] Pushed to HuggingFace: `git push origin main`
- [ ] Build started in HuggingFace interface

### Step 4: Backend Environment Variables
- [ ] Navigated to Space > Settings > Variables
- [ ] Added `DATABASE_URL` (Neon connection string)
- [ ] Generated `SECRET_KEY`: `openssl rand -hex 32`
- [ ] Added `SECRET_KEY` (64-character hex string)
- [ ] Added `ENVIRONMENT` = `production`
- [ ] Clicked "Save"
- [ ] Space rebuilding with new variables

### Step 5: Backend Verification
- [ ] Waited for build to complete (2-5 minutes)
- [ ] Checked logs for errors
- [ ] Tested health endpoint: `curl /health`
- [ ] Expected response: `{"status":"healthy","service":"teamflow-backend"}`
- [ ] Accessed API docs: `/docs`
- [ ] Tested ReDoc: `/redoc`
- [ ] No errors in logs
- [ ] Backend deployed successfully

---

## Frontend Deployment Checklist

### Step 1: Vercel Project Setup
- [ ] Logged into [Vercel Dashboard](https://vercel.com/dashboard)
- [ ] Installed Vercel CLI: `npm install -g vercel`
- [ ] Logged into Vercel CLI: `vercel login`
- [ ] Navigated to `teamflow-web/frontend`
- [ ] Ran `vercel link` to connect project
- [ ] Noted `orgId` from `.vercel/project.json`
- [ ] Noted `projectId` from `.vercel/project.json`

### Step 2: Frontend Deployment
- [ ] Built frontend locally: `npm run build`
- [ ] Build successful without errors
- [ ] Deployed to Vercel: `vercel`
- [ ] Noted deployment URL
- [ ] Deployed to production: `vercel --prod`
- [ ] Frontend accessible at Vercel URL

### Step 3: Frontend Environment Variables
- [ ] Navigated to Vercel Dashboard > Project > Settings
- [ ] Selected "Environment Variables"
- [ ] Added `NEXT_PUBLIC_API_URL`
- [ ] Value: `https://YOUR_USERNAME-teamflow-backend.hf.space`
- [ ] Selected "Production" environment
- [ ] Clicked "Save"
- [ ] Triggered redeployment from Vercel Dashboard
- [ ] New deployment with environment variables successful

### Step 4: CORS Configuration
- [ ] Returned to HuggingFace Space Settings
- [ ] Added/updated `FRONTEND_URL` variable
- [ ] Value: Vercel deployment URL
- [ ] Clicked "Save"
- [ ] Space rebuilding with CORS configuration
- [ ] Waited for rebuild to complete

### Step 5: Frontend Verification
- [ ] Opened Vercel deployment URL
- [ ] Page loaded without errors
- [ ] Checked browser console (F12)
- [ ] No console errors
- [ ] Opened Network tab
- [ ] API calls visible in Network tab
- [ ] API calls return 200 status
- [ ] Frontend deployed successfully

---

## Integration Testing Checklist

### Authentication Flow
- [ ] Navigate to frontend
- [ ] Click "Sign Up" or "Register"
- [ ] Fill in user details
- [ ] Submit registration form
- [ ] Receive success message
- [ ] Redirected to login/dashboard
- [ ] Login with created credentials
- [ ] Successfully authenticated
- [ ] See user dashboard

### Core Features
- [ ] Create a new project
- [ ] Project appears in list
- [ ] Create a new task
- [ ] Task appears in task board
- [ ] Edit task details
- [ ] Changes saved successfully
- [ ] Delete task
- [ ] Task removed from list
- [ ] View analytics/dashboard
- [ ] Data loads correctly

### API Endpoints
- [ ] GET `/api/v1/projects` works
- [ ] POST `/api/v1/projects` works
- [ ] GET `/api/v1/tasks` works
- [ ] POST `/api/v1/tasks` works
- [ ] Auth endpoints work
- [ ] All responses return JSON
- [ ] No 500 errors

---

## CI/CD Setup Checklist (Optional)

### GitHub Secrets Configuration
- [ ] Generated Vercel token from [Vercel Tokens](https://vercel.com/account/tokens)
- [ ] Copied `VERCEL_TOKEN`
- [ ] Copied `VERCEL_ORG_ID` from `.vercel/project.json`
- [ ] Copied `VERCEL_PROJECT_ID` from `.vercel/project.json`
- [ ] Generated HuggingFace token from [HF Tokens](https://huggingface.co/settings/tokens)
- [ ] Token has **Write** permissions
- [ ] Copied `HF_TOKEN` (starts with `hf_`)
- [ ] Noted `HF_SPACE_NAME` = `YOUR_USERNAME/teamflow-backend`
- [ ] Copied `BACKEND_API_URL`
- [ ] Navigated to GitHub repo > Settings > Secrets
- [ ] Added all 6 secrets to GitHub
- [ ] Secret names match exactly

### GitHub Actions Workflow
- [ ] Verified `.github/workflows/deploy.yml` exists
- [ ] Workflow file has correct syntax
- [ ] Pushed to `002-fullstack-web-crm` branch
- [ ] Workflow triggered automatically
- [ ] Checked Actions tab in GitHub
- [ ] Frontend deployment job successful
- [ ] Backend deployment job successful
- [ ] Both services live and accessible

---

## Post-Deployment Checklist

### Monitoring Setup
- [ ] Bookmarked Vercel Dashboard
- [ ] Bookmarked HuggingFace Space page
- [ ] Bookmarked Neon Console
- [ ] Enabled Vercel Analytics (if desired)
- [ ] Set up error tracking (if desired)
- [ ] Configured log aggregation (if desired)

### Documentation
- [ ] Saved all deployment URLs
- [ ] Documented all credentials securely
- [ ] Noted all environment variables
- [ ] Saved rollback procedures
- [ ] Documented any custom configurations

### Security Review
- [ ] Changed default passwords
- [ ] Rotated temporary tokens
- [ ] Verified HTTPS enabled everywhere
- [ ] Checked CORS configuration
- [ ] Verified database SSL mode
- [ ] Reviewed API security headers
- [ ] Enabled rate limiting (if available)

### Backup Strategy
- [ ] Database backups enabled (Neon auto-backups)
- [ ] Code pushed to GitHub
- [ ] Environment variables documented
- [ ] Rollback procedure tested

---

## Troubleshooting Verification

### Common Issues Check
- [ ] No CORS errors in browser console
- [ ] No 404 errors on API calls
- [ ] No 500 errors on backend
- [ ] Database connection stable
- [ ] No memory issues (check HuggingFace logs)
- [ ] Build times reasonable (< 10 minutes)
- [ ] Page load times acceptable (< 5 seconds)

### Performance Check
- [ ] Backend responds in < 1 second
- [ ] Frontend loads in < 3 seconds
- [ ] API endpoints respond quickly
- [ ] No memory leaks
- [ ] Database queries optimized

---

## Final Verification

### Automated Script
- [ ] Run verification script:
    ```bash
    BACKEND_URL=https://YOUR_BACKEND_URL \
    FRONTEND_URL=https://YOUR_FRONTEND_URL \
    ./scripts/verify-deployment.sh
    ```
- [ ] All checks pass
- [ ] No warnings
- [ ] No failures

### Manual Smoke Test
- [ ] Open incognito browser window
- [ ] Navigate to frontend
- [ ] Register new user
- [ ] Login successfully
- [ ] Create sample project
- [ ] Create sample task
- [ ] View dashboard
- [ ] Logout successfully
- [ ] All features work as expected

---

## Sign-Off

### Deployment Team
- [ ] Developer signature: ________________ Date: ________
- [ ] QA verification: ________________ Date: ________
- [ ] Project lead approval: ________________ Date: ________

### Deployment Details
- **Backend URL**: _________________________________________
- **Frontend URL**: _________________________________________
- **API Docs URL**: _________________________________________
- **Database**: Neon PostgreSQL (Free tier)
- **Deployment Date**: _____________________________________
- **Branch**: `002-fullstack-web-crm`
- **Commit SHA**: _________________________________________

---

## Notes and Issues

Document any issues encountered during deployment:

1. _______________________________________________________
2. _______________________________________________________
3. _______________________________________________________

Workarounds implemented:
1. _______________________________________________________
2. _______________________________________________________
3. _______________________________________________________

---

## Success Criteria

Deployment is considered successful when:

- [x] Backend health endpoint returns `{"status":"healthy"}`
- [x] API documentation accessible at `/docs`
- [x] Frontend loads without console errors
- [x] All API calls return 200 status
- [x] User can register and login
- [x] Core features (projects, tasks) work correctly
- [x] Verification script passes all checks
- [x] No critical errors in logs

---

**Deployment Status**: ⬜ In Progress | ⬜ Completed | ⬜ Failed

**Next Steps After Success**:
- Monitor for 24 hours
- Collect user feedback
- Plan next iteration
- Document lessons learned

---

**Quick Reference**:
- Deployment Guide: [DEPLOYMENT.md](./DEPLOYMENT.md)
- Quick Start: [DEPLOYMENT_SUMMARY.md](./DEPLOYMENT_SUMMARY.md)
- Environment Variables: [ENVIRONMENT_VARIABLES.md](./ENVIRONMENT_VARIABLES.md)
- Backend README: [teamflow-web/backend/README.md](./teamflow-web/backend/README.md)
