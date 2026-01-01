#!/usr/bin/env python3
"""
Migration management script for Alembic.

Provides simplified commands for common migration operations.
Usage:
  python scripts/migrate.py status
  python scripts/migrate.py upgrade
  python scripts/migrate.py downgrade
  python scripts/migrate.py create "migration message"
"""
import sys
import subprocess
from pathlib import Path

def run_alembic(command: str) -> int:
    """Run alembic command and return exit code."""
    result = subprocess.run(
        ["uv", "run", "alembic"] + command.split(),
        cwd=Path(__file__).parent.parent
    )
    return result.returncode

def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python migrate.py <command>")
        print("\nCommands:")
        print("  status    - Show current migration version")
        print("  history   - Show migration history")
        print("  upgrade   - Apply all pending migrations")
        print("  downgrade - Rollback one migration")
        print("  create    - Create new migration (requires message)")
        print("\nExamples:")
        print("  python migrate.py status")
        print("  python migrate.py create 'Add user preferences table'")
        return 1

    command = sys.argv[1]

    if command == "status":
        return run_alembic("current")

    elif command == "history":
        return run_alembic("history")

    elif command == "upgrade":
        print("Applying migrations...")
        return run_alembic("upgrade head")

    elif command == "downgrade":
        print("Rolling back one migration...")
        return run_alembic("downgrade -1")

    elif command == "create":
        if len(sys.argv) < 3:
            print("Error: create command requires a message")
            print("Usage: python migrate.py create 'Your migration message'")
            return 1

        message = sys.argv[2]
        print(f"Creating migration: {message}")
        return run_alembic(f"revision --autogenerate -m '{message}'")

    else:
        print(f"Unknown command: {command}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
