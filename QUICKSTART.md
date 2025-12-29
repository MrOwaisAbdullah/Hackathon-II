# TeamFlow Console - Quick Start Guide

Get up and running with TeamFlow Console in under 2 minutes.

## Installation

```bash
pip install teamflow-console
```

**Requirements:** Python 3.13 or higher

## Running the App

```bash
teamflow
```

## Your First Task (Under 60 Seconds)

1. **Launch the app**
   ```bash
   $ teamflow
   ```

2. **Press Enter** to dismiss the data loss warning

3. **Main Menu appears** - Press `1` for Task Management

4. **Task Management Menu** - Press `1` to Create Task

5. **Fill in the task details:**
   - **Title**: `Fix login bug` (or any task)
   - **Description**: Press Enter to skip (optional)
   - **Priority**: Press `1` for High (or 2 for Medium, 3 for Low)
   - **Assignee**: Press `0` for Unassigned

6. **Done!** Your first task is created

## Keyboard Shortcuts

| Key | Action | Where |
|-----|--------|-------|
| `1-5` | Select option | All menus |
| `0` | Back to main menu | Submenus |
| `c` | Go to Create Task | Main menu |
| `l` | Go to List Tasks | Main menu |
| `q` | Quit | Anywhere |
| `Enter` | Continue | After actions |

## Common Workflows

### Create a User

```
Main Menu → 2 (User & Team Mgmt) → 1 (Create User)
Name: Sarah
Role: 2 (Developer)
Skills: Python,FastAPI (optional)
```

### Create a Team

```
Main Menu → 2 (User & Team Mgmt) → 2 (Create Team)
Team name: Frontend Squad
Members: 1,2 (comma-separated user IDs)
```

### Assign a Task

```
Main Menu → 1 (Task Mgmt) → 3 (Update Task)
Task ID: 1
Select field to update: 5 (Assignee)
Select user: 1 (Sarah)
```

### View All Tasks

```
Main Menu → 3 (View Tasks)
```

### Complete a Task

```
Main Menu → 1 (Task Mgmt) → 4 (Complete Task)
Task ID: 1
Confirm: Y
```

## Understanding the Display

### Task List

```
┌──────┬─────────────────┬──────────┬─────────────┬────────────┐
│  ID  │ Title           │ Priority │ Assignee    │ Status     │
├──────┼─────────────────┼──────────┼─────────────┼────────────┤
│   1  │ Fix Navbar       │ High     │ Sarah       │ Todo       │
│   2  │ Update docs      │ Medium   │ Unassigned  │ Done       │
└──────┴─────────────────┴──────────┴─────────────┴────────────┘
```

**Color Coding:**
- **Red** = High Priority
- **Yellow** = Medium Priority
- **Blue** = Low Priority
- **Green** = Done Status

## Data Persistence

**Important:** This version uses **in-memory storage**. All data is lost when you exit the application.

This is intentional for Phase 1 (validation/learning phase). Persistent database storage comes in a future update.

## Troubleshooting

### "ModuleNotFoundError" after install

Try reinstalling:
```bash
pip uninstall teamflow-console -y
pip install teamflow-console
```

### "command not found: teamflow"

Make sure you're using the correct Python environment:
```bash
python -m teamflow_console
```

### Terminal shows strange characters

Use a modern terminal:
- **Windows:** Windows Terminal or PowerShell 5.1+
- **macOS:** Terminal.app or iTerm2
- **Linux:** Any modern terminal emulator

## Development

For development setup and running tests, see:
- [Full Documentation](specs/001-console-task-distribution/quickstart.md)
- [Project README](README.md)

## Need Help?

- **Issues:** [GitHub Issues](https://github.com/MrOwaisAbdullah/Teamflow/issues)
- **Documentation:** [Full Quick Start](specs/001-console-task-distribution/quickstart.md)

---

**Enjoy using TeamFlow Console!** 🚀
