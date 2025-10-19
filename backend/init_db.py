"""
Database initialization script for CALIDUS
Creates tables and optionally seeds demo data
"""

from app.database import engine, SessionLocal, Base
from app.models.user import User
from app.core.security import get_password_hash


def init_db():
    """Initialize the database"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")


def seed_demo_users():
    """Seed demo users for testing"""
    db = SessionLocal()

    try:
        # Check if users already exist
        existing_admin = db.query(User).filter(User.username == "admin").first()
        if existing_admin:
            print("⚠️  Demo users already exist. Skipping seed.")
            return

        print("Seeding demo users...")

        # Create admin user
        admin = User(
            username="admin",
            email="admin@calidus.com",
            hashed_password=get_password_hash("demo2024"),
            role="admin",
            is_active=True
        )
        db.add(admin)

        # Create engineer user
        engineer = User(
            username="engineer",
            email="engineer@calidus.com",
            hashed_password=get_password_hash("engineer2024"),
            role="engineer",
            is_active=True
        )
        db.add(engineer)

        # Create viewer user
        viewer = User(
            username="viewer",
            email="viewer@calidus.com",
            hashed_password=get_password_hash("viewer2024"),
            role="viewer",
            is_active=True
        )
        db.add(viewer)

        db.commit()

        print("✅ Demo users created:")
        print("   - admin / demo2024 (Admin)")
        print("   - engineer / engineer2024 (Engineer)")
        print("   - viewer / viewer2024 (Viewer)")

    except Exception as e:
        print(f"❌ Error seeding demo users: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("🚀 CALIDUS Database Initialization")
    print("=" * 50)

    init_db()
    seed_demo_users()

    print("=" * 50)
    print("✅ Database initialization complete!")
