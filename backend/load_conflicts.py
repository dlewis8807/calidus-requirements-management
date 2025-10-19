#!/usr/bin/env python3
"""
Add requirement conflicts to the synthetic data.
Creates explicit conflicts, priority inconsistencies, and potential duplicates.
"""
import random
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import (
    Requirement, TraceabilityLink, TraceLinkType,
    RequirementType, RequirementPriority, RequirementStatus, VerificationMethod
)
from app.config import get_settings

# Database connection
settings = get_settings()
DATABASE_URL = settings.database_url
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


def add_explicit_conflicts():
    """
    Add explicit conflict traceability links between requirements.
    These show up as "High Severity" conflicts.
    """
    db = SessionLocal()
    try:
        print("\n1️⃣  Adding Explicit Conflicts...")

        # Get some approved requirements that could conflict
        autopilot_reqs = db.query(Requirement).filter(
            Requirement.category == "AutoPilot",
            Requirement.status == RequirementStatus.APPROVED
        ).limit(10).all()

        avionics_reqs = db.query(Requirement).filter(
            Requirement.category == "Avionics",
            Requirement.status == RequirementStatus.APPROVED
        ).limit(10).all()

        communication_reqs = db.query(Requirement).filter(
            Requirement.category == "Communication",
            Requirement.status == RequirementStatus.APPROVED
        ).limit(5).all()

        conflicts_created = 0

        # Create conflicts between autopilot requirements
        if len(autopilot_reqs) >= 2:
            # Conflict 1: Autopilot mode conflict
            link1 = TraceabilityLink(
                source_id=autopilot_reqs[0].id,
                target_id=autopilot_reqs[1].id,
                link_type=TraceLinkType.CONFLICTS_WITH,
                description=f"Requirements {autopilot_reqs[0].requirement_id} and {autopilot_reqs[1].requirement_id} specify conflicting autopilot engagement modes. One requires manual confirmation while the other allows automatic engagement.",
                rationale="Detected during integration testing - requires design review",
                created_by_id=1
            )
            db.add(link1)
            conflicts_created += 1

        if len(autopilot_reqs) >= 4:
            # Conflict 2: Control authority conflict
            link2 = TraceabilityLink(
                source_id=autopilot_reqs[2].id,
                target_id=autopilot_reqs[3].id,
                link_type=TraceLinkType.CONFLICTS_WITH,
                description=f"Requirements {autopilot_reqs[2].requirement_id} and {autopilot_reqs[3].requirement_id} define incompatible control authority limits. Maximum deflection angles overlap causing control ambiguity.",
                rationale="Identified during flight dynamics analysis",
                created_by_id=1
            )
            db.add(link2)
            conflicts_created += 1

        if len(autopilot_reqs) >= 6:
            # Conflict 3: Sensor input conflict
            link3 = TraceabilityLink(
                source_id=autopilot_reqs[4].id,
                target_id=autopilot_reqs[5].id,
                link_type=TraceLinkType.CONFLICTS_WITH,
                description=f"Requirements {autopilot_reqs[4].requirement_id} and {autopilot_reqs[5].requirement_id} specify different sensor data sources for the same flight parameter, creating potential data inconsistency.",
                rationale="Flagged during software architecture review",
                created_by_id=1
            )
            db.add(link3)
            conflicts_created += 1

        if len(avionics_reqs) >= 2:
            # Conflict 4: Display refresh rate conflict
            link4 = TraceabilityLink(
                source_id=avionics_reqs[0].id,
                target_id=avionics_reqs[1].id,
                link_type=TraceLinkType.CONFLICTS_WITH,
                description=f"Requirements {avionics_reqs[0].requirement_id} and {avionics_reqs[1].requirement_id} define conflicting display refresh rates. Different update frequencies specified for same primary flight display.",
                rationale="Requires avionics system integration review",
                created_by_id=1
            )
            db.add(link4)
            conflicts_created += 1

        if len(avionics_reqs) >= 4:
            # Conflict 5: Navigation data priority
            link5 = TraceabilityLink(
                source_id=avionics_reqs[2].id,
                target_id=avionics_reqs[3].id,
                link_type=TraceLinkType.CONFLICTS_WITH,
                description=f"Requirements {avionics_reqs[2].requirement_id} and {avionics_reqs[3].requirement_id} specify conflicting navigation data source priorities for GPS vs ILS approach modes.",
                rationale="Flight management system logic conflict",
                created_by_id=1
            )
            db.add(link5)
            conflicts_created += 1

        if len(communication_reqs) >= 2:
            # Conflict 6: Radio frequency conflict
            link6 = TraceabilityLink(
                source_id=communication_reqs[0].id,
                target_id=communication_reqs[1].id,
                link_type=TraceLinkType.CONFLICTS_WITH,
                description=f"Requirements {communication_reqs[0].requirement_id} and {communication_reqs[1].requirement_id} specify overlapping radio frequency bands that would cause interference.",
                rationale="Radio spectrum allocation conflict",
                created_by_id=1
            )
            db.add(link6)
            conflicts_created += 1

        if len(autopilot_reqs) >= 8 and len(avionics_reqs) >= 6:
            # Conflict 7: Cross-system conflict (autopilot vs avionics)
            link7 = TraceabilityLink(
                source_id=autopilot_reqs[6].id,
                target_id=avionics_reqs[4].id,
                link_type=TraceLinkType.CONFLICTS_WITH,
                description=f"Autopilot requirement {autopilot_reqs[6].requirement_id} demands faster response times than avionics requirement {avionics_reqs[4].requirement_id} can safely support with current processing capability.",
                rationale="Cross-system compatibility issue - needs systems engineering coordination",
                created_by_id=1
            )
            db.add(link7)
            conflicts_created += 1

        if len(autopilot_reqs) >= 10 and len(communication_reqs) >= 4:
            # Conflict 8: Autopilot vs Communication bandwidth
            link8 = TraceabilityLink(
                source_id=autopilot_reqs[8].id,
                target_id=communication_reqs[3].id,
                link_type=TraceLinkType.CONFLICTS_WITH,
                description=f"Autopilot telemetry requirement {autopilot_reqs[8].requirement_id} requires more data bandwidth than communication requirement {communication_reqs[3].requirement_id} allocates for autopilot subsystem.",
                rationale="Data bus bandwidth allocation conflict",
                created_by_id=1
            )
            db.add(link8)
            conflicts_created += 1

        db.commit()
        print(f"   ✅ Created {conflicts_created} explicit conflicts")
        return conflicts_created

    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


