"""
Sample Data Generator for Week 2
Generates 15,000+ requirements with traceability links and test cases.
"""
import random
import sys
from pathlib import Path
from datetime import datetime, timedelta
from faker import Faker

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models import (
    User, Requirement, TestCase, TraceabilityLink,
    RequirementType, RequirementStatus, RequirementPriority, VerificationMethod,
    TestCaseStatus, TestCasePriority, TraceLinkType
)

fake = Faker()

# ============================================================================
# Configuration
# ============================================================================

# Target counts (to exceed 15,000 requirements)
AHLR_COUNT = 500          # Aircraft High-Level Requirements
SYSTEM_COUNT = 5000       # System Requirements (10 per AHLR)
TECHNICAL_COUNT = 10000   # Technical Specifications (2 per System)
CERTIFICATION_COUNT = 1000  # Certification Requirements

TOTAL_REQUIREMENTS = AHLR_COUNT + SYSTEM_COUNT + TECHNICAL_COUNT + CERTIFICATION_COUNT  # 16,500

# Test case generation rate (not all requirements need tests)
TEST_CASE_PROBABILITY = 0.7  # 70% of requirements will have test cases
AVG_TESTS_PER_REQUIREMENT = 2

# Categories for requirements
CATEGORIES = [
    "FlightControl", "Navigation", "Propulsion", "Avionics", "Communication",
    "Safety", "FuelSystem", "LandingGear", "Electrical", "Hydraulic",
    "Environmental", "Instrumentation", "AutoPilot", "WeatherRadar", "TCAS"
]

# Regulatory documents
REGULATORY_DOCS = [
    ("14 CFR Part 23", "§23.143", 23),
    ("14 CFR Part 23", "§23.145", 45),
    ("14 CFR Part 23", "§23.147", 67),
    ("14 CFR Part 25", "§25.101", 12),
    ("14 CFR Part 25", "§25.103", 34),
    ("EASA CS-23", "CS 23.143", 56),
    ("EASA CS-25", "CS 25.101", 78),
]


# ============================================================================
# Data Generation Functions
# ============================================================================

