# TeamFlow Deployment Files

This directory contains all deployment configurations and documentation for the TeamFlow fullstack CRM application.

## Quick Start

**New to deployment?** Start here: [DEPLOYMENT_SUMMARY.md](./DEPLOYMENT_SUMMARY.md) (25-minute guide)

## Documentation Files

### 1. DEPLOYMENT_SUMMARY.md
**Quick start guide** for deploying TeamFlow in under 30 minutes.
- Prerequisites checklist
- Step-by-step deployment instructions
- Verification steps
- Troubleshooting quick reference

**Best for**: First-time deployment

---

### 2. DEPLOYMENT.md
**Comprehensive deployment guide** with detailed instructions.
- Platform-specific configurations
- Environment setup
- CI/CD automation
- Advanced troubleshooting
- Rollback procedures

**Best for**: Complete deployment understanding

---

### 3. DEPLOYMENT_CHECKLIST.md
**Printable checklist** to ensure nothing is missed.
- Pre-flight checks
- Backend deployment steps
- Frontend deployment steps
- Integration testing
- Post-deployment verification

**Best for**: Production deployments

---

### 4. ENVIRONMENT_VARIABLES.md
**Complete reference** for all environment variables.
- Backend variables (HuggingFace Spaces)
- Frontend variables (Vercel)
- GitHub Actions secrets
- Security best practices
- Troubleshooting

**Best for**: Configuration reference

---

## Configuration Files

### Backend Deployment (HuggingFace Spaces)

**Location**: `teamflow-web/backend/`

| File | Purpose |
|------|---------|
| `Dockerfile` | Container configuration for HuggingFace Spaces |
| `README.md` | Space configuration with YAML frontmatter |
| `.env.hf-template` | Environment variable template |
| `.dockerignore` | Files to exclude from Docker image |

**Key Files Modified**:
- `app/core/config.py` - Enhanced with CORS and HuggingFace detection

---

### Frontend Deployment (Vercel)

**Location**: `teamflow-web/frontend/`

| File | Purpose |
|------|---------|
| `vercel.json` | Vercel platform configuration |
| `.env.production` | Production environment variables |
| `.env.vercel-template` | Environment variable template |
| `next.config.ts` - Updated | Dynamic API URL configuration |

---

### CI/CD Automation (GitHub Actions)

**Location**: `.github/workflows/`

| File | Purpose |
|------|---------|
| `deploy.yml` | Automated deployment to Vercel + HuggingFace |

**Triggers**:
- Push to `002-fullstack-web-crm` branch
- Manual workflow dispatch

---

## Scripts

### deploy.sh
**Quick deployment script** for manual deployment.

```bash
# Deploy both frontend and backend
./scripts/deploy.sh all

# Deploy only backend
./scripts/deploy.sh backend

# Deploy only frontend (production)
./scripts/deploy.sh frontend --prod
```

**Requirements**:
- `HF_TOKEN` environment variable
- Vercel CLI installed and logged in

---

### verify-deployment.sh
**Automated verification script** to test deployment health.

```bash
BACKEND_URL=https://your-backend.hf.space \
FRONTEND_URL=https://your-app.vercel.app \
./scripts/verify-deployment.sh
```

**Tests**:
- Backend health endpoint
- API documentation
- Frontend accessibility
- CORS configuration
- Environment variables
- Database connection

---

## Deployment Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   GitHub    │ Push    │  GitHub      │ Deploy  │  Vercel     │
│  Repository │ ──────> │  Actions     │ ──────> │  (Frontend) │
└─────────────┘         └──────────────┘         └─────────────┘
                              │                         │
                              │ Deploy                  │
                              ▼                         │
                         ┌──────────────┐              │
                         │ HuggingFace  │ ─────────────┘
                         │   Spaces     │              │
                         │  (Backend)   │ ─────────────┤
                         └──────────────┘              │
                                │                       │
                                ▼                       │
                         ┌──────────────┐              │
                         │    Neon      │              │
                         │ PostgreSQL   │ <────────────┘
                         └──────────────┘
