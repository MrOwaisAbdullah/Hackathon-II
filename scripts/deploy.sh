#!/bin/bash

###############################################################################
# TeamFlow Quick Deployment Script
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}======================================"
echo "TeamFlow Deployment Script"
echo "======================================${NC}"
echo ""

# Check if we're in the right directory
if [ ! -f "DEPLOYMENT.md" ]; then
    echo -e "${RED}Error: Please run this script from the project root directory${NC}"
    exit 1
fi

# Parse arguments
DEPLOY_TARGET="${1:-all}"  # all, frontend, backend

echo "Deployment target: $DEPLOY_TARGET"
echo ""

###############################################################################
# Backend Deployment (HuggingFace Spaces)
###############################################################################

if [ "$DEPLOY_TARGET" = "all" ] || [ "$DEPLOY_TARGET" = "backend" ]; then
    echo -e "${BLUE}======================================"
    echo "Deploying Backend to HuggingFace Spaces"
    echo "======================================${NC}"
    echo ""

    # Check if HuggingFace CLI is installed
    if ! command -v huggingface-cli &> /dev/null; then
        echo -e "${YELLOW}Installing HuggingFace CLI...${NC}"
        pip install huggingface_hub
    fi

    # Check for HF_TOKEN
    if [ -z "$HF_TOKEN" ]; then
        echo -e "${RED}Error: HF_TOKEN environment variable not set${NC}"
        echo "Get your token from: https://huggingface.co/settings/tokens"
        echo "Then run: export HF_TOKEN=hf_..."
        exit 1
    fi

    # Check for HF_SPACE_NAME
    if [ -z "$HF_SPACE_NAME" ]; then
        echo -e "${RED}Error: HF_SPACE_NAME environment variable not set${NC}"
        echo "Format: export HF_SPACE_NAME=username/space-name"
        exit 1
    fi

    echo "Cloning HuggingFace Space..."
    # Clone to temporary directory
    TEMP_DIR=$(mktemp -d)
    git clone https://huggingface.co/spaces/$HF_SPACE_NAME "$TEMP_DIR"

    echo "Copying backend files..."
    rsync -av --exclude='.venv' --exclude='.venv_linux' --exclude='.pytest_cache' \
        --exclude='__pycache__' --exclude='*.pyc' --exclude='.git' \
        --exclude='.env' --exclude='node_modules' \
        --delete \
        teamflow-web/backend/ "$TEMP_DIR/"

    echo "Configuring git..."
    cd "$TEMP_DIR"
    git config user.email "deployment@teamflow.local"
    git config user.name "Deployment Script"

    echo "Committing changes..."
    git add .
    git diff --quiet && git diff --staged --quiet || git commit -m "Deploy from local - $(date)"

    echo "Pushing to HuggingFace..."
    git push origin main

    echo -e "${GREEN}✓ Backend deployment initiated!${NC}"
    echo "Monitor at: https://huggingface.co/spaces/$HF_SPACE_NAME"

    # Cleanup
    cd -
    rm -rf "$TEMP_DIR"

    echo ""
fi

###############################################################################
# Frontend Deployment (Vercel)
###############################################################################

if [ "$DEPLOY_TARGET" = "all" ] || [ "$DEPLOY_TARGET" = "frontend" ]; then
    echo -e "${BLUE}======================================"
    echo "Deploying Frontend to Vercel"
    echo "======================================${NC}"
    echo ""

    cd teamflow-web/frontend

    # Check if Vercel CLI is installed
    if ! command -v vercel &> /dev/null; then
        echo -e "${YELLOW}Installing Vercel CLI...${NC}"
        npm install -g vercel
    fi

    # Check if logged in
    if ! vercel whoami &> /dev/null; then
        echo "Please login to Vercel:"
        vercel login
    fi

    echo "Building frontend..."
    npm run build

    echo "Deploying to Vercel..."
    if [ "$DEPLOY_TARGET" = "frontend" ] || [ "$2" = "--prod" ]; then
        echo "Deploying to production..."
        vercel --prod
    else
        echo "Deploying to preview..."
        vercel
    fi

    cd -

    echo -e "${GREEN}✓ Frontend deployment complete!${NC}"
    echo ""
fi

###############################################################################
# Summary
###############################################################################

echo -e "${BLUE}======================================"
echo "Deployment Summary"
echo "======================================${NC}"
echo ""
echo "Next Steps:"
echo ""
echo "1. Wait for backend to build (2-5 minutes)"
echo "   Monitor: https://huggingface.co/spaces/$HF_SPACE_NAME"
echo ""
echo "2. Update environment variables:"
echo "   - HuggingFace: Set DATABASE_URL and SECRET_KEY"
echo "   - Vercel: Set NEXT_PUBLIC_API_URL"
echo ""
echo "3. Verify deployment:"
echo "   ./scripts/verify-deployment.sh"
echo ""
echo "4. Test the application:"
echo "   - Backend Health: https://\$SPACE_NAME.hf.space/health"
echo "   - API Docs: https://\$SPACE_NAME.hf.space/docs"
echo "   - Frontend: Check Vercel deployment URL"
echo ""
echo -e "${GREEN}Deployment initiated successfully!${NC}"
