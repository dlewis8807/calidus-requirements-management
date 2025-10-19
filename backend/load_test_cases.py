#!/usr/bin/env python3
"""
Load test cases from JSON files into the database.
"""
import json
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Requirement, TestCase, TestCaseStatus, TestCasePriority
from app.config import get_settings

# Database connection
settings = get_settings()
DATABASE_URL = settings.database_url
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def map_status(status_str: str) -> TestCaseStatus:
    """Map JSON status to enum"""
    mapping = {
        "Passed": TestCaseStatus.PASSED,
        "Failed": TestCaseStatus.FAILED,
        "Not_Executed": TestCaseStatus.PENDING,
        "Pending": TestCaseStatus.PENDING,
        "In_Progress": TestCaseStatus.IN_PROGRESS,
        "Blocked": TestCaseStatus.BLOCKED
    }
    return mapping.get(status_str, TestCaseStatus.PENDING)

def map_priority(priority_str: str) -> TestCasePriority:
    """Map JSON priority to enum"""
    mapping = {
        "Critical": TestCasePriority.CRITICAL,
        "High": TestCasePriority.HIGH,
        "Medium": TestCasePriority.MEDIUM,
        "Low": TestCasePriority.LOW
    }
    return mapping.get(priority_str, TestCasePriority.MEDIUM)

def load_test_cases():
    """Load all test cases from JSON files"""
    print("="*70)
    print("🧪 LOADING TEST CASES")
    print("="*70)

    # Path to test cases
    test_case_path = Path("/app/synthetic_requirements/test_cases")

    if not test_case_path.exists():
        print(f"❌ Test cases directory not found: {test_case_path}")
        return

    # Find all test case JSON files
    json_files = sorted(test_case_path.glob("TC-*.json"))
    print(f"\n📁 Found {len(json_files)} test case files")

    if len(json_files) == 0:
        print("❌ No test case files found!")
        return

    db = SessionLocal()

    try:
        # Get all requirements indexed by requirement_id
        requirements = {req.requirement_id: req for req in db.query(Requirement).all()}
        print(f"📦 {len(requirements)} requirements available for linking")

        loaded_count = 0
        skipped = 0
        errors = []

        for json_file in json_files:
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)

                # Find the linked requirement
                req_id = data.get("requirement_id")
                requirement = requirements.get(req_id)

                if not requirement:
                    errors.append(f"{json_file.name}: Requirement {req_id} not found")
                    skipped += 1
                    continue

                # Build description with objective and notes
                description_parts = [data["description"]]
                if data.get("objective"):
                    description_parts.append(f"Objective: {data['objective']}")
                if data.get("notes"):
                    description_parts.append(f"Notes: {data['notes']}")

                full_description = "\n".join(description_parts)

                # Create test case
                test_case = TestCase(
                    test_case_id=data["test_case_id"],
                    title=data["title"],
                    description=full_description,
                    requirement_id=requirement.id,
                    test_type=data["test_type"],
                    priority=map_priority(data["priority"]),
                    status=map_status(data["status"]),
                    preconditions=json.dumps(data.get("preconditions", [])),
                    test_steps=json.dumps(data.get("test_steps", [])),
                    expected_results=json.dumps(data.get("expected_results", [])),
                    actual_results=json.dumps(data.get("actual_results")) if data.get("actual_results") else None,
                    test_environment=data.get("environment"),
                    automated=data.get("automated", False),
                    execution_duration=data.get("duration_minutes"),
                    execution_date=data.get("execution_date"),
                    created_by_id=1  # Admin user
                )

                db.add(test_case)
                loaded_count += 1

                if loaded_count % 10 == 0:
                    print(f"   ... loaded {loaded_count} test cases")

            except Exception as e:
                errors.append(f"{json_file.name}: {str(e)}")
                continue

        db.commit()

        print(f"\n✅ Loaded {loaded_count} test cases")
        print(f"⏭️  Skipped {skipped} test cases (requirements not found)")

        if errors:
            print(f"\n⚠️  {len(errors)} errors encountered:")
            for error in errors[:5]:  # Show first 5 errors
                print(f"      - {error}")

        # Verify loaded data
        print("\n📊 Verifying test cases...")
        total_tests = db.query(TestCase).count()
        print(f"   Total test cases in database: {total_tests}")

        # Count by status
        from sqlalchemy import func
        status_counts = db.query(
            TestCase.status, func.count(TestCase.id)
        ).group_by(TestCase.status).all()

        print("\n   Test cases by status:")
        for status, count in status_counts:
            print(f"   - {status.value}: {count}")

        # Test coverage
        reqs_with_tests = db.query(Requirement).filter(
            Requirement.test_cases.any()
        ).count()
        total_reqs = db.query(Requirement).count()
        coverage = (reqs_with_tests / total_reqs * 100) if total_reqs > 0 else 0

        print(f"\n   Test coverage: {reqs_with_tests}/{total_reqs} requirements ({coverage:.1f}%)")

        print("\n" + "="*70)
        print("✅ TEST CASES LOADED SUCCESSFULLY")
        print("="*70)

    except Exception as e:
        print(f"\n❌ Error loading test cases: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise

    finally:
        db.close()

if __name__ == "__main__":
    load_test_cases()
