# Common Pitfalls in CLI Deployment

Mistakes to avoid when deploying Python CLI applications to PyPI.

---

## Pitfall #1: Flat Package Structure

**The Mistake:**
```
myproject/
├── main.py
├── cli/
├── lib/
├── models/
└── pyproject.toml
```

**Why It Fails:**
When installed via pip, files go to `site-packages/` but imports like `from cli.menus` look for top-level `cli`, not `myproject.cli`.

**The Fix:**
```
myproject/
├── myproject/
│   ├── __init__.py
│   ├── cli/
│   ├── lib/
│   └── models/
└── pyproject.toml
```

**Takeaway:** Always use a package namespace directory.

---

## Pitfall #2: Absolute Imports in Packages

**The Mistake:**
```python
# myproject/__init__.py
from myproject.cli.menus import MainMenu  # FAILS when installed
```

**Why It Fails:**
Python doesn't resolve `myproject` correctly when the package is imported as a module.

**The Fix:**
```python
# myproject/__init__.py
from .cli.menus import MainMenu  # Works
```

**Takeaway:** Use relative imports (`.` for same level, `..` for parent) within packages.

---

## Pitfall #3: .gitignore Excludes Package Directories

**The Mistake:**
```gitignore
lib/
models/
services/
```

**Why It Fails:**
Git ignores `myproject/lib/`, so it's not in the wheel.

**The Fix:**
```gitignore
lib/
!myproject/lib/

models/
!myproject/models/

services/
!myproject/services/
```

**Takeaway:** Add exceptions for your package directories.

---

## Pitfall #4: main.py Instead of __init__.py

**The Mistake:**
```
myproject/
├── main.py           # Entry point here
├── cli/
└── pyproject.toml

# pyproject.toml
[project.scripts]
mycommand = "main:main"
```

**Why It Fails:**
`main.py` might not be included in wheel, or imports fail.

**The Fix:**
```
myproject/
├── __init__.py       # Entry point here (rename main.py)
├── cli/
└── pyproject.toml

# pyproject.toml
[project.scripts]
mycommand = "myproject:main"
```

**Takeaway:** Use `__init__.py` as the entry point inside the package.

---

## Pitfall #5: Wrong Entry Point Format

**The Mistake:**
```toml
[project.scripts]
mycommand = "myproject.main:main"  # WRONG if main is in __init__.py
mycommand = "myproject:main"       # WRONG if main is in main.py
```

**Why It Fails:**
Python can't find the module or function.

**The Fix:**
```toml
# If main() is in myproject/__init__.py:
[project.scripts]
mycommand = "myproject:main"

# If main() is in myproject/main.py:
[project.scripts]
mycommand = "myproject.main:main"
```

**Takeaway:** Format is `module.submodule:function` or `package:function`.

---

## Pitfall #6: Forgetting to Bump Version

**The Mistake:**
```toml
[project]
version = "0.1.0"  # Already published!
```

**Why It Fails:**
PyPI rejects: `File already exists ('package-0.1.0.tar.gz')`

**The Fix:**
```toml
[project]
version = "0.1.1"  # Always increment
```

**Takeaway:** PyPI doesn't allow overwrites. Always bump version.

---

## Pitfall #7: Missing __init__.py Files

**The Mistake:**
```
myproject/
├── __init__.py
├── cli/              # Missing __init__.py
└── lib/              # Missing __init__.py
```

**Why It Fails:**
Python doesn't treat directories as packages without `__init__.py`.

**The Fix:**
```
myproject/
├── __init__.py
├── cli/
│   └── __init__.py   # Can be empty
└── lib/
    └── __init__.py   # Can be empty
```

**Takeaway:** Every package directory needs `__init__.py`.

---

## Pitfall #8: Trusted Publishing Without Setup

**The Mistake:**
```yaml
- name: Publish to PyPI
  uses: pypa/gh-action-pypi-publish@release/v1
  # No password, using trusted publishing
```

**Why It Fails:**
```
invalid-publisher: valid token, but no corresponding publisher
```

**The Fix:**
```yaml
- name: Publish to PyPI
  uses: pypa/gh-action-pypi-publish@release/v1
  with:
    password: ${{ secrets.PYPI_API_TOKEN }}
```

**Takeaway:** Use API token authentication for simplicity.

---

## Pitfall #9: Not Testing Wheel Contents

**The Mistake:**
Building and publishing without inspecting the wheel.

**Why It Fails:**
Discover missing files only after users report issues.

**The Fix:**
```bash
# Always inspect before publishing
python -m zipfile -l dist/*.whl
```

**Takeaway:** Verify wheel contents before every release.

---

## Pitfall #10: Testing Only in Development Mode

**The Mistake:**
Testing with `python main.py` or `PYTHONPATH=src python -m src.main`.

**Why It Fails:**
Doesn't catch import issues that only appear when installed.

**The Fix:**
```bash
# Build and test install
python -m build
pip install dist/*.whl --force-reinstall
mycommand  # Test installed command
```

**Takeaway:** Always test the installed package, not development mode.

---

## Quick Reference

| Pitfall | Quick Check | Fix |
|---------|-------------|-----|
| Flat structure | Files at root? | Use `pkg/` directory |
| Absolute imports | `from pkg.module`? | Use `from .module` |
| .gitignore | Files tracked? | Add `!pkg/dir/` |
| main.py | Entry point location? | Use `__init__.py` |
| Entry point | Format correct? | Check `pkg:func` |
| Version | Bumped? | Increment version |
| Missing __init__.py | All dirs have it? | Add empty files |
| Trusted publishing | Workflow fails? | Use API token |
| Not testing wheel | Did you inspect? | `zipfile -l dist/*.whl` |
| Dev mode only | Tested install? | `pip install dist/*.whl` |

---

## Prevention Checklist

Before tagging:

```bash
# 1. Check structure
ls -la your_package/
# Should see __init__.py and subdirectories

# 2. Check imports
grep -r "^from your_package\." your_package/
# Should return nothing

# 3. Check git tracking
git ls-files your_package/
# Should see all __init__.py files

# 4. Build and inspect
python -m build
python -m zipfile -l dist/*.whl

# 5. Test install
pip install dist/*.whl --force-reinstall
yourcommand

# 6. Now tag
git tag v0.1.0
git push origin v0.1.0
```

---

**Remember:** Test twice, publish once. PyPI doesn't allow undo!
