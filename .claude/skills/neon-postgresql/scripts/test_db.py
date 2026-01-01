#!/usr/bin/env python3
"""
Database connection test script for Neon PostgreSQL.

Verifies connection, checks tables, and tests basic queries.
Usage: python scripts/test_db.py
"""
import os
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from config import settings

async def test_connection() -> None:
    """Test database connection and basic operations."""
    print("Testing Neon PostgreSQL connection...")

    # Create async engine
    db_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    engine = create_async_engine(db_url, echo=False)

    try:
        # Test connection
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✓ Connected to PostgreSQL")
            print(f"  Version: {version.split(',')[0]}")

        # Test session
        AsyncSessionLocal = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

        async with AsyncSessionLocal() as session:
            # Check tables exist
            result = await session.execute(text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result]
            print(f"\n✓ Found {len(tables)} tables:")
            for table in tables:
                print(f"  - {table}")

            # Test simple query (if users table exists)
            if "users" in tables:
                result = await session.execute(text("SELECT COUNT(*) FROM users"))
                count = result.scalar()
                print(f"\n✓ Users table contains {count} records")

        print("\n✓ All connection tests passed")

    except Exception as e:
        print(f"\n✗ Connection test failed: {e}")
        raise
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(test_connection())
