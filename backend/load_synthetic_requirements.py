#!/usr/bin/env python3
"""
Load synthetic requirements from JSON files into the database.
Replaces the auto-generated 16,500 requirements with 103 real synthetic requirements.
"""
import json
import os
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import Requirement, RequirementType, RequirementPriority, RequirementStatus, VerificationMethod
from app.config import get_settings

# Database connection
settings = get_settings()
DATABASE_URL = settings.database_url
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def map_type(type_str: str) -> RequirementType:
    """Map JSON type to enum"""
    mapping = {
        "Aircraft_High_Level_Requirement": RequirementType.AHLR,
        "System_Requirement": RequirementType.SYSTEM,
        "Technical_Specification": RequirementType.TECHNICAL,
        "Certification_Requirement": RequirementType.CERTIFICATION
    }
    return mapping.get(type_str, RequirementType.TECHNICAL)

def map_priority(priority_str: str) -> RequirementPriority:
    """Map JSON priority to enum"""
    mapping = {
        "Critical": RequirementPriority.CRITICAL,
        "High": RequirementPriority.HIGH,
        "Medium": RequirementPriority.MEDIUM,
        "Low": RequirementPriority.LOW
    }
    return mapping.get(priority_str, RequirementPriority.MEDIUM)

def map_status(status_str: str) -> RequirementStatus:
    """Map JSON status to enum"""
    mapping = {
        "Draft": RequirementStatus.DRAFT,
        "Under_Review": RequirementStatus.UNDER_REVIEW,
        "In Review": RequirementStatus.UNDER_REVIEW,
        "Approved": RequirementStatus.APPROVED,
        "Deprecated": RequirementStatus.DEPRECATED
    }
    return mapping.get(status_str, RequirementStatus.DRAFT)

def map_verification(method_str: str) -> VerificationMethod:
    """Map JSON verification method to enum"""
    mapping = {
        "Test": VerificationMethod.TEST,
        "Analysis": VerificationMethod.ANALYSIS,
        "Inspection": VerificationMethod.INSPECTION,
        "Demonstration": VerificationMethod.DEMONSTRATION
    }
    return mapping.get(method_str, VerificationMethod.TEST)

def load_synthetic_requirements():
    """Load all synthetic requirements from JSON files"""
    print("=" * 70)
    print("🔄 LOADING SYNTHETIC REQUIREMENTS")
    print("=" * 70)

    # Path to synthetic requirements
    base_path = Path("/app/synthetic_requirements")

    if not base_path.exists():
        print(f"❌ Synthetic requirements directory not found: {base_path}")
        return

    # Find all JSON files (excluding special files)
    json_files = []
    for folder in ["AHLR", "System", "Technical", "Certification"]:
        folder_path = base_path / folder
        if folder_path.exists():
            json_files.extend(folder_path.glob("*.json"))

    print(f"\n📁 Found {len(json_files)} synthetic requirement files")

    if len(json_files) == 0:
        print("❌ No JSON files found!")
        return

    # Create database session
    db = SessionLocal()

    try:
        # Step 1: Clear existing requirements
        print("\n1️⃣  Clearing existing requirements...")
        db.execute(text("DELETE FROM test_cases"))
        db.execute(text("DELETE FROM traceability_links"))
        db.execute(text("DELETE FROM requirements"))
        db.commit()
        print("   ✅ Existing data cleared")

        # Step 2: Load synthetic requirements
        print(f"\n2️⃣  Loading {len(json_files)} synthetic requirements...")

        loaded_count = 0
        errors = []

        for json_file in sorted(json_files):
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)

                # Create requirement
                req = Requirement(
                    requirement_id=data["requirement_id"],
                    type=map_type(data["type"]),
                    category=data.get("category", "General"),
                    title=data["title"],
                    description=data["description"],
                    priority=map_priority(data.get("priority", "Medium")),
                    status=map_status(data.get("status", "Draft")),
                    verification_method=map_verification(data.get("verification_method", "Test")),
                    regulatory_document=data.get("regulatory_source", {}).get("document"),
                    regulatory_section=data.get("regulatory_source", {}).get("section"),
                    regulatory_page=data.get("regulatory_source", {}).get("page"),
                    file_path=data.get("regulatory_source", {}).get("file_path"),
                    version=data.get("version", "1.0"),
                    rationale=data.get("rationale"),
                    created_by_id=1  # Admin user
                )

                db.add(req)
                loaded_count += 1

                if loaded_count % 10 == 0:
                    print(f"   ... loaded {loaded_count} requirements")

            except Exception as e:
                import traceback
                error_details = traceback.format_exc()
                errors.append(f"{json_file.name}: {str(e)}\n{error_details}")
                continue

        db.commit()

        print(f"\n   ✅ Loaded {loaded_count} synthetic requirements")

        if errors:
            print(f"\n   ⚠️  {len(errors)} errors encountered:")
            for error in errors[:2]:  # Show first 2 errors with full details
                print(f"\n{error}\n")

        # Step 3: Verify loaded data
        print("\n3️⃣  Verifying loaded data...")
        counts = db.execute(text("""
            SELECT type, COUNT(*) as count
            FROM requirements
            GROUP BY type
            ORDER BY type
        """)).fetchall()

        total = 0
        for row in counts:
            print(f"   - {row[0]}: {row[1]} requirements")
            total += row[1]

        print(f"\n   ✅ Total requirements in database: {total}")

        print("\n" + "=" * 70)
        print("✅ SYNTHETIC REQUIREMENTS LOADED SUCCESSFULLY")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ Error loading requirements: {str(e)}")
        db.rollback()
        raise

    finally:
        db.close()

if __name__ == "__main__":
    load_synthetic_requirements()
