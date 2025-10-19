#!/usr/bin/env python3
"""
Load traceability links from the matrix JSON file.
"""
import json
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Requirement, TraceabilityLink, TraceLinkType
from app.config import get_settings

# Database connection
settings = get_settings()
DATABASE_URL = settings.database_url
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def load_traceability_links():
    """Load traceability links from JSON"""
    print("="*70)
    print("🔗 LOADING TRACEABILITY LINKS")
    print("="*70)

    # Load the matrix file
    matrix_file = Path("/app/synthetic_requirements/Traceability/traceability_matrix.json")

    if not matrix_file.exists():
        print(f"❌ Matrix file not found: {matrix_file}")
        return

    with open(matrix_file, 'r') as f:
        data = json.load(f)

    trace_links = data.get("trace_links", [])
    print(f"\n📊 Found {len(trace_links)} trace links in matrix")

    db = SessionLocal()

    try:
        # Get all requirements indexed by requirement_id
        requirements = {req.requirement_id: req for req in db.query(Requirement).all()}
        print(f"📦 {len(requirements)} requirements in database")

        created = 0
        skipped = 0
        errors = []

        for link_data in trace_links:
            ahlr_id = link_data.get("ahlr")
            system_id = link_data.get("system")
            technical_id = link_data.get("technical")
            certification_id = link_data.get("certification")

            # Create AHLR -> System link
            if ahlr_id and system_id:
                ahlr = requirements.get(ahlr_id)
                system = requirements.get(system_id)

                if ahlr and system:
                    link = TraceabilityLink(
                        source_id=system.id,
                        target_id=ahlr.id,
                        link_type=TraceLinkType.DERIVES_FROM,
                        description=f"System {system_id} derives from AHLR {ahlr_id}",
                        created_by_id=1
                    )
                    db.add(link)
                    created += 1
                else:
                    skipped += 1

            # Create System -> Technical link
            if system_id and technical_id:
                system = requirements.get(system_id)
                technical = requirements.get(technical_id)

                if system and technical:
                    link = TraceabilityLink(
                        source_id=technical.id,
                        target_id=system.id,
                        link_type=TraceLinkType.REFINES,
                        description=f"Technical {technical_id} refines System {system_id}",
                        created_by_id=1
                    )
                    db.add(link)
                    created += 1
                else:
                    skipped += 1

            # Create requirement -> Certification link
            if certification_id:
                cert = requirements.get(certification_id)

                # Try to link from system or technical
                source = requirements.get(system_id) or requirements.get(technical_id)

                if source and cert:
                    link = TraceabilityLink(
                        source_id=source.id,
                        target_id=cert.id,
                        link_type=TraceLinkType.VERIFIES,
                        description=f"Verifies certification requirement {certification_id}",
                        created_by_id=1
                    )
                    db.add(link)
                    created += 1
                else:
                    skipped += 1

        db.commit()

        print(f"\n✅ Created {created} traceability links")
        print(f"⏭️  Skipped {skipped} links (requirements not found)")

        # Verify
        total_links = db.query(TraceabilityLink).count()
        print(f"\n📊 Total links in database: {total_links}")

        print("\n" + "="*70)
        print("✅ TRACEABILITY LINKS LOADED")
        print("="*70)

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    load_traceability_links()
