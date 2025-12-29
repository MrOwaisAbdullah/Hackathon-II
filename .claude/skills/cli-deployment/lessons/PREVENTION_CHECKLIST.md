# Pre-Publish Prevention Checklist

Use this checklist before publishing any Python CLI package to PyPI.

---

## Phase 1: Structure Validation

### Package Directory Structure
- [ ] All code is inside a package directory (e.g., `your_package/`)
- [ ] No code files at project root level (no `main.py`, `cli/`, etc. at root)
- [ ] Package directory has `__init__.py` with `main()` function
- [ ] Each subdirectory has `__init__.py` (can be empty)
- [ ] Directory structure:
  ```
  project/
  ├── your_package/
  │   ├── __init__.py
  │   ├── cli/
  │   │   └── __init__.py
  │   ├── lib/
  │   │   └── __init__.py
  │   ├── models/
  │   │   └── __init__.py
  │   └── services/
  │       └── __init__.py
  ├── pyproject.toml
  ├── README.md
  └── LICENSE
  ```

---

## Phase 2: Import Validation

### Relative Imports Only
- [ ] All imports within package use relative syntax
- [ ] `from .sibling import` for same level
- [ ] `from ..parent import` for parent level
- [ ] NO `from package.module` absolute imports within package
- [ ] Only absolute imports for external packages (rich, pydantic, etc.)

### Check with Grep
```bash
# Find any remaining absolute imports to your own package
grep -r "^from your_package\." your_package/
# Should return NO results
```

---

## Phase 3: .gitignore Validation

### Check for Problematic Patterns
- [ ] `.gitignore` reviewed for `cli/`, `lib/`, `models/`, `services/`
- [ ] Exceptions added for package directories:
  ```gitignore
  cli/
  !your_package/cli/

  lib/
  !your_package/lib/

  models/
  !your_package/models/

  services/
  !your_package/services/
  ```

### Verify Files Are Tracked
```bash
# Check that all package files are tracked by git
git ls-files your_package/

# Should see all __init__.py and .py files
```

---

## Phase 4: pyproject.toml Validation

### Build Configuration
- [ ] `name` uses hyphens: `your-package-name`
- [ ] `version` is bumped from previous release
- [ ] `packages = ["your_package"]` is set
- [ ] `include = ["your_package/**/*.py"]` is set
- [ ] Entry point: `yourcommand = "your_package:main"`

### Complete Check
```toml
[project]
name = "your-package-name"          # Check: hyphens
version = "0.1.0"                    # Check: bumped
description = "..."
readme = "README.md"
requires-python = ">=3.13"
license = { text = "MIT" }
authors = [...]

[project.scripts]
yourcommand = "your_package:main"    # Check: correct entry point

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build]
include = [
    "your_package/**/*.py",          # Check: pattern correct
]

[tool.hatch.build.targets.wheel]
packages = ["your_package"]          # Check: package name
```

---

## Phase 5: Build Verification

### Build and Inspect
```bash
# Build the wheel
python -m build

# List wheel contents
python -m zipfile -l dist/your_package-0.1.0-py3-none-any.whl
```

### Verify Contents
- [ ] `your_package/__init__.py` is present
- [ ] `your_package/cli/__init__.py` is present
- [ ] `your_package/lib/__init__.py` is present
- [ ] `your_package/models/__init__.py` is present
- [ ] `your_package/services/__init__.py` is present
- [ ] All `.py` files are included
- [ ] No unexpected missing files

---

## Phase 6: Local Install Test

### Test Install and Run
```bash
# Uninstall any existing version
pip uninstall your-package -y

# Install from built wheel
pip install dist/your_package-0.1.0-py3-none-any.whl

# Test the command
yourcommand

# Test imports
python -c "from your_package import main; print('Import OK')"
```

### Verify Functionality
- [ ] Command runs without errors
- [ ] Main menu displays correctly
- [ ] All menu options work
- [ ] No import errors
- [ ] Visual spacing looks correct

---

## Phase 7: Release Preparation

### Git Status
- [ ] All changes committed
- [ ] Working directory is clean
- [ ] Version in `pyproject.toml` is final
- [ ] Tag not yet created (will create after this check)

### Documentation
- [ ] README.md has installation instructions
- [ ] QUICKSTART.md (optional) for getting started
- [ ] CHANGELOG.md updated (if you have one)

---

## Phase 8: Tag and Publish

### Create and Push Tag
```bash
git tag v0.1.0
git push origin v0.1.0
```

### Verify GitHub Actions
- [ ] Workflow triggers on tag push
- [ ] Build job completes successfully
- [ ] Publish job completes successfully
- [ ] No errors in workflow logs

---

## Phase 9: Post-Publish Verification

### Install from PyPI
```bash
pip uninstall your-package -y
pip install your-package==0.1.0
```

### Final Test
- [ ] Command runs: `yourcommand`
- [ ] No import errors
- [ ] All features work
- [ ] Check PyPI page: `https://pypi.org/project/your-package/`

---

## Quick Reference Commands

```bash
# Verify structure
find your_package/ -name "*.py"
git ls-files your_package/

# Check imports
grep -r "^from your_package\." your_package/

# Build and inspect
python -m build
python -m zipfile -l dist/*.whl

# Local test
pip install dist/*.whl --force-reinstall
yourcommand

# Release
git tag v0.1.0 && git push origin v0.1.0

# Verify on PyPI
pip install your-package==0.1.0
```

---

## Common Issues to Watch For

| Issue | Symptom | Fix |
|-------|---------|-----|
| Wrong package structure | `ModuleNotFoundError` after install | Use `your_package/` directory |
| Absolute imports | `ImportError` when installed | Use `from .module` imports |
| .gitignore excludes files | Files missing from wheel | Add `!your_package/dir/` |
| Wrong entry point | `command not found` | Check `[project.scripts]` |
| Old version | `File already exists` | Bump version in `pyproject.toml` |

---

**Remember:** PyPI does NOT allow overwriting existing versions. Always verify before tagging!