def add_priority_inconsistencies():
    """
    Modify requirements to create priority inconsistencies.
    Same category + same verification method but different priorities.
    """
    db = SessionLocal()
    try:
        print("\n2️⃣  Creating Priority Inconsistencies...")

        # Get requirements by category (using actual categories from database)
        categories = ["AutoPilot", "Avionics", "Communication", "Electrical", "Propulsion"]
        inconsistencies_created = 0

        for category in categories:
            # Get approved requirements in this category
            reqs = db.query(Requirement).filter(
                Requirement.category == category,
                Requirement.status == RequirementStatus.APPROVED
            ).limit(8).all()

            if len(reqs) >= 6:
                # Set same verification method but different priorities
                # This creates an inconsistency that the endpoint will detect
                reqs[0].verification_method = VerificationMethod.TEST
                reqs[0].priority = RequirementPriority.CRITICAL

                reqs[1].verification_method = VerificationMethod.TEST
                reqs[1].priority = RequirementPriority.HIGH

                reqs[2].verification_method = VerificationMethod.TEST
                reqs[2].priority = RequirementPriority.MEDIUM

                reqs[3].verification_method = VerificationMethod.TEST
                reqs[3].priority = RequirementPriority.LOW

                reqs[4].verification_method = VerificationMethod.ANALYSIS
                reqs[4].priority = RequirementPriority.CRITICAL

                reqs[5].verification_method = VerificationMethod.ANALYSIS
                reqs[5].priority = RequirementPriority.HIGH

                if len(reqs) >= 8:
                    reqs[6].verification_method = VerificationMethod.ANALYSIS
                    reqs[6].priority = RequirementPriority.MEDIUM

                    reqs[7].verification_method = VerificationMethod.ANALYSIS
                    reqs[7].priority = RequirementPriority.LOW

                inconsistencies_created += 1

        db.commit()
        print(f"   ✅ Created priority inconsistencies in {inconsistencies_created} categories")
        return inconsistencies_created

    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


