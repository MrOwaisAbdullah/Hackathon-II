"""Seed database with test agency and admin user."""
import sys
from pathlib import Path
from uuid import uuid4

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlmodel import Session, select, text

from app.core.security import get_password_hash
from app.db.session import engine
from app.models.agency import Agency
from app.models.user import User, UserRole


def seed_database() -> None:
    """Create test agency and admin user."""
    with Session(engine) as session:
        # Check if test user already exists
        existing_user = session.exec(
            select(User).where(User.email == "admin@test.com")
        ).first()

        if existing_user:
            print("✓ Test user already exists: admin@test.com")
            return

        # Check if test agency already exists (from previous failed run)
        existing_agency = session.exec(
            select(Agency).where(Agency.email == "admin@test.com")
        ).first()

        if existing_agency:
            agency = existing_agency
            print(f"✓ Using existing agency: {agency.name} (ID: {agency.id})")
        else:
            # Create test agency
            agency = Agency(
                name="Test Agency",
                email="admin@test.com",
            )
            session.add(agency)
            session.commit()
            session.refresh(agency)
            print(f"✓ Created agency: {agency.name} (ID: {agency.id})")

        # Create admin user using raw SQL to bypass enum issues
        from datetime import datetime

        user_id = uuid4()
        hashed_pw = get_password_hash("password123")
        now = datetime.utcnow()

        insert_sql = text("""
            INSERT INTO users (id, email, name, hashed_password, role, agency_id, created_at, updated_at)
            VALUES (:id, :email, :name, :hashed_password, :role, :agency_id, :created_at, :updated_at)
        """)

        session.execute(insert_sql, {
            "id": user_id,
            "email": "admin@test.com",
            "name": "Admin User",
            "hashed_password": hashed_pw,
            "role": "admin",  # Lowercase to match database enum
            "agency_id": agency.id,
            "created_at": now,
            "updated_at": now,
        })
        session.commit()

        print(f"✓ Created admin user: admin@test.com (ID: {user_id})")
        print("\nTest credentials:")
        print("  Email: admin@test.com")
        print("  Password: password123")


if __name__ == "__main__":
    print("Seeding database...")
    seed_database()
    print("\n✅ Database seeded successfully!")