```

---

## Environment Variables Summary

### Backend (HuggingFace Spaces)
```bash
DATABASE_URL=postgresql://...
SECRET_KEY=64-char-hex-string
ENVIRONMENT=production
FRONTEND_URL=https://your-app.vercel.app
```

### Frontend (Vercel)
```bash
NEXT_PUBLIC_API_URL=https://your-backend.hf.space
```

### GitHub Actions (Secrets)
```bash
VERCEL_TOKEN=...
VERCEL_ORG_ID=...
VERCEL_PROJECT_ID=...
HF_TOKEN=hf_...
HF_SPACE_NAME=username/space-name
BACKEND_API_URL=https://your-backend.hf.space
```

---

## Deployment Methods

### Method 1: Manual Deployment (Recommended for First Time)

**Advantages**:
- Full control over each step
- Easier to troubleshoot
- Better understanding of process

**Time**: 25-30 minutes

**Guide**: [DEPLOYMENT_SUMMARY.md](./DEPLOYMENT_SUMMARY.md)

---

### Method 2: Script-Based Deployment

**Advantages**:
- Faster deployment
- Repeatable process
- Less manual work

**Time**: 10-15 minutes

**Command**:
```bash
./scripts/deploy.sh all
```

**Requirements**:
- Environment variables set
- Vercel CLI installed
- Git configured

---

### Method 3: CI/CD Automation (Recommended for Ongoing)

**Advantages**:
- Automatic deployments on push
- Consistent process
- Easy rollback

**Setup Time**: 10 minutes

**Guide**: [DEPLOYMENT.md](./DEPLOYMENT.md) (Part 3)

---

## Platform Links

### Required Services

| Service | Link | Cost |
|---------|------|------|
| **Vercel** | [vercel.com](https://vercel.com) | Free |
| **HuggingFace** | [huggingface.co](https://huggingface.co) | Free |
| **Neon** | [neon.tech](https://neon.tech) | Free |
| **GitHub** | [github.com](https://github.com) | Free |

---

## Verification Steps

After deployment, verify:

1. **Backend Health**:
   ```bash
   curl https://your-backend.hf.space/health
   ```

2. **API Documentation**:
   ```
   https://your-backend.hf.space/docs
   ```

3. **Frontend Loads**:
   ```
   https://your-app.vercel.app
   ```

4. **Run Verification Script**:
   ```bash
   ./scripts/verify-deployment.sh
   ```

---

## Troubleshooting

### Quick Fixes

| Issue | Solution |
|-------|----------|
| **Backend won't build** | Check `README.md` has YAML frontmatter |
| **CORS errors** | Add frontend URL to `FRONTEND_URL` |
| **API calls failing** | Check `NEXT_PUBLIC_API_URL` in Vercel |
| **Database errors** | Verify `DATABASE_URL` has `?sslmode=require` |

### Detailed Troubleshooting

See [DEPLOYMENT.md](./DEPLOYMENT.md#troubleshooting) for comprehensive troubleshooting guide.

---

## Cost Summary

All services use **free tiers**:

- **Vercel**: Free (Hobby plan)
  - Unlimited deployments
  - Automatic HTTPS
  - Global CDN

- **HuggingFace Spaces**: Free (CPU basic)
  - Docker support
  - Public or private spaces
  - Auto-scaling

- **Neon PostgreSQL**: Free (0.5GB)
  - Serverless Postgres
  - Auto-scaling
  - Daily backups

- **GitHub Actions**: Free (public repos)
  - CI/CD automation
  - Secret management
  - Workflow logs

**Total Monthly Cost**: $0.00

---

## Support Resources

### Documentation
- Deployment Summary: [DEPLOYMENT_SUMMARY.md](./DEPLOYMENT_SUMMARY.md)
- Full Guide: [DEPLOYMENT.md](./DEPLOYMENT.md)
- Checklist: [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md)
- Environment Variables: [ENVIRONMENT_VARIABLES.md](./ENVIRONMENT_VARIABLES.md)

### Platform Documentation
- [Vercel Docs](https://vercel.com/docs)
- [HuggingFace Spaces Docs](https://huggingface.co/docs/hub/spaces)
- [Neon Docs](https://neon.tech/docs)

### Community
- [Vercel Community](https://vercel.com/community)
- [HuggingFace Forums](https://discuss.huggingface.co)
- [Stack Overflow](https://stackoverflow.com)

---

## File Structure

```
.
├── DEPLOYMENT.md                          # Comprehensive guide
├── DEPLOYMENT_SUMMARY.md                  # Quick start
├── DEPLOYMENT_CHECKLIST.md                # Printable checklist
├── ENVIRONMENT_VARIABLES.md               # Variable reference
├── README_DEPLOYMENT.md                   # This file
├── .github/
│   └── workflows/
│       └── deploy.yml                     # CI/CD workflow
├── scripts/
│   ├── deploy.sh                          # Deployment script
│   └── verify-deployment.sh               # Verification script
└── teamflow-web/
    ├── frontend/
    │   ├── vercel.json                    # Vercel config
    │   ├── .env.production                # Production vars
    │   └── .env.vercel-template           # Variable template
    └── backend/
        ├── Dockerfile                     # Container config
        ├── README.md                      # Space config
        ├── .env.hf-template               # Variable template
        └── .dockerignore                  # Build exclusions
```

---

## Success Criteria

Deployment is successful when:

- [ ] Backend health endpoint returns `{"status":"healthy"}`
- [ ] API docs accessible at `/docs`
- [ ] Frontend loads without console errors
- [ ] API calls show 200 status in Network tab
- [ ] User can register and login
- [ ] Core features (projects, tasks) work
- [ ] Verification script passes all checks

---

## Next Steps

After successful deployment:

1. **Monitor for 24 hours**
   - Check Vercel Analytics
   - Monitor HuggingFace logs
   - Review database usage

2. **Gather Feedback**
   - Test with real users
   - Collect bug reports
   - Document feature requests

3. **Plan Iterations**
   - Prioritize bug fixes
   - Plan new features
   - Schedule updates

4. **Set Up Monitoring**
   - Error tracking (Sentry, etc.)
   - Uptime monitoring
   - Performance tracking

---

## Contributing

When updating deployment configurations:

1. Test locally first
2. Update documentation
3. Verify scripts work
4. Test on staging environment
5. Document changes

---

## License

Deployment configurations are part of the TeamFlow project.

See main project LICENSE file for details.

---

**Last Updated**: 2026-01-05
**Version**: 1.0.0
**Status**: Production Ready
