#!/usr/bin/env python3
"""
Fix broken trace links in synthetic requirements.
"""

import json
from pathlib import Path

BASE_PATH = Path("/Users/z/Documents/CALIDUS/synthetic_requirements")

def fix_all_trace_links():
    """Fix broken trace links."""
    print("Fixing broken trace links...")
    print()

    fixed_count = 0

    # Fix certification files
    cert_path = BASE_PATH / "Certification"
    for filepath in cert_path.glob("*.json"):
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)

            modified = False

            # Fix traces_to links
            if "traces_to" in data:
                fixed_traces = []
                for trace_id in data["traces_to"]:
                    if trace_id:
                        # Fix TECH IDs (TECH-96 -> TECH-096)
                        if trace_id.startswith("TECH-") and len(trace_id) == 7:
                            fixed_id = f"TECH-{int(trace_id.split('-')[1]):03d}"
                            fixed_traces.append(fixed_id)
                            modified = True
                            print(f"  Fixed in {filepath.name}: {trace_id} -> {fixed_id}")
                        # Fix SYS IDs (SYS-50 -> SYS-050)
                        elif trace_id.startswith("SYS-") and len(trace_id) == 6:
                            fixed_id = f"SYS-{int(trace_id.split('-')[1]):03d}"
                            fixed_traces.append(fixed_id)
                            modified = True
                            print(f"  Fixed in {filepath.name}: {trace_id} -> {fixed_id}")
                        else:
                            fixed_traces.append(trace_id)
                    else:
                        fixed_traces.append(trace_id)

                data["traces_to"] = fixed_traces

            # Fix traced_by links
            if "traced_by" in data:
                fixed_traces = []
                for trace_id in data["traced_by"]:
                    if trace_id:
                        # Fix any shortened IDs
                        if trace_id.startswith("TECH-") and len(trace_id) == 7:
                            fixed_id = f"TECH-{int(trace_id.split('-')[1]):03d}"
                            fixed_traces.append(fixed_id)
                            modified = True
                        elif trace_id.startswith("SYS-") and len(trace_id) == 6:
                            fixed_id = f"SYS-{int(trace_id.split('-')[1]):03d}"
                            fixed_traces.append(fixed_id)
                            modified = True
                        elif trace_id.startswith("AHLR-") and len(trace_id) == 7:
                            fixed_id = f"AHLR-{int(trace_id.split('-')[1]):03d}"
                            fixed_traces.append(fixed_id)
                            modified = True
                        elif trace_id.startswith("CERT-") and len(trace_id) == 7:
                            fixed_id = f"CERT-{int(trace_id.split('-')[1]):03d}"
                            fixed_traces.append(fixed_id)
                            modified = True
                        else:
                            fixed_traces.append(trace_id)
                    else:
                        fixed_traces.append(trace_id)

                data["traced_by"] = fixed_traces

            # Save if modified
            if modified:
                with open(filepath, 'w') as f:
                    json.dump(data, f, indent=2)
                fixed_count += 1

        except Exception as e:
            print(f"❌ Error fixing {filepath}: {e}")

    # Check other categories too
    for category in ["AHLR", "System", "Technical"]:
        category_path = BASE_PATH / category
        if not category_path.exists():
            continue

        for filepath in category_path.glob("*.json"):
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)

                modified = False

                # Fix traces_to
                if "traces_to" in data:
                    fixed_traces = []
                    for trace_id in data["traces_to"]:
                        if trace_id and isinstance(trace_id, str):
                            # Ensure proper formatting
                            if trace_id.startswith("AHLR-"):
                                parts = trace_id.split("-")
                                if len(parts) == 2 and parts[1].isdigit():
                                    fixed_id = f"AHLR-{int(parts[1]):03d}"
                                    if fixed_id != trace_id:
                                        print(f"  Fixed in {filepath.name}: {trace_id} -> {fixed_id}")
                                        modified = True
                                    fixed_traces.append(fixed_id)
                                else:
                                    fixed_traces.append(trace_id)
                            elif trace_id.startswith("SYS-"):
                                parts = trace_id.split("-")
                                if len(parts) == 2 and parts[1].isdigit():
                                    fixed_id = f"SYS-{int(parts[1]):03d}"
                                    if fixed_id != trace_id:
                                        print(f"  Fixed in {filepath.name}: {trace_id} -> {fixed_id}")
                                        modified = True
                                    fixed_traces.append(fixed_id)
                                else:
                                    fixed_traces.append(trace_id)
                            elif trace_id.startswith("TECH-"):
                                parts = trace_id.split("-")
                                if len(parts) == 2 and parts[1].isdigit():
                                    fixed_id = f"TECH-{int(parts[1]):03d}"
                                    if fixed_id != trace_id:
                                        print(f"  Fixed in {filepath.name}: {trace_id} -> {fixed_id}")
                                        modified = True
                                    fixed_traces.append(fixed_id)
                                else:
                                    fixed_traces.append(trace_id)
                            else:
                                fixed_traces.append(trace_id)
                        else:
                            fixed_traces.append(trace_id)

                    data["traces_to"] = fixed_traces

                # Fix traced_by
                if "traced_by" in data:
                    fixed_traces = []
                    for trace_id in data["traced_by"]:
                        if trace_id and isinstance(trace_id, str):
                            # Ensure proper formatting (but allow TC- prefix)
                            if trace_id.startswith("TC-"):
                                fixed_traces.append(trace_id)
                            elif trace_id.startswith("SYS-"):
                                parts = trace_id.split("-")
                                if len(parts) == 2 and parts[1].isdigit():
                                    fixed_id = f"SYS-{int(parts[1]):03d}"
                                    if fixed_id != trace_id:
                                        print(f"  Fixed in {filepath.name}: {trace_id} -> {fixed_id}")
                                        modified = True
                                    fixed_traces.append(fixed_id)
                                else:
                                    fixed_traces.append(trace_id)
                            elif trace_id.startswith("TECH-"):
                                parts = trace_id.split("-")
                                if len(parts) == 2 and parts[1].isdigit():
                                    fixed_id = f"TECH-{int(parts[1]):03d}"
                                    if fixed_id != trace_id:
                                        print(f"  Fixed in {filepath.name}: {trace_id} -> {fixed_id}")
                                        modified = True
                                    fixed_traces.append(fixed_id)
                                else:
                                    fixed_traces.append(trace_id)
                            elif trace_id.startswith("CERT-"):
                                parts = trace_id.split("-")
                                if len(parts) == 2 and parts[1].isdigit():
                                    fixed_id = f"CERT-{int(parts[1]):03d}"
                                    if fixed_id != trace_id:
                                        print(f"  Fixed in {filepath.name}: {trace_id} -> {fixed_id}")
                                        modified = True
                                    fixed_traces.append(fixed_id)
                                else:
                                    fixed_traces.append(trace_id)
                            else:
                                fixed_traces.append(trace_id)
                        else:
                            fixed_traces.append(trace_id)

                    data["traced_by"] = fixed_traces

                if modified:
                    with open(filepath, 'w') as f:
                        json.dump(data, f, indent=2)
                    fixed_count += 1

            except Exception as e:
                print(f"❌ Error fixing {filepath}: {e}")

    print()
    print(f"✅ Fixed {fixed_count} files")
    print()

if __name__ == "__main__":
    fix_all_trace_links()
