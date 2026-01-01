#!/usr/bin/env python3
"""
Database initialization script for Neon PostgreSQL.

Creates all tables and applies migrations.
Usage: python scripts/init_db.py
"""
import os
import asyncio
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine
from config import settings

# Import all models to ensure they're registered with SQLModel.metadata
from models.user import User
from models.user_preferences import UserPreferences
from models.chat_session import ChatSession

async def init_database() -> None:
    """Initialize database with all tables."""
    print("Initializing database...")

    # Create sync engine for DDL operations
    from sqlalchemy import create_engine
    sync_engine = create_engine(settings.DATABASE_URL)

    try:
        # Create all tables
        print(f"Connecting to: {settings.DATABASE_URL.split('@')[1]}")  # Hide credentials
        SQLModel.metadata.create_all(sync_engine)
        print("✓ All tables created successfully")

        # Run migrations if alembic is available
        try:
            from alembic.config import Config
            from alembic import command

            alembic_cfg = Config("alembic.ini")
            command.upgrade(alembic_cfg, "head")
            print("✓ Migrations applied successfully")
        except ImportError:
            print("! Alembic not available, skipping migrations")

    except Exception as e:
        print(f"✗ Error initializing database: {e}")
        raise
    finally:
        sync_engine.dispose()
        print("\nDatabase initialization complete")

if __name__ == "__main__":
    asyncio.run(init_database())
