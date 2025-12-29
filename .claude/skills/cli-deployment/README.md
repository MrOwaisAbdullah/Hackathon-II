# CLI Deployment Skill

Deploy Python CLI applications to PyPI with GitHub Actions CI/CD. Contains all lessons learned from real-world deployment.

## Quick Start

```bash
# Invoke the skill when creating or deploying a CLI package
/skill cli-deployment
```

## What's Included

### 📁 Templates
- `pyproject.toml.template` - Complete package configuration
- `workflow.yml.template` - GitHub Actions publish workflow
- `entrypoint.py.template` - CLI entry point pattern
- `gitignore.template` - Proper .gitignore with package exceptions

### 📜 Scripts
- `verify-wheel.py` - Inspect wheel contents before publishing
- `check-imports.py` - Scan for problematic import patterns
- `publish.sh` - Automated publish workflow

### 📚 Documentation
- `LESSONS_LEARNED.md` - All bugs encountered and fixes
- `PREVENTION_CHECKLIST.md` - Pre-publish verification checklist
- `COMMON_PITFALLS.md` - Mistakes to avoid

## Key Learnings

### Package Namespace
```
✓ DO:                           ✗ DON'T:
project/                        project/
├── your_package/               ├── main.py
│   ├── __init__.py             ├── cli/
│   ├── cli/                    ├── lib/
│   └── lib/                    └── pyproject.toml
└── pyproject.toml
```

### Import Patterns
```python
# ✓ Relative imports (within package)
from .cli.menus import MainMenu      # Same level
from ..lib.formatting import create_console  # Parent level

# ✗ Absolute imports (fail when installed)
from your_package.cli.menus import MainMenu
```

### .gitignore Exceptions
```gitignore
lib/
!your_package/lib/     # EXCEPTION - keep package lib/
cli/
!your_package/cli/     # EXCEPTION - keep package cli/
```

## Quick Reference

### Build Commands
```bash
# Build wheel
python -m build

# Inspect contents
python -m zipfile -l dist/*.whl

# Run verification script
python .claude/skills/cli-deployment/scripts/verify-wheel.py dist/*.whl

# Check imports
python .claude/skills/cli-deployment/scripts/check-imports.py your_package/
```

### Publish Workflow
```bash
# 1. Update version in pyproject.toml
# 2. Run checks
python -m build && python check-imports.py your_package/

# 3. Local test
pip install dist/*.whl --force-reinstall
yourcommand

# 4. Tag and push
git tag v0.1.0
git push origin v0.1.0

# 5. GitHub Actions automatically publishes to PyPI
```

## Templates Usage

### pyproject.toml
```bash
cp .claude/skills/cli-deployment/templates/pyproject.toml.template pyproject.toml
# Edit: name, version, description, your_package
```

### GitHub Actions
```bash
mkdir -p .github/workflows
cp .claude/skills/cli-deployment/templates/workflow.yml.template .github/workflows/publish.yml
# Edit: your-package, PYPI_API_TOKEN secret
```

### .gitignore
```bash
cp .claude/skills/cli-deployment/templates/gitignore.template .gitignore
# Edit: your_package exceptions
```

## Common Issues

| Issue | Fix |
|-------|-----|
| `ModuleNotFoundError: No module named 'pkg.lib'` | Add `!your_package/lib/` to `.gitignore` |
| `ImportError: attempted relative import beyond` | Use `.` for same level, `..` for parent |
| `command not found` | Check `[project.scripts]` in `pyproject.toml` |
| Files missing from wheel | Set `packages = ["your_package"]` |
| `File already exists` | Bump version in `pyproject.toml` |

## Resources

- [Python Packaging Tutorial](https://packaging.python.org/)
- [Hatchling Documentation](https://hatch.pypa.io/latest/)
- [PyPI Publishing](https://pypi.org/help/#publishing)
