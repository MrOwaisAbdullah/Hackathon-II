---
name: cli-deployment
description: Deploy Python CLI applications to PyPI with GitHub Actions CI/CD. Includes all lessons learned from real-world deployment (package namespaces, relative imports, .gitignore patterns, hatchling config).
category: backend
version: 1.0.0
---

# CLI Deployment Skill

## Purpose

Deploy Python CLI applications to PyPI with automated GitHub Actions CI/CD, avoiding common pitfalls.

This skill captures all lessons learned from deploying TeamFlow Console to PyPI, including:
- Package namespace structure
- Relative vs absolute imports
- pyproject.toml configuration (hatchling)
- .gitignore patterns to avoid
- GitHub Actions workflow setup
- Common issues and solutions

## When to Use This Skill

Use this skill when:
- Creating a new Python CLI package from scratch
- Converting an existing script to a publishable package
- Fixing import/packaging issues in a CLI app
- Setting up automated PyPI publishing
- Debugging "ModuleNotFoundError" after pip install

## Core Issues & Solutions

### Issue 1: Flat Package Structure

**Problem:** Files at root level (`main.py`, `cli/`, `lib/`) fail when installed because Python can't find the modules.

```
project/
├── main.py
├── cli/
├── lib/
└── pyproject.toml

# Result: ModuleNotFoundError: No module named 'cli'
```

**Solution:** Use proper package namespace:

```
project/
├── your_package/
│   ├── __init__.py
│   ├── cli/
│   ├── lib/
│   └── ...
└── pyproject.toml
```

### Issue 2: Absolute Imports Fail in Installed Package

**Problem:** `from your_package.lib.formatting import` fails when installed.

```python
# your_package/__init__.py
from your_package.cli.menus import MainMenu  # FAILS
```

**Solution:** Use relative imports:

```python
# your_package/__init__.py
from .cli.menus import MainMenu  # Works

# your_package/cli/menus.py
from ..lib.formatting import create_console  # Parent level
from .prompts import TaskPrompts  # Same level
```

### Issue 3: .gitignore Excludes Package Directories

**Problem:** `.gitignore` has `lib/` which ignores `your_package/lib/`.

```gitignore
lib/
# Result: your_package/lib/ not in wheel
```

**Solution:** Add exception:

```gitignore
lib/
!your_package/lib/
```

### Issue 4: Files Missing from Wheel

**Problem:** Subdirectories not included in built wheel.

**Solution:** Configure `pyproject.toml`:

```toml
[tool.hatch.build]
include = [
    "your_package/**/*.py",
]

[tool.hatch.build.targets.wheel]
packages = ["your_package"]
```

## pyproject.toml Template

```toml
[project]
name = "your-package-name"  # hyphens in PyPI name
version = "0.1.0"
description = "Your package description"
readme = "README.md"
requires-python = ">=3.13"
license = { text = "MIT" }
authors = [
    { name = "Your Name", email = "your@email.com" }
]

dependencies = [
    "typer>=0.12.0",
    "rich>=13.7.0",
]

[project.urls]
Homepage = "https://github.com/username/repo"
Repository = "https://github.com/username/repo"

[project.scripts]
yourcommand = "your_package:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build]
include = [
    "your_package/**/*.py",
]

[tool.hatch.build.targets.wheel]
packages = ["your_package"]
```

## GitHub Actions Workflow

Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  push:
    tags:
      - 'v*.*.*'

permissions:
  contents: write

jobs:
  build:
    name: Build package
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.13'

      - name: Install build dependencies
        run: |
          python -m pip install --upgrade pip
          pip install build twine

      - name: Build package
        run: python -m build

      - name: Store distribution packages
        uses: actions/upload-artifact@v4
        with:
          name: python-package-distributions
          path: dist/

  publish-to-pypi:
    name: Publish to PyPI
    needs: build
    runs-on: ubuntu-latest

    steps:
      - name: Download distribution packages
        uses: actions/download-artifact@v4
        with:
          name: python-package-distributions
          path: dist/

      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          password: ${{ secrets.PYPI_API_TOKEN }}
```

### Setup Steps

1. Create PyPI account: https://pypi.org/account/register/
2. Create API token: Account settings → API tokens
3. Add to GitHub Secrets: `PYPI_API_TOKEN`

## Import Quick Reference

| Location | Import Pattern | Example |
|----------|---------------|---------|
| `pkg/__init__.py` → `pkg/cli/` | `from .cli.menus import` | Same level (dot) |
| `pkg/cli/menus.py` → `pkg/lib/` | `from ..lib.formatting import` | Parent level (dot dot) |
| `pkg/cli/menus.py` → `pkg/cli/prompts.py` | `from .prompts import` | Same level (dot) |
| `pkg/services/task.py` → `pkg/models/` | `from ..models.task import` | Parent level (dot dot) |

## Testing Before Publishing

```bash
# Build the wheel
python -m build

# Inspect wheel contents
python -m zipfile -l dist/*.whl

# Local test install
pip install dist/*.whl --force-reinstall

# Test the command
yourcommand

# Verify imports
python -c "from your_package import main; print('OK')"
```

## Release Workflow

```bash
# 1. Update version in pyproject.toml
# 2. Commit changes
git add pyproject.toml
git commit -m "chore: Bump version to 0.1.0"

# 3. Create and push tag
git tag v0.1.0
git push origin v0.1.0

# 4. GitHub Actions automatically builds and publishes
```

## Common Issues Reference

| Error | Cause | Fix |
|-------|--------|-----|
| `ModuleNotFoundError: No module named 'pkg.lib'` | `.gitignore` excludes `lib/` | Add `!your_package/lib/` to `.gitignore` |
| `ImportError: attempted relative import beyond top-level` | Wrong relative level | Use `..` for parent, `.` for same level |
| `command not found` | Entry point wrong | Check `[project.scripts]` in `pyproject.toml` |
| Files missing from wheel | Build config wrong | Set `packages = ["your_package"]` |

## CLI Best Practices

### Entry Point Pattern

```python
# your_package/__init__.py
def main() -> None:
    """Main entry point."""
    app = YourApplication()
    try:
        app.run()
    except KeyboardInterrupt:
        print("\nExiting...")
        raise SystemExit(0)
```

### Visual Spacing

```python
def display(console: Console) -> None:
    console.clear()
    console.print()  # BEFORE

    panel = Panel(content)
    console.print(panel)
    console.print()  # AFTER
```

## Resources

- [Python Packaging Tutorial](https://packaging.python.org/)
- [Hatchling Documentation](https://hatch.pypa.io/latest/)
- [PyPI Publishing](https://pypi.org/help/#publishing)