def add_potential_duplicates():
    """
    Create requirements with similar titles to trigger duplicate detection.
    The endpoint looks for matching first 50 characters.
    """
    db = SessionLocal()
    try:
        print("\n3️⃣  Adding Potential Duplicate Requirements...")

        duplicates_created = 0

        # Duplicate group 1: Maximum takeoff weight requirements
        base_req1 = db.query(Requirement).filter(
            Requirement.type == RequirementType.SYSTEM
        ).first()

        if base_req1:
            # Create 3 requirements with similar titles about takeoff weight
            for i in range(3):
                dup = Requirement(
                    requirement_id=f"DUP-MTOW-{i+1:03d}",
                    title="Maximum takeoff weight shall not exceed 12,500 lbs for certification compliance",
                    description=f"Version {i+1}: This requirement ensures the aircraft remains within Part 23 weight limits. Maximum takeoff weight is a critical certification parameter.",
                    type=RequirementType.CERTIFICATION,
                    category="Weight and Balance",
                    priority=RequirementPriority.CRITICAL,
                    status=RequirementStatus.APPROVED,
                    verification_method=VerificationMethod.ANALYSIS,
                    regulatory_document="14 CFR Part 23",
                    regulatory_section="§23.2005",
                    version="1.0",
                    created_by_id=1
                )
                db.add(dup)
            duplicates_created += 3

        # Duplicate group 2: Stall speed requirements
        for i in range(4):
            dup = Requirement(
                requirement_id=f"DUP-VS0-{i+1:03d}",
                title="Stall speed in landing configuration shall not exceed 61 knots CAS",
                description=f"Variant {i+1}: The aircraft shall demonstrate a stall speed (VS0) not exceeding 61 KCAS in the landing configuration to meet Part 23 performance requirements.",
                type=RequirementType.TECHNICAL,
                category="Aerodynamics",
                priority=RequirementPriority.CRITICAL,
                status=RequirementStatus.APPROVED,
                verification_method=VerificationMethod.TEST,
                regulatory_document="14 CFR Part 23",
                regulatory_section="§23.2110",
                version="1.0",
                created_by_id=1
            )
            db.add(dup)
        duplicates_created += 4

        # Duplicate group 3: Fuel system requirements
        for i in range(3):
            dup = Requirement(
                requirement_id=f"DUP-FUEL-{i+1:03d}",
                title="Fuel system shall prevent vapor lock at altitudes up to 25,000 feet",
                description=f"Alternative specification {i+1}: The fuel system design must prevent vapor lock formation at operating altitudes up to 25,000 feet MSL under all environmental conditions.",
                type=RequirementType.SYSTEM,
                category="Propulsion Systems",
                priority=RequirementPriority.HIGH,
                status=RequirementStatus.UNDER_REVIEW,
                verification_method=VerificationMethod.TEST,
                regulatory_document="14 CFR Part 23",
                regulatory_section="§23.2420",
                version="1.0",
                created_by_id=1
            )
            db.add(dup)
        duplicates_created += 3

        # Duplicate group 4: Emergency exit requirements
        for i in range(2):
            dup = Requirement(
                requirement_id=f"DUP-EXIT-{i+1:03d}",
                title="Emergency exits shall be accessible within 5 seconds from any passenger seat",
                description=f"Iteration {i+1}: All emergency exits must be reachable and operable within 5 seconds from any passenger or crew position for emergency evacuation compliance.",
                type=RequirementType.CERTIFICATION,
                category="Safety Systems",
                priority=RequirementPriority.CRITICAL,
                status=RequirementStatus.APPROVED,
                verification_method=VerificationMethod.DEMONSTRATION,
                regulatory_document="14 CFR Part 23",
                regulatory_section="§23.2310",
                version="1.0",
                created_by_id=1
            )
            db.add(dup)
        duplicates_created += 2

        # Duplicate group 5: Electrical load requirements
        for i in range(3):
            dup = Requirement(
                requirement_id=f"DUP-ELEC-{i+1:03d}",
                title="Electrical system shall support continuous load of 150 amperes minimum",
                description=f"Revision {i+1}: The aircraft electrical system must provide continuous power output of at least 150 amperes to support all avionics and essential systems.",
                type=RequirementType.TECHNICAL,
                category="Electrical Systems",
                priority=RequirementPriority.HIGH,
                status=RequirementStatus.APPROVED,
                verification_method=VerificationMethod.TEST,
                regulatory_document="14 CFR Part 23",
                regulatory_section="§23.2435",
                version="1.0",
                created_by_id=1
            )
            db.add(dup)
        duplicates_created += 3

        db.commit()
        print(f"   ✅ Created {duplicates_created} potential duplicate requirements in 5 groups")
        return duplicates_created

    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


def main():
    """Main function to add all conflicts"""
    print("=" * 70)
    print("⚠️  ADDING REQUIREMENT CONFLICTS TO SYNTHETIC DATA")
    print("=" * 70)

    try:
        # Add explicit conflicts
        explicit = add_explicit_conflicts()

        # Add priority inconsistencies
        priority = add_priority_inconsistencies()

        # Add potential duplicates
        duplicates = add_potential_duplicates()

        print("\n" + "=" * 70)
        print("✅ CONFLICTS SUCCESSFULLY ADDED")
        print("=" * 70)
        print(f"\n📊 Summary:")
        print(f"   • Explicit Conflicts: {explicit}")
        print(f"   • Priority Inconsistency Groups: {priority}")
        print(f"   • Potential Duplicates: {duplicates}")
        print(f"\n🌐 View at: http://localhost:3000/dashboard/conflicts")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ Failed to add conflicts: {str(e)}")
        raise


if __name__ == "__main__":
    main()