def create_admin_user(db: Session) -> User:
    """Create or get admin user for data generation"""
    admin = db.query(User).filter(User.username == "admin").first()
    if not admin:
        from app.core.security import get_password_hash
        admin = User(
            username="admin",
            email="admin@calidus.aero",
            hashed_password=get_password_hash("Admin123!"),
            role="admin",
            full_name="System Administrator"
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
    return admin


def generate_requirement_description(req_type: RequirementType, category: str) -> str:
    """Generate realistic requirement description"""
    shall_statements = [
        f"The {category} system SHALL provide {fake.catch_phrase().lower()}",
        f"The aircraft SHALL maintain {fake.catch_phrase().lower()} during {category.lower()} operations",
        f"The {category} subsystem SHALL ensure {fake.catch_phrase().lower()}",
        f"The system SHALL monitor {category.lower()} parameters and {fake.catch_phrase().lower()}",
        f"The {category} SHALL be capable of {fake.catch_phrase().lower()}",
    ]
    return random.choice(shall_statements)


def generate_ahlr_requirements(db: Session, user: User, count: int) -> list:
    """Generate Aircraft High-Level Requirements"""
    print(f"Generating {count} AHLR requirements...")
    ahlrs = []

    for i in range(1, count + 1):
        category = random.choice(CATEGORIES)
        doc, section, page = random.choice(REGULATORY_DOCS)

        req = Requirement(
            requirement_id=f"AHLR-{i:04d}",
            type=RequirementType.AHLR,
            category=category,
            title=f"{category} High-Level Requirement {i}",
            description=generate_requirement_description(RequirementType.AHLR, category),
            priority=random.choice(list(RequirementPriority)),
            status=random.choices(
                list(RequirementStatus),
                weights=[10, 70, 5, 15]  # Most approved, some draft, few deprecated/under review
            )[0],
            verification_method=random.choice(list(VerificationMethod)),
            regulatory_document=doc,
            regulatory_section=section,
            regulatory_page=page,
            file_path=f"/rawdata/{doc.replace(' ', '_')}.pdf",
            version="1.0",
            created_by_id=user.id,
            created_at=datetime.utcnow() - timedelta(days=random.randint(180, 365))
        )
        ahlrs.append(req)

        if i % 100 == 0:
            print(f"  Generated {i}/{count} AHLR requirements")

    db.add_all(ahlrs)
    db.commit()
    print(f"✓ Created {count} AHLR requirements")
    return ahlrs


def generate_system_requirements(db: Session, user: User, ahlrs: list, count: int) -> list:
    """Generate System Requirements (derived from AHLRs)"""
    print(f"Generating {count} System requirements...")
    system_reqs = []

    for i in range(1, count + 1):
        # Link to parent AHLR
        parent_ahlr = random.choice(ahlrs)

        req = Requirement(
            requirement_id=f"SYS-{i:05d}",
            type=RequirementType.SYSTEM,
            category=parent_ahlr.category,
            title=f"{parent_ahlr.category} System Requirement {i}",
            description=generate_requirement_description(RequirementType.SYSTEM, parent_ahlr.category),
            priority=parent_ahlr.priority,
            status=random.choices(
                list(RequirementStatus),
                weights=[5, 75, 3, 17]
            )[0],
            verification_method=random.choice(list(VerificationMethod)),
            version="1.0",
            created_by_id=user.id,
            created_at=datetime.utcnow() - timedelta(days=random.randint(90, 180))
        )
        system_reqs.append(req)

        if i % 500 == 0:
            print(f"  Generated {i}/{count} System requirements")

    db.add_all(system_reqs)
    db.commit()

    # Create traceability links (System -> AHLR)
    print("  Creating AHLR → System traceability links...")
    trace_links = []
    for sys_req in system_reqs:
        parent_ahlr = random.choice(ahlrs)
        link = TraceabilityLink(
            source_id=sys_req.id,
            target_id=parent_ahlr.id,
            link_type=TraceLinkType.DERIVES_FROM,
            description=f"{sys_req.requirement_id} derives from {parent_ahlr.requirement_id}",
            created_by_id=user.id
        )
        trace_links.append(link)

    db.add_all(trace_links)
    db.commit()
    print(f"✓ Created {count} System requirements with traceability")
    return system_reqs


def generate_technical_requirements(db: Session, user: User, system_reqs: list, count: int) -> list:
    """Generate Technical Specifications (derived from System)"""
    print(f"Generating {count} Technical requirements...")
    technical_reqs = []

    for i in range(1, count + 1):
        parent_sys = random.choice(system_reqs)

        req = Requirement(
            requirement_id=f"TECH-{i:05d}",
            type=RequirementType.TECHNICAL,
            category=parent_sys.category,
            title=f"{parent_sys.category} Technical Specification {i}",
            description=generate_requirement_description(RequirementType.TECHNICAL, parent_sys.category),
            priority=parent_sys.priority,
            status=random.choices(
                list(RequirementStatus),
                weights=[15, 65, 5, 15]
            )[0],
            verification_method=random.choice(list(VerificationMethod)),
            version="1.0",
            created_by_id=user.id,
            created_at=datetime.utcnow() - timedelta(days=random.randint(30, 90))
        )
        technical_reqs.append(req)

        if i % 1000 == 0:
            print(f"  Generated {i}/{count} Technical requirements")

    db.add_all(technical_reqs)
    db.commit()

    # Create traceability links (Technical -> System)
    print("  Creating System → Technical traceability links...")
    trace_links = []
    for tech_req in technical_reqs:
        parent_sys = random.choice(system_reqs)
        link = TraceabilityLink(
            source_id=tech_req.id,
            target_id=parent_sys.id,
            link_type=random.choice([TraceLinkType.DERIVES_FROM, TraceLinkType.REFINES]),
            description=f"{tech_req.requirement_id} refines {parent_sys.requirement_id}",
            created_by_id=user.id
        )
        trace_links.append(link)

    db.add_all(trace_links)
    db.commit()
    print(f"✓ Created {count} Technical requirements with traceability")
    return technical_reqs


def generate_certification_requirements(db: Session, user: User, count: int) -> list:
    """Generate Certification Requirements"""
    print(f"Generating {count} Certification requirements...")
    cert_reqs = []

    for i in range(1, count + 1):
        category = random.choice(CATEGORIES)
        doc, section, page = random.choice(REGULATORY_DOCS)

        req = Requirement(
            requirement_id=f"CERT-{i:04d}",
            type=RequirementType.CERTIFICATION,
            category=category,
            title=f"Certification Requirement {doc} {section}",
            description=f"The aircraft SHALL comply with {doc} {section} requirements for {category.lower()}",
            priority=RequirementPriority.CRITICAL,
            status=RequirementStatus.APPROVED,
            verification_method=VerificationMethod.INSPECTION,
            regulatory_document=doc,
            regulatory_section=section,
            regulatory_page=page,
            file_path=f"/rawdata/{doc.replace(' ', '_')}.pdf",
            version="1.0",
            created_by_id=user.id,
            created_at=datetime.utcnow() - timedelta(days=random.randint(365, 730))
        )
        cert_reqs.append(req)

        if i % 100 == 0:
            print(f"  Generated {i}/{count} Certification requirements")

    db.add_all(cert_reqs)
    db.commit()
    print(f"✓ Created {count} Certification requirements")
    return cert_reqs


def generate_test_cases(db: Session, user: User, all_requirements: list) -> None:
    """Generate test cases for requirements"""
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
                    created_by_id=user.id,
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
                    print(f"  Generated {test_count} test cases...")

    db.add_all(test_cases)
    db.commit()
    print(f"✓ Created {test_count} test cases")


# ============================================================================
# Main Generation Function
# ============================================================================

def generate_all_data():
    """Generate all sample data"""
    print("=" * 70)
    print("CALIDUS Sample Data Generator - Week 2")
    print("=" * 70)
    print(f"Target: {TOTAL_REQUIREMENTS:,} requirements")
    print(f"  - AHLR: {AHLR_COUNT:,}")
    print(f"  - System: {SYSTEM_COUNT:,}")
    print(f"  - Technical: {TECHNICAL_COUNT:,}")
    print(f"  - Certification: {CERTIFICATION_COUNT:,}")
    print("=" * 70)

    db = SessionLocal()

    try:
        # Create admin user
        print("\n1. Creating admin user...")
        admin_user = create_admin_user(db)
        print(f"✓ Admin user: {admin_user.username}")

        # Generate requirements hierarchy
        print("\n2. Generating requirements...")
        ahlrs = generate_ahlr_requirements(db, admin_user, AHLR_COUNT)
        system_reqs = generate_system_requirements(db, admin_user, ahlrs, SYSTEM_COUNT)
        technical_reqs = generate_technical_requirements(db, admin_user, system_reqs, TECHNICAL_COUNT)
        cert_reqs = generate_certification_requirements(db, admin_user, CERTIFICATION_COUNT)

        all_requirements = ahlrs + system_reqs + technical_reqs + cert_reqs

        # Generate test cases
        print("\n3. Generating test cases...")
        generate_test_cases(db, admin_user, all_requirements)

        # Final statistics
        print("\n" + "=" * 70)
        print("✓ Data Generation Complete!")
        print("=" * 70)
        total_reqs = db.query(Requirement).count()
        total_tests = db.query(TestCase).count()
        total_traces = db.query(TraceabilityLink).count()

        print(f"Total Requirements: {total_reqs:,}")
        print(f"Total Test Cases: {total_tests:,}")
        print(f"Total Traceability Links: {total_traces:,}")
        print("=" * 70)

    except Exception as e:
        print(f"\n✗ Error during data generation: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    generate_all_data()
