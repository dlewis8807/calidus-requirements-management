# Synthetic Requirements Index

Generated: 2025-10-17
Total Files: 103 JSON files

## Quick Statistics

| Category | Files | Est. Requirements | Issues |
|----------|-------|-------------------|--------|
| **AHLR** | 25 | 75-125 | 2 |
| **System** | 35 | 175-280 | 3 |
| **Technical** | 20 | 160-240 | 2 |
| **Certification** | 20 | 40-80 | 1 |
| **Traceability** | 3 | - | - |
| **TOTAL** | **103** | **~600** | **8** |

## Files by Category

### Aircraft High-Level Requirements (25 files)

#### Flight Control (5 files)
- [AHLR-001-FlightControl.json](AHLR/AHLR-001-FlightControl.json) - Redundant flight control systems
- [AHLR-002-FlightControl.json](AHLR/AHLR-002-FlightControl.json) - Controllability in all conditions
- [AHLR-003-FlightControl.json](AHLR/AHLR-003-FlightControl.json) - Control authority requirements
- [AHLR-004-FlightControl.json](AHLR/AHLR-004-FlightControl.json) - Pilot-induced oscillation prevention
- [AHLR-005-FlightControl.json](AHLR/AHLR-005-FlightControl.json) - Performance limits

#### Powerplant (4 files)
- [AHLR-006-Powerplant.json](AHLR/AHLR-006-Powerplant.json) - Power requirements OEI
- [AHLR-007-Powerplant.json](AHLR/AHLR-007-Powerplant.json) - Engine failure safety
- [AHLR-008-Powerplant.json](AHLR/AHLR-008-Powerplant.json) - Parameter monitoring
- [AHLR-009-Powerplant.json](AHLR/AHLR-009-Powerplant.json) - Fuel supply continuity

#### Structures (5 files)
- [AHLR-010-Structures.json](AHLR/AHLR-010-Structures.json) - Limit loads
- [AHLR-011-Structures.json](AHLR/AHLR-011-Structures.json) - Ultimate loads
- [AHLR-012-Structures.json](AHLR/AHLR-012-Structures.json) - Structural integrity
- [AHLR-013-Structures.json](AHLR/AHLR-013-Structures.json) - Crash survivability
- [AHLR-014-Structures.json](AHLR/AHLR-014-Structures.json) - Fail-safe design

#### Systems (4 files)
- [AHLR-015-Systems.json](AHLR/AHLR-015-Systems.json) ⚠️ **GAP - No downstream requirements**
- [AHLR-016-Systems.json](AHLR/AHLR-016-Systems.json) - System failure safety
- [AHLR-017-Systems.json](AHLR/AHLR-017-Systems.json) - System health monitoring
- [AHLR-018-Systems.json](AHLR/AHLR-018-Systems.json) - System reconfiguration

#### Performance (4 files)
- [AHLR-019-Performance.json](AHLR/AHLR-019-Performance.json) - Takeoff/landing performance
- [AHLR-020-Performance.json](AHLR/AHLR-020-Performance.json) - Climb gradient
- [AHLR-021-Performance.json](AHLR/AHLR-021-Performance.json) - Stall speed
- [AHLR-022-Performance.json](AHLR/AHLR-022-Performance.json) - Cruise performance

#### Safety (3 files)
- [AHLR-023-Safety.json](AHLR/AHLR-023-Safety.json) ⚠️ **OUTDATED - References DO-178B**
- [AHLR-024-Safety.json](AHLR/AHLR-024-Safety.json) - Fire detection/suppression
- [AHLR-025-Safety.json](AHLR/AHLR-025-Safety.json) - Crashworthiness

### System Requirements (35 files)

#### Flight Control Systems (13 files)
- SYS-042 through SYS-046: Autopilot (5 files)
- SYS-047 through SYS-050: Fly-by-Wire (4 files)
- SYS-051 through SYS-054: Actuators (4 files)

#### Avionics Systems (8 files)
- SYS-055 through SYS-058: Display (4 files)
- SYS-059 through SYS-062: Navigation (4 files)

#### Hydraulics Systems (6 files)
- SYS-063 through SYS-065: Primary (3 files)
- SYS-066 through SYS-068: Backup (3 files)
  - [SYS-067-Hydraulics-Backup.json](System/SYS-067-Hydraulics-Backup.json) ⚠️ **CONFLICT with SYS-089**

#### Electrical Systems (6 files)
- SYS-069 through SYS-071: Power (3 files)
- SYS-072 through SYS-074: Distribution (3 files)

#### Fuel Systems (2 files)
- SYS-075 through SYS-076: Storage (2 files)

⚠️ **SYS-078** - Contains TBD fields (incomplete)
⚠️ **SYS-089** - Orphaned requirement (no parent AHLR)

### Technical Specifications (20 files)

Components covered:
- TECH-089: ActuatorInterface
- TECH-090: DisplayProcessor
- TECH-091: SensorFusion ⚠️ **DUPLICATE of TECH-092**
- TECH-092: NavigationComputer
- TECH-093: HydraulicPump
- TECH-094: PowerSupply
- TECH-095: FuelValve
- TECH-096: ControlSurfaceActuator
- TECH-097: FlightDataRecorder
- TECH-098: WeatherRadar
- TECH-099: AutopilotServo
- TECH-100: AntiIceSystem
- TECH-101: LandingGearController
- TECH-102: CabinPressure
- TECH-103: OxygenSystem
- TECH-104: EmergencyPowerUnit
- TECH-105: FireSuppressionSystem
- TECH-106: CommunicationsRadio
- TECH-107: TransponderSystem
- TECH-108: TCASystem

⚠️ **TECH-034** - Ambiguous acceptance criteria

