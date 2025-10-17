#!/usr/bin/env python3
"""
Comprehensive integrity check for synthetic requirements.
"""

import json
from pathlib import Path
from collections import Counter

BASE_PATH = Path("/Users/z/Documents/CALIDUS/synthetic_requirements")

def comprehensive_check():
    """Run comprehensive integrity checks."""
    print("=" * 70)
    print("COMPREHENSIVE INTEGRITY CHECK")
    print("=" * 70)
    print()

    all_req_ids = []
    all_trace_to = []
    all_traced_by = []
    req_types = Counter()
    categories = Counter()

    # Load all requirement files
    requirement_files = []
    for category in ["AHLR", "System", "Technical", "Certification"]:
        category_path = BASE_PATH / category
        if category_path.exists():
            requirement_files.extend(category_path.glob("*.json"))

    print(f"📋 Total requirement files: {len(requirement_files)}")
    print()

    # Analyze each file
    for filepath in requirement_files:
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)

            req_id = data.get("requirement_id")
            all_req_ids.append(req_id)
            req_types[data.get("type")] += 1
            categories[data.get("category")] += 1

            # Collect trace links
            all_trace_to.extend(data.get("traces_to", []))
            all_traced_by.extend(data.get("traced_by", []))

        except Exception as e:
            print(f"❌ Error reading {filepath}: {e}")

    print("✅ Statistics:")
    print(f"   - Total requirements: {len(all_req_ids)}")
    print(f"   - AHLR: {sum(1 for r in all_req_ids if r.startswith('AHLR-'))}")
    print(f"   - SYS: {sum(1 for r in all_req_ids if r.startswith('SYS-'))}")
    print(f"   - TECH: {sum(1 for r in all_req_ids if r.startswith('TECH-'))}")
    print(f"   - CERT: {sum(1 for r in all_req_ids if r.startswith('CERT-'))}")
    print()

    # Check for duplicates
    duplicates = [req_id for req_id, count in Counter(all_req_ids).items() if count > 1]
    if duplicates:
        print(f"❌ Duplicate requirement IDs: {len(duplicates)}")
        for dup in duplicates[:5]:
            print(f"   - {dup}")
    else:
        print("✅ No duplicate requirement IDs")
    print()

    # Check trace integrity
    all_req_ids_set = set(all_req_ids)
    orphaned_traces_to = [t for t in all_trace_to if t and not t.startswith("TC-") and t not in all_req_ids_set]
    orphaned_traced_by = [t for t in all_traced_by if t and not t.startswith("TC-") and t not in all_req_ids_set]

    if orphaned_traces_to:
        print(f"⚠️  Broken 'traces_to' links: {len(set(orphaned_traces_to))}")
        for trace in list(set(orphaned_traces_to))[:5]:
            print(f"   - {trace} (not found)")
    else:
        print("✅ All 'traces_to' links are valid")

    if orphaned_traced_by:
        print(f"⚠️  Broken 'traced_by' links: {len(set(orphaned_traced_by))}")
        for trace in list(set(orphaned_traced_by))[:5]:
            print(f"   - {trace} (not found)")
    else:
        print("✅ All 'traced_by' links are valid")
    print()

    # Check requirement ID sequences
    print("✅ Requirement ID Sequences:")

    ahlr_ids = sorted([int(r.split("-")[1]) for r in all_req_ids if r.startswith("AHLR-")])
    sys_ids = sorted([int(r.split("-")[1]) for r in all_req_ids if r.startswith("SYS-")])
    tech_ids = sorted([int(r.split("-")[1]) for r in all_req_ids if r.startswith("TECH-")])
    cert_ids = sorted([int(r.split("-")[1]) for r in all_req_ids if r.startswith("CERT-")])

    print(f"   - AHLR: {ahlr_ids[0]}-{ahlr_ids[-1]} ({len(ahlr_ids)} requirements)")
    print(f"   - SYS: {sys_ids[0]}-{sys_ids[-1]} ({len(sys_ids)} requirements)")
    print(f"   - TECH: {tech_ids[0]}-{tech_ids[-1]} ({len(tech_ids)} requirements)")
    print(f"   - CERT: {cert_ids[0]}-{cert_ids[-1]} ({len(cert_ids)} requirements)")
    print()

    # Check intentional issues
    print("✅ Intentional Issues (for demo):")
    issues_count = 0
    for filepath in requirement_files:
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            if data.get("issues"):
                issues_count += 1
                print(f"   - {data['requirement_id']}: {data['issues'][0]['type']}")
        except:
            pass

    print(f"\n   Total: {issues_count} requirements with intentional issues")
    print()

    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    if not duplicates and not orphaned_traces_to and not orphaned_traced_by:
        print("🎉 ALL INTEGRITY CHECKS PASSED!")
        print("✅ No duplicates found")
        print("✅ No broken trace links")
        print("✅ All requirement IDs are unique")
        print("✅ Ready for import to CALIDUS")
    else:
        print("⚠️  Some issues found (see above)")
        if duplicates:
            print(f"   - {len(duplicates)} duplicate IDs")
        if orphaned_traces_to:
            print(f"   - {len(set(orphaned_traces_to))} broken 'traces_to'")
        if orphaned_traced_by:
            print(f"   - {len(set(orphaned_traced_by))} broken 'traced_by'")
    print("=" * 70)
    print()

if __name__ == "__main__":
    comprehensive_check()
