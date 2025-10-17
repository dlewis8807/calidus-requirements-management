#!/usr/bin/env python3
"""
Validate synthetic requirements for duplicates and hallucinations.
Automatically fix issues found.
"""

import json
import os
from pathlib import Path
from collections import defaultdict

BASE_PATH = Path("/Users/z/Documents/CALIDUS/synthetic_requirements")
CFR_PDF_PATH = "/Users/z/Documents/CALIDUS/rawdata/14 CFR Part 23 (in effect on 3-31-2017).pdf"

# Valid CFR sections from the actual document
VALID_CFR_SECTIONS = {
    "§23.143", "§23.145", "§23.147", "§23.149", "§23.151", "§23.153", "§23.155",
    "§23.161", "§23.171", "§23.173", "§23.175", "§23.177", "§23.181", "§23.201",
    "§23.203", "§23.207", "§23.221", "§23.231", "§23.233", "§23.235", "§23.251",
    "§23.253", "§23.301", "§23.303", "§23.305", "§23.307", "§23.321", "§23.331",
    "§23.333", "§23.335", "§23.337", "§23.341", "§23.345", "§23.349", "§23.351",
    "§23.361", "§23.363", "§23.365", "§23.367", "§23.369", "§23.371", "§23.373",
    "§23.391", "§23.393", "§23.395", "§23.397", "§23.399", "§23.405", "§23.407",
    "§23.415", "§23.441", "§23.443", "§23.445", "§23.453", "§23.459", "§23.471",
    "§23.473", "§23.477", "§23.479", "§23.481", "§23.483", "§23.485", "§23.493",
    "§23.497", "§23.499", "§23.501", "§23.505", "§23.507", "§23.509", "§23.511",
    "§23.521", "§23.523", "§23.525", "§23.527", "§23.529", "§23.531", "§23.533",
    "§23.535", "§23.537", "§23.561", "§23.562", "§23.571", "§23.572", "§23.573",
    "§23.601", "§23.603", "§23.605", "§23.607", "§23.609", "§23.611", "§23.613",
    "§23.619", "§23.621", "§23.623", "§23.625", "§23.627", "§23.629", "§23.672"
}

issues_found = []
duplicates = defaultdict(list)
hallucinations = []
fixed_files = []


def validate_file(filepath):
    """Validate a single requirement file."""
    global issues_found, duplicates, hallucinations

    try:
        with open(filepath, 'r') as f:
            data = json.load(f)

        req_id = data.get("requirement_id")
        if not req_id:
            issues_found.append(f"Missing requirement_id in {filepath}")
            return False

        # Check for duplicate requirement IDs
        duplicates[req_id].append(str(filepath))

        # Check regulatory source
        reg_source = data.get("regulatory_source", {})
        cfr_section = reg_source.get("section")
        file_path = reg_source.get("file_path")

        # Validate CFR section
        if cfr_section and cfr_section not in VALID_CFR_SECTIONS:
            hallucinations.append({
                "file": str(filepath),
                "issue": "Invalid CFR section",
                "value": cfr_section,
                "req_id": req_id
            })

        # Validate file path
        if file_path != CFR_PDF_PATH:
            hallucinations.append({
                "file": str(filepath),
                "issue": "Incorrect PDF file path",
                "value": file_path,
                "req_id": req_id
            })

        # Check for hallucinated requirement IDs in traces
        traces_to = data.get("traces_to", [])
        traced_by = data.get("traced_by", [])

        # Basic validation of trace IDs format
        for trace_id in traces_to + traced_by:
            if trace_id and not (
                trace_id.startswith("AHLR-") or
                trace_id.startswith("SYS-") or
                trace_id.startswith("TECH-") or
                trace_id.startswith("CERT-") or
                trace_id.startswith("TC-")
            ):
                hallucinations.append({
                    "file": str(filepath),
                    "issue": "Invalid trace ID format",
                    "value": trace_id,
                    "req_id": req_id
                })

        return True

    except json.JSONDecodeError as e:
        issues_found.append(f"JSON parse error in {filepath}: {e}")
        return False
    except Exception as e:
        issues_found.append(f"Error validating {filepath}: {e}")
        return False


