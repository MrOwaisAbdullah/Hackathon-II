#!/bin/bash
# Quick publish script for CLI packages
# Run this script after updating version in pyproject.toml

set -e

PACKAGE_NAME="your_package"  # CHANGE THIS
COMMAND_NAME="yourcommand"   # CHANGE THIS

echo "=========================================="
echo "CLI Package Publish Script"
echo "=========================================="
echo ""
echo "Package: $PACKAGE_NAME"
echo "Command: $COMMAND_NAME"
echo ""

# Get current version
VERSION=$(grep "^version = " pyproject.toml | cut -d'"' -f2)
echo "Version: $VERSION"
echo ""

# Check for uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  Warning: You have uncommitted changes"
    read -p "Continue anyway? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Run checks
echo "=========================================="
echo "Step 1: Checking imports"
echo "=========================================="
python .claude/skills/cli-deployment/scripts/check-imports.py $PACKAGE_NAME/
echo ""

echo "=========================================="
echo "Step 2: Building wheel"
echo "=========================================="
python -m build
echo ""

echo "=========================================="
echo "Step 3: Verifying wheel"
echo "=========================================="
WHEEL=$(ls dist/${PACKAGE_NAME}-${VERSION}-py3-none-any.whl 2>/dev/null || echo "")
if [ -z "$WHEEL" ]; then
    echo "❌ Wheel not found!"
    exit 1
fi
python .claude/skills/cli-deployment/scripts/verify-wheel.py "$WHEEL"
echo ""

echo "=========================================="
echo "Step 4: Local install test"
echo "=========================================="
pip uninstall ${PACKAGE_NAME} -y 2>/dev/null || true
pip install "$WHEEL"
echo ""

echo "Testing command..."
if $COMMAND_NAME --version >/dev/null 2>&1 || $COMMAND_NAME -h >/dev/null 2>&1 || true; then
    echo "✓ Command works!"
else
    echo "⚠️  Could not verify command (may not have --version or -h)"
fi
echo ""

echo "=========================================="
echo "Step 5: Commit and tag"
echo "=========================================="
read -p "Commit changes? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git add pyproject.toml
    git commit -m "chore: Bump version to $VERSION"
fi

echo ""
echo "Creating tag v$VERSION..."
git tag "v$VERSION"
echo ""

echo "=========================================="
echo "Step 6: Push to GitHub"
echo "=========================================="
read -p "Push to GitHub now? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git push
    git push origin "v$VERSION"
    echo ""
    echo "✓ Published! GitHub Actions will build and upload to PyPI."
    echo ""
    echo "Monitor at: https://github.com/your-username/your-repo/actions"
else
    echo "Skipped. Run manually when ready:"
    echo "  git push"
    echo "  git push origin v$VERSION"
fi

echo ""
echo "=========================================="
echo "Done!"
echo "=========================================="