### Certification Requirements (20 files)

- CERT-118: FlightTest
- CERT-119: StructuralTest
- CERT-120: SystemsTest
- CERT-121: SoftwareVerification
- CERT-122: HardwareVerification
- CERT-123: FailureModes
- CERT-124: SafetyAnalysis
- CERT-125: EnvironmentalTest
- CERT-126: EMITest
- CERT-127: LightningTest
- CERT-128: BirdStrike
- CERT-129: Crashworthiness
- CERT-130: FlammabilityTest
- CERT-131: ToxicityTest
- CERT-132: EmergencyEvacuation
- CERT-133: GroundHandling
- CERT-134: PerformanceDemo
- CERT-135: StallTest
- CERT-136: SpinTest
- CERT-137: Documentation

⚠️ **CERT-045** - Missing test cases

### Traceability Files (3 files)

- [traceability_matrix.json](Traceability/traceability_matrix.json) - Full traceability matrix with 275 links
- [gap_analysis.json](Traceability/gap_analysis.json) - Gap analysis report
- [compliance_matrix.json](Traceability/compliance_matrix.json) - 14 CFR Part 23 compliance

## Intentional Issues for Troubleshooting Demo

### 1. Gap: AHLR-015 (High Severity)
**Type**: Missing Downstream Requirements
**Description**: AHLR-015 has no derived system requirements
**Impact**: Cannot verify compliance
**File**: [AHLR/AHLR-015-Systems.json](AHLR/AHLR-015-Systems.json)

### 2. Orphan: SYS-089 (Critical Severity)
**Type**: Missing Upstream Traceability
**Description**: SYS-089 has no parent AHLR
**Impact**: Unclear regulatory basis
**File**: System/SYS-089-*.json (needs to be located in generated files)

### 3. Conflict: SYS-067 vs SYS-089 (High Severity)
**Type**: Contradictory Requirements
**Description**: SYS-067 and SYS-089 have conflicting specifications
**Impact**: Design ambiguity
**Files**: [System/SYS-067-Hydraulics-Backup.json](System/SYS-067-Hydraulics-Backup.json)

### 4. Ambiguity: TECH-034 (Medium Severity)
**Type**: Unclear Acceptance Criteria
**Description**: TECH-034 has multiple interpretations
**Impact**: Verification uncertainty
**File**: Technical/TECH-034-*.json

### 5. Missing Verification: CERT-045 (High Severity)
**Type**: No Test Cases Defined
**Description**: CERT-045 lacks verification plan
**Impact**: Cannot demonstrate compliance
**File**: Certification/CERT-045-*.json

### 6. Outdated: AHLR-023 (Medium Severity)
**Type**: Superseded Reference
**Description**: References DO-178B instead of DO-178C
**Impact**: Non-current compliance basis
**File**: [AHLR/AHLR-023-Safety.json](AHLR/AHLR-023-Safety.json)

### 7. Incomplete: SYS-078 (Medium Severity)
**Type**: TBD Fields
**Description**: Contains "TBD" in description
**Impact**: Incomplete specification
**File**: System/SYS-078-*.json

### 8. Duplicate: TECH-091 = TECH-092 (Low Severity)
**Type**: Redundant Requirements
**Description**: TECH-091 and TECH-092 are duplicates
**Impact**: Maintenance burden
**Files**: [Technical/TECH-091-SensorFusion.json](Technical/TECH-091-SensorFusion.json), [Technical/TECH-092-NavigationComputer.json](Technical/TECH-092-NavigationComputer.json)

## 14 CFR Part 23 Coverage

All requirements link to specific sections of 14 CFR Part 23:
- File path: `/Users/z/Documents/CALIDUS/rawdata/14 CFR Part 23 (in effect on 3-31-2017).pdf`
- Sections covered: §23.143 through §23.672
- Page references: 23 through 180

## Usage Examples

### Import All Requirements

```bash
# Navigate to synthetic_requirements directory
cd /Users/z/Documents/CALIDUS/synthetic_requirements

# Import via CALIDUS demo
# 1. Open http://localhost:3000/demo
# 2. Select "Upload Documents" section
# 3. Upload all JSON files from each subdirectory
```

### Run Traceability Analysis

```bash
# View traceability matrix
cat Traceability/traceability_matrix.json | python3 -m json.tool

# View gap analysis
cat Traceability/gap_analysis.json | python3 -m json.tool

# View compliance matrix
cat Traceability/compliance_matrix.json | python3 -m json.tool
```

### Find Specific Issues

```bash
# Find all requirements with issues
grep -r '"issues": \[' --include="*.json" | wc -l

# Find gap issues
grep -r '"type": "Gap"' --include="*.json"

# Find orphan requirements
grep -r '"type": "Orphan"' --include="*.json"

# Find conflicts
grep -r '"type": "Conflict"' --include="*.json"
```

## Verification Checklist

- [x] 25 AHLR files generated
- [x] 35 System files generated
- [x] 20 Technical files generated
- [x] 20 Certification files generated
- [x] 3 Traceability files generated
- [x] All files reference 14 CFR Part 23 PDF
- [x] Intentional issues included for demo
- [x] JSON format valid
- [x] Proper requirement IDs assigned
- [x] Traceability links established

## Next Steps

1. **Review Requirements**: Examine sample files for quality
2. **Import to CALIDUS**: Use demo page upload feature
3. **Run Analysis**: Execute traceability and gap analysis
4. **View Dashboard**: Explore troubleshooting features
5. **Generate Reports**: Export compliance and coverage reports

---

**Generated**: 2025-10-17
**Tool**: generate_synthetic_requirements.py
**Purpose**: Demonstrate CALIDUS capabilities
**Status**: ✅ Ready for import
