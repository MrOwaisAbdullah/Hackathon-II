# Lessons Learned: CLI Deployment

All bugs, issues, and lessons learned from deploying TeamFlow Console to PyPI.

---

## Critical Bugs Fixed

### Bug #1: ModuleNotFoundError - No module named 'teamflow_console.lib'

**Symptom:**
```
ModuleNotFoundError: No module named 'teamflow_console.lib'
```

**Cause:**
`.gitignore` had `lib/` which ignored `teamflow_console/lib/`, so it wasn't included in the wheel.

**Fix:**
Add exception to `.gitignore`:
```gitignore
lib/
# But keep our package's lib directory
!teamflow_console/lib/
```

**Prevention:**
- Always check `.gitignore` for patterns that might ignore package directories
- Common problematic patterns: `cli/`, `lib/`, `models/`, `services/`
- Add exceptions: `!your_package/cli/`, etc.

---

### Bug #2: Absolute imports fail when installed

**Symptom:**
```python
from teamflow_console.lib.formatting import create_console
# ImportError: when package is installed via pip
```

**Cause:**
Absolute imports don't resolve correctly when a package is installed. Python's `__package__` context isn't set properly.

**Fix:**
Use relative imports:
```python
# pkg/__init__.py
from .cli.menus import MainMenu
from .lib.formatting import create_console

# pkg/cli/menus.py
from ..lib.formatting import create_console
```

**Prevention:**
- Always use relative imports within packages
- `from .sibling import` for same level
- `from ..parent import` for parent level
- Only use absolute imports for external packages

---

### Bug #3: Flat package structure fails when installed

**Symptom:**
```
project/
├── main.py
├── cli/
├── lib/

# Result: ModuleNotFoundError after pip install
```

**Cause:**
Files at root level install to `site-packages/`, but imports look for top-level `cli`, not `teamflow_console.cli`.

**Fix:**
Use proper package namespace:
```
project/
├── teamflow_console/
│   ├── __init__.py
│   ├── cli/
│   ├── lib/
```

**Prevention:**
- All code must be inside a package directory
- Package name in `pyproject.toml` should match directory name
- Entry point: `yourcommand = "package_name:main"`

---

### Bug #4: Files missing from wheel

**Symptom:**
Wheel installs but `ls site-packages/package/` shows missing directories.

**Cause:**
Hatchling build config not including subdirectories properly.

**Fix:**
```toml
[tool.hatch.build]
include = [
    "your_package/**/*.py",
]

[tool.hatch.build.targets.wheel]
packages = ["your_package"]
```

**Prevention:**
- Always test wheel contents before publishing: `python -m zipfile -l dist/*.whl`
- Verify all subdirectories are present
- Check that all `__init__.py` files are included

---

### Bug #5: Version already exists on PyPI

**Symptom:**
```
File already exists ('your_package-0.1.0.tar.gz')
```

**Cause:**
Trying to publish same version twice (PyPI doesn't allow overwrites).

**Fix:**
Bump version in `pyproject.toml`:
```toml
version = "0.1.1"  # Always increment
```

**Prevention:**
- Use semantic versioning properly
- Never try to overwrite an existing version
- Check PyPI for current version before publishing

---

### Bug #6: Main.py not included in wheel

**Symptom:**
```
ModuleNotFoundError: No module named 'main'
```

**Cause:**
Entry point points to `main:main` but `main.py` wasn't included in build.

**Fix:**
1. Rename `main.py` to `__init__.py` inside package
2. Update entry point: `cmd = "package:main"`
3. Ensure `__init__.py` is in the package directory

**Prevention:**
- Use `__init__.py` as entry point, not separate `main.py`
- Test import after install: `python -c "from package import main"`

---

## Design Patterns That Worked

### Pattern 1: Package Namespace with Relative Imports

```python
# package/__init__.py (entry point)
from .cli.menus import MainMenu
from .lib.formatting import create_console
from .services import TaskService

def main():
    app = Application()
    app.run()
```

```python
# package/cli/menus.py
from ..lib.formatting import create_console
from ..models import Task

class MainMenu:
    @staticmethod
    def display(console):
        console.print()  # Line break BEFORE
        panel = Panel(...)
        console.print(panel)
        console.print()  # Line break AFTER
```

---

### Pattern 2: Hatchling Build Configuration

```toml
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

---

### Pattern 3: Entry Point with Keyboard Interrupt

```python
def main() -> None:
    """Main entry point for CLI application."""
    app = YourApplication()
    try:
        app.run()
    except KeyboardInterrupt:
        print("\nExiting...")
        raise SystemExit(0)
```

---

### Pattern 4: GitHub Actions with API Token

```yaml
- name: Publish to PyPI
  uses: pypa/gh-action-pypi-publish@release/v1
  with:
    password: ${{ secrets.PYPI_API_TOKEN }}
```

**Setup:**
1. Create PyPI account
2. Generate API token
3. Add to GitHub Secrets as `PYPI_API_TOKEN`

---

## Quick Reference

### Package Structure
```
project/
├── your_package/
│   ├── __init__.py     # Entry point with main()
│   ├── cli/
│   │   ├── __init__.py
│   │   └── menus.py
│   ├── lib/
│   │   ├── __init__.py
│   │   └── formatting.py
│   ├── models/
│   └── services/
├── pyproject.toml
├── README.md
├── LICENSE
└── .gitignore
```

### Import Patterns
| From | To | Import |
|------|-----|--------|
| `pkg/__init__.py` | `pkg/cli/menus.py` | `from .cli.menus import` |
| `pkg/cli/menus.py` | `pkg/lib/formatting.py` | `from ..lib.formatting import` |
| `pkg/cli/menus.py` | `pkg/cli/prompts.py` | `from .prompts import` |
| `pkg/services/task.py` | `pkg/models/task.py` | `from ..models.task import` |

### Pre-Publish Checklist
- [ ] All imports are relative (no `from package.module`)
- [ ] `.gitignore` has exceptions for package dirs
- [ ] `pyproject.toml` has correct `packages` and `include`
- [ ] Version bumped in `pyproject.toml`
- [ ] Entry point: `cmd = "package:main"`
- [ ] Build locally: `python -m build`
- [ ] Verify wheel: `python -m zipfile -l dist/*.whl`
- [ ] Test install: `pip install dist/*.whl`
- [ ] Test command runs successfully

### Common Commands
```bash
# Build
python -m build

# Inspect wheel
python -m zipfile -l dist/*.whl

# Local test install
pip install dist/*.whl --force-reinstall

# Test import
python -c "from package import main; print('OK')"

# Release
git tag v0.1.0
git push origin v0.1.0
```

---

**Version:** 1.0.0
**Last Updated:** 2025-01-29
**Based On:** TeamFlow Console PyPI Deployment
