# Synthetic Requirements Dataset

This directory contains 100+ synthetic requirements files for demonstrating CALIDUS capabilities.

## Purpose

These synthetic requirements demonstrate:
- ✅ Multi-level requirements hierarchy
- ✅ Traceability across requirement types
- ✅ Compliance mapping to 14 CFR Part 23
- ✅ Gap detection and analysis
- ✅ Ambiguity identification
- ✅ Coverage analysis
- ✅ Impact assessment

## Directory Structure

```
synthetic_requirements/
├── AHLR/                   # Aircraft High-Level Requirements (25 files)
├── System/                 # System Requirements (35 files)
├── Technical/              # Technical Specifications (20 files)
├── Certification/          # Certification Requirements (20 files)
├── Traceability/           # Traceability matrices (10+ files)
└── README.md              # This file
```

## Requirement Classifications

### 1. Aircraft High-Level Requirements (AHLR) - 25 files
Top-level safety and functional requirements derived from regulations.

**Format**: `AHLR-XXX-[Category].json`
**Categories**:
- Flight Control
- Powerplant
- Structures
- Systems
- Performance
- Safety

**Example**: `AHLR-001-FlightControl.json`

### 2. System Requirements (SYS) - 35 files
Derived system-level requirements that implement AHLRs.

**Format**: `SYS-XXX-[System]-[Subsystem].json`
**Systems**:
- Flight Control Systems
- Avionics
- Hydraulics
- Electrical
- Fuel Systems
- Landing Gear
- Environmental Control

**Example**: `SYS-042-FlightControl-Autopilot.json`

### 3. Technical Specifications (TECH) - 20 files
Detailed technical specifications for implementation.

**Format**: `TECH-XXX-[Component].json`
**Components**:
- Hardware specifications
- Software requirements
- Interface definitions
- Performance parameters
- Test specifications

**Example**: `TECH-089-ActuatorInterface.json`

### 4. Certification Requirements (CERT) - 20 files
Compliance requirements for FAA certification.

**Format**: `CERT-XXX-[Regulation].json`
**Regulations**:
- 14 CFR Part 23 sections
- DO-178C compliance
- DO-254 compliance
- Testing requirements
- Documentation requirements

**Example**: `CERT-118-Part23.23.143.json`

## Traceability Structure

Each requirement includes:
- **Requirement ID**: Unique identifier
- **Title**: Short description
- **Description**: Detailed requirement text
- **Rationale**: Why this requirement exists
- **Priority**: Critical/High/Medium/Low
- **Status**: Draft/Approved/Verified/Validated
- **Source**: Reference to 14 CFR Part 23 section
- **Traces To**: Parent requirements (upward traceability)
- **Traced By**: Child requirements (downward traceability)
- **Verification Method**: Test/Analysis/Inspection/Demo
- **Compliance**: Regulatory compliance mapping

## File Format

All requirements are in JSON format for easy parsing:

```json
{
  "requirement_id": "AHLR-001",
  "type": "Aircraft_High_Level_Requirement",
  "category": "Flight_Control",
  "title": "Redundant Flight Control Systems",
  "description": "The aircraft SHALL provide redundant flight control systems...",
  "rationale": "Required for safety in case of single system failure",
  "priority": "Critical",
  "status": "Approved",
  "regulatory_source": {
    "document": "14 CFR Part 23",
    "section": "§23.672",
    "title": "Stability augmentation and automatic and power-operated systems",
    "file_path": "/Users/z/Documents/CALIDUS/rawdata/14 CFR Part 23 (in effect on 3-31-2017).pdf",
    "page": 89
  },
  "traces_to": [],
  "traced_by": ["SYS-042", "SYS-043"],
  "verification_method": "Test",
  "test_cases": ["TC-101", "TC-102"],
  "compliance_status": "Compliant",
  "issues": []
}
```

## Traceability Scenarios

### Complete Traceability (Green)
- AHLR-001 → SYS-042 → TECH-089 → CERT-118
- All links valid, no gaps

### Missing Links (Yellow)
- AHLR-015 → [GAP] → TECH-095
- Missing system requirement

### Orphaned Requirements (Red)
- SYS-089 has no parent AHLR
- No traceability to regulation

### Ambiguous Requirements (Orange)
- TECH-034 has unclear acceptance criteria
- Multiple interpretations possible

### Conflicting Requirements (Red)
- SYS-067 conflicts with SYS-089
- Requires resolution

## Usage in CALIDUS

### Import Requirements

```bash
# Method 1: Bulk import via API
curl -X POST http://localhost:8000/api/requirements/bulk-import \
  -F "files=@synthetic_requirements/*.json"

# Method 2: Import via frontend
# Navigate to: http://localhost:3000/demo
# Upload JSON files from synthetic_requirements/
```

### Run Traceability Analysis

```bash
# Generate traceability matrix
curl http://localhost:8000/api/traceability/matrix

# Detect gaps
curl http://localhost:8000/api/traceability/gaps

# Find orphaned requirements
curl http://localhost:8000/api/traceability/orphans
```

### Run Compliance Check

```bash
# Check 14 CFR Part 23 compliance
curl http://localhost:8000/api/compliance/check?regulation=14_CFR_Part_23

# Generate compliance report
curl http://localhost:8000/api/compliance/report -o compliance_report.pdf
```

## Statistics

| Category | Count | Avg per File |
|----------|-------|--------------|
| AHLR | 25 files | ~3-5 requirements |
| System | 35 files | ~5-8 requirements |
| Technical | 20 files | ~8-12 requirements |
| Certification | 20 files | ~2-4 requirements |
| **Total Requirements** | **~600** | **6 avg** |

## Traceability Coverage

| Link Type | Count | Coverage |
|-----------|-------|----------|
| AHLR → SYS | 75 links | 90% |
| SYS → TECH | 120 links | 85% |
| TECH → CERT | 80 links | 95% |
| **Total Links** | **275** | **90%** |

## Known Issues (Intentional)

To demonstrate troubleshooting features:

1. **Gap: AHLR-015** - No system requirements defined
2. **Orphan: SYS-089** - No parent AHLR
3. **Ambiguity: TECH-034** - Unclear acceptance criteria
4. **Conflict: SYS-067 vs SYS-089** - Contradictory requirements
5. **Missing Verification: CERT-045** - No test cases defined
6. **Outdated: AHLR-023** - References superseded standard
7. **Incomplete: SYS-078** - TBD in description field
8. **Duplicate: TECH-091 = TECH-092** - Redundant requirements

## Generation Metadata

- **Generated**: 2025-10-17
- **Format**: JSON
- **Schema Version**: 1.0
- **Total Files**: 100
- **Total Requirements**: ~600
- **Traceability Links**: ~275
- **Regulatory References**: 14 CFR Part 23
- **Compliance Coverage**: 90%

---

**Note**: These are synthetic requirements for demonstration purposes only. They are not intended for actual aircraft certification.
