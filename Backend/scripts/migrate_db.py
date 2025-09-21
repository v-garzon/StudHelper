#!/usr/bin/env python3
"""Database migration script."""

import subprocess
import sys
from pathlib import Path


def run_command(command: str) -> bool:
    """Run a shell command."""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True)
    return result.returncode == 0


def main():
    """Main migration function."""
    if len(sys.argv) < 2:
        print("Usage: python migrate_db.py <command>")
        print("Commands:")
        print("  init     - Initialize migrations")
        print("  migrate  - Create new migration")
        print("  upgrade  - Apply migrations")
        print("  downgrade - Downgrade one migration")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "init":
        success = run_command("alembic init migrations")
        if success:
            print("✅ Migrations initialized")
    
    elif command == "migrate":
        message = sys.argv[2] if len(sys.argv) > 2 else "auto migration"
        success = run_command(f'alembic revision --autogenerate -m "{message}"')
        if success:
            print("✅ Migration created")
    
    elif command == "upgrade":
        success = run_command("alembic upgrade head")
        if success:
            print("✅ Migrations applied")
    
    elif command == "downgrade":
        success = run_command("alembic downgrade -1")
        if success:
            print("✅ Migration downgraded")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()