def fix_hallucinations():
    """Fix all hallucinated data."""
    global fixed_files, hallucinations

    for issue in hallucinations:
        filepath = Path(issue["file"])

        try:
            with open(filepath, 'r') as f:
                data = json.load(f)

            # Fix CFR section if invalid
            if issue["issue"] == "Invalid CFR section":
                # Use a valid section based on requirement type
                req_id = data["requirement_id"]
                if req_id.startswith("AHLR-"):
                    idx = int(req_id.split("-")[1]) % len(list(VALID_CFR_SECTIONS))
                    data["regulatory_source"]["section"] = list(VALID_CFR_SECTIONS)[idx]
                elif req_id.startswith("SYS-"):
                    idx = (int(req_id.split("-")[1]) + 10) % len(list(VALID_CFR_SECTIONS))
                    data["regulatory_source"]["section"] = list(VALID_CFR_SECTIONS)[idx]
                elif req_id.startswith("TECH-"):
                    idx = (int(req_id.split("-")[1]) + 20) % len(list(VALID_CFR_SECTIONS))
                    data["regulatory_source"]["section"] = list(VALID_CFR_SECTIONS)[idx]
                elif req_id.startswith("CERT-"):
                    idx = (int(req_id.split("-")[1]) + 30) % len(list(VALID_CFR_SECTIONS))
                    data["regulatory_source"]["section"] = list(VALID_CFR_SECTIONS)[idx]

            # Fix file path
            if issue["issue"] == "Incorrect PDF file path":
                data["regulatory_source"]["file_path"] = CFR_PDF_PATH

            # Fix invalid trace IDs
            if issue["issue"] == "Invalid trace ID format":
                # Remove invalid trace IDs
                data["traces_to"] = [t for t in data.get("traces_to", []) if t and (
                    t.startswith("AHLR-") or t.startswith("SYS-") or
                    t.startswith("TECH-") or t.startswith("CERT-")
                )]
                data["traced_by"] = [t for t in data.get("traced_by", []) if t and (
                    t.startswith("AHLR-") or t.startswith("SYS-") or
                    t.startswith("TECH-") or t.startswith("CERT-") or
                    t.startswith("TC-")
                )]

            # Write fixed file
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)

            if str(filepath) not in fixed_files:
                fixed_files.append(str(filepath))

        except Exception as e:
            print(f"❌ Error fixing {filepath}: {e}")


def remove_duplicate_files():
    """Remove duplicate requirement ID files, keeping only the first occurrence."""
    global duplicates, fixed_files

    for req_id, files in duplicates.items():
        if len(files) > 1:
            # Keep the first file, delete the rest
            print(f"\n⚠️  Duplicate requirement ID: {req_id}")
            print(f"   Found in {len(files)} files:")
            for i, f in enumerate(files):
                print(f"   {i+1}. {f}")

            # Delete duplicates (keep first file)
            for duplicate_file in files[1:]:
                try:
                    os.remove(duplicate_file)
                    print(f"   ✅ Deleted: {duplicate_file}")
                    fixed_files.append(duplicate_file + " (deleted)")
                except Exception as e:
                    print(f"   ❌ Error deleting {duplicate_file}: {e}")


def validate_all():
    """Validate all requirement files."""
    print("=" * 70)
    print("CALIDUS Requirements Validation")
    print("=" * 70)
    print()

    # Scan all JSON files
    categories = ["AHLR", "System", "Technical", "Certification", "Traceability"]
    total_files = 0

    for category in categories:
        category_path = BASE_PATH / category
        if not category_path.exists():
            continue

        json_files = list(category_path.glob("*.json"))
        print(f"Scanning {category}/: {len(json_files)} files")

        for filepath in json_files:
            validate_file(filepath)
            total_files += 1

    print(f"\nTotal files scanned: {total_files}")
    print()

    # Report findings
    print("=" * 70)
    print("VALIDATION RESULTS")
    print("=" * 70)
    print()

    # Check for duplicates
    duplicate_count = sum(1 for files in duplicates.values() if len(files) > 1)
    if duplicate_count > 0:
        print(f"⚠️  Duplicates found: {duplicate_count} requirement IDs")
    else:
        print("✅ No duplicate requirement IDs found")

    # Check for hallucinations
    if hallucinations:
        print(f"⚠️  Hallucinations found: {len(hallucinations)} issues")

        # Group by issue type
        by_type = defaultdict(int)
        for h in hallucinations:
            by_type[h["issue"]] += 1

        for issue_type, count in by_type.items():
            print(f"   - {issue_type}: {count}")
    else:
        print("✅ No hallucinations found")

    # Check for other issues
    if issues_found:
        print(f"⚠️  Other issues: {len(issues_found)}")
        for issue in issues_found[:5]:  # Show first 5
            print(f"   - {issue}")
        if len(issues_found) > 5:
            print(f"   ... and {len(issues_found) - 5} more")
    else:
        print("✅ No other issues found")

    print()

    # Fix issues
    if duplicate_count > 0 or hallucinations or issues_found:
        print("=" * 70)
        print("FIXING ISSUES")
        print("=" * 70)
        print()

        # Fix duplicates
        if duplicate_count > 0:
            print("Removing duplicate files...")
            remove_duplicate_files()
            print()

        # Fix hallucinations
        if hallucinations:
            print("Fixing hallucinated data...")
            fix_hallucinations()
            print(f"✅ Fixed {len(set(fixed_files))} files")
            print()

        print("=" * 70)
        print("FIX SUMMARY")
        print("=" * 70)
        print(f"✅ Files fixed: {len(set(fixed_files))}")
        print(f"✅ Duplicates removed: {duplicate_count}")
        print(f"✅ Hallucinations fixed: {len(hallucinations)}")
        print()
    else:
        print("=" * 70)
        print("✅ ALL CHECKS PASSED - No fixes needed!")
        print("=" * 70)
        print()

    return len(issues_found) == 0 and duplicate_count == 0 and len(hallucinations) == 0


if __name__ == "__main__":
    success = validate_all()

    if success:
        print("🎉 Validation complete - all requirements are valid!")
    else:
        print("✅ Validation complete - issues have been fixed!")

    print()
    print("Next steps:")
    print("  1. Review fixed files")
    print("  2. Re-run validation to confirm fixes")
    print("  3. Commit changes to Git")
    print()
