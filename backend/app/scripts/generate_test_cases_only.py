"""
Generate Test Cases Only
Generates test cases for existing requirements.
"""
import random
import sys
from pathlib import Path
from datetime import datetime, timedelta
from faker import Faker

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import (
    User, Requirement, TestCase,
    TestCaseStatus, TestCasePriority
)

fake = Faker()

# Test case generation rate
TEST_CASE_PROBABILITY = 0.7  # 70% of requirements will have test cases
AVG_TESTS_PER_REQUIREMENT = 2


def generate_test_cases():
    """Generate test cases for all existing requirements"""
    print("=" * 70)
    print("CALIDUS Test Case Generator")
    print("=" * 70)

    db = SessionLocal()

    try:
        # Get admin user
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            print("✗ Admin user not found!")
            return

        # Get all requirements
        all_requirements = db.query(Requirement).all()
        print(f"Found {len(all_requirements):,} requirements")

        # Generate test cases
        print("Generating test cases...")
        test_cases = []
        test_count = 0

        for req in all_requirements:
            # Determine if this requirement should have tests
            if random.random() < TEST_CASE_PROBABILITY:
                num_tests = random.randint(1, AVG_TESTS_PER_REQUIREMENT * 2)

                for i in range(num_tests):
                    test_count += 1
                    tc = TestCase(
                        test_case_id=f"TC-{test_count:06d}",
                        title=f"Verify {req.requirement_id}: {req.title[:50]}",
                        description=f"Test case to verify requirement {req.requirement_id}",
                        test_steps=f"1. Setup test environment\\n2. Execute test for {req.category}\\n3. Verify results\\n4. Document findings",
                        expected_results=f"System meets {req.requirement_id} specification",
                        status=random.choices(
                            list(TestCaseStatus),
                            weights=[20, 50, 10, 5, 15]  # pending, passed, failed, blocked, in_progress
                        )[0],
                        priority=random.choice(list(TestCasePriority)),
                        automated=random.random() < 0.3,  # 30% automated
                        test_type=random.choice(["unit", "integration", "system", "acceptance"]),
                        test_environment=random.choice(["dev", "staging", "production"]),
                        requirement_id=req.id,
                        created_by_id=admin.id,
                        created_at=datetime.utcnow() - timedelta(days=random.randint(1, 60))
                    )

                    # Add execution details for passed/failed tests
                    if tc.status in [TestCaseStatus.PASSED, TestCaseStatus.FAILED]:
                        tc.execution_date = datetime.utcnow() - timedelta(days=random.randint(1, 30))
                        tc.execution_duration = random.randint(60, 3600)  # 1 min to 1 hour
                        tc.executed_by = "automated" if tc.automated else fake.name()
                        tc.actual_results = "Test passed successfully" if tc.status == TestCaseStatus.PASSED else "Test failed - see logs"

                    test_cases.append(tc)

                    if test_count % 1000 == 0:
                        print(f"  Generated {test_count:,} test cases...")
                        # Commit in batches to avoid memory issues
                        db.add_all(test_cases)
                        db.commit()
                        test_cases = []

        # Commit remaining test cases
        if test_cases:
            db.add_all(test_cases)
            db.commit()

        print(f"✓ Created {test_count:,} test cases")

        # Final statistics
        print("\n" + "=" * 70)
        print("✓ Test Case Generation Complete!")
        print("=" * 70)
        total_tests = db.query(TestCase).count()
        print(f"Total Test Cases: {total_tests:,}")
        print("=" * 70)

    except Exception as e:
        print(f"\n✗ Error during test case generation: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    generate_test_cases()
