#!/usr/bin/env python3
"""
Generate synthetic requirements for CALIDUS demonstration.
Creates 100 requirement files with proper traceability.
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any

# Base path for synthetic requirements
BASE_PATH = Path("/Users/z/Documents/CALIDUS/synthetic_requirements")

# Reference to 14 CFR Part 23 PDF
CFR_PART_23_PATH = "/Users/z/Documents/CALIDUS/rawdata/14 CFR Part 23 (in effect on 3-31-2017).pdf"

# CFR Part 23 sections for reference
CFR_SECTIONS = [
    {"section": "§23.143", "title": "General", "page": 23},
    {"section": "§23.145", "title": "Longitudinal control", "page": 24},
    {"section": "§23.147", "title": "Directional and lateral control", "page": 25},
    {"section": "§23.149", "title": "Minimum control speed", "page": 26},
    {"section": "§23.151", "title": "Acrobatic maneuvers", "page": 27},
    {"section": "§23.153", "title": "Control during landings", "page": 28},
    {"section": "§23.155", "title": "Elevator control force in maneuvers", "page": 29},
    {"section": "§23.161", "title": "Trim", "page": 32},
    {"section": "§23.171", "title": "General", "page": 35},
    {"section": "§23.173", "title": "Static longitudinal stability", "page": 36},
    {"section": "§23.175", "title": "Demonstration of static longitudinal stability", "page": 37},
    {"section": "§23.177", "title": "Static directional and lateral stability", "page": 38},
    {"section": "§23.181", "title": "Dynamic stability", "page": 40},
    {"section": "§23.201", "title": "Wings level stall", "page": 45},
    {"section": "§23.203", "title": "Turning flight and accelerated turning stalls", "page": 46},
    {"section": "§23.207", "title": "Stall warning", "page": 47},
    {"section": "§23.221", "title": "Spinning", "page": 50},
    {"section": "§23.231", "title": "Longitudinal stability and control", "page": 55},
    {"section": "§23.233", "title": "Directional stability and control", "page": 56},
    {"section": "§23.235", "title": "Operation on unpaved surfaces", "page": 57},
    {"section": "§23.251", "title": "Vibration and buffeting", "page": 60},
    {"section": "§23.253", "title": "High speed characteristics", "page": 61},
    {"section": "§23.301", "title": "Loads", "page": 70},
    {"section": "§23.303", "title": "Factor of safety", "page": 71},
    {"section": "§23.305", "title": "Strength and deformation", "page": 72},
    {"section": "§23.307", "title": "Proof of structure", "page": 73},
    {"section": "§23.321", "title": "General", "page": 75},
    {"section": "§23.331", "title": "Symmetric maneuvering conditions", "page": 78},
    {"section": "§23.333", "title": "Flight envelope", "page": 79},
    {"section": "§23.335", "title": "Design airspeeds", "page": 80},
    {"section": "§23.337", "title": "Limit maneuvering load factors", "page": 81},
    {"section": "§23.341", "title": "Gust and turbulence loads", "page": 82},
    {"section": "§23.345", "title": "High lift devices", "page": 85},
    {"section": "§23.349", "title": "Rolling conditions", "page": 86},
    {"section": "§23.351", "title": "Yawing conditions", "page": 87},
    {"section": "§23.361", "title": "Engine torque", "page": 88},
    {"section": "§23.363", "title": "Side load on engine mount", "page": 89},
    {"section": "§23.365", "title": "Pressurized cabin loads", "page": 90},
    {"section": "§23.367", "title": "Unsymmetrical loads due to engine failure", "page": 91},
    {"section": "§23.369", "title": "Rear lift truss", "page": 92},
    {"section": "§23.371", "title": "Gyroscopic and aerodynamic loads", "page": 93},
    {"section": "§23.373", "title": "Speed control devices", "page": 94},
    {"section": "§23.391", "title": "Control surface and system loads", "page": 95},
    {"section": "§23.393", "title": "Loads parallel to hinge line", "page": 96},
    {"section": "§23.395", "title": "Control system", "page": 97},
    {"section": "§23.397", "title": "Limit control forces and torques", "page": 98},
    {"section": "§23.399", "title": "Dual control system", "page": 99},
    {"section": "§23.405", "title": "Secondary control system", "page": 100},
    {"section": "§23.407", "title": "Trim tab effects", "page": 101},
    {"section": "§23.415", "title": "Ground gust conditions", "page": 102},
    {"section": "§23.441", "title": "Maneuvering loads", "page": 105},
    {"section": "§23.443", "title": "Gust loads", "page": 106},
    {"section": "§23.445", "title": "Outboard fins or winglets", "page": 107},
    {"section": "§23.453", "title": "Nose wheel", "page": 110},
    {"section": "§23.459", "title": "Special devices", "page": 111},
    {"section": "§23.471", "title": "General", "page": 115},
    {"section": "§23.473", "title": "Ground load conditions and assumptions", "page": 116},
    {"section": "§23.477", "title": "Landing gear arrangement", "page": 117},
    {"section": "§23.479", "title": "Level landing conditions", "page": 118},
    {"section": "§23.481", "title": "Tail down landing conditions", "page": 119},
    {"section": "§23.483", "title": "One-wheel landing conditions", "page": 120},
    {"section": "§23.485", "title": "Side load conditions", "page": 121},
    {"section": "§23.493", "title": "Braked roll conditions", "page": 122},
    {"section": "§23.497", "title": "Supplementary conditions for tail wheels", "page": 123},
    {"section": "§23.499", "title": "Supplementary conditions for nose wheels", "page": 124},
    {"section": "§23.501", "title": "Ground load conditions: landing gear with skids", "page": 125},
    {"section": "§23.505", "title": "Ski landing conditions", "page": 126},
    {"section": "§23.507", "title": "Jacking loads", "page": 127},
    {"section": "§23.509", "title": "Towing loads", "page": 128},
    {"section": "§23.511", "title": "Ground load: unsymmetrical loads on multiple-wheel units", "page": 129},
    {"section": "§23.521", "title": "Water load conditions", "page": 130},
    {"section": "§23.523", "title": "Design weights and center of gravity positions", "page": 131},
    {"section": "§23.525", "title": "Application of loads", "page": 132},
    {"section": "§23.527", "title": "Hull and main float load factors", "page": 133},
    {"section": "§23.529", "title": "Hull and main float landing conditions", "page": 134},
    {"section": "§23.531", "title": "Hull and main float takeoff condition", "page": 135},
    {"section": "§23.533", "title": "Hull and main float bottom pressures", "page": 136},
    {"section": "§23.535", "title": "Auxiliary float loads", "page": 137},
    {"section": "§23.537", "title": "Seawing loads", "page": 138},
    {"section": "§23.561", "title": "Emergency landing conditions", "page": 145},
    {"section": "§23.562", "title": "Emergency landing dynamic conditions", "page": 146},
    {"section": "§23.571", "title": "Metallic pressurized cabin structures", "page": 150},
    {"section": "§23.572", "title": "Metallic wing, empennage, and associated structures", "page": 151},
    {"section": "§23.573", "title": "Damage tolerance and fatigue evaluation of structure", "page": 152},
    {"section": "§23.601", "title": "General", "page": 160},
    {"section": "§23.603", "title": "Materials and workmanship", "page": 161},
    {"section": "§23.605", "title": "Fabrication methods", "page": 162},
    {"section": "§23.607", "title": "Fasteners", "page": 163},
    {"section": "§23.609", "title": "Protection of structure", "page": 164},
    {"section": "§23.611", "title": "Accessibility provisions", "page": 165},
    {"section": "§23.613", "title": "Material strength properties and design values", "page": 166},
    {"section": "§23.619", "title": "Special factors", "page": 167},
    {"section": "§23.621", "title": "Casting factors", "page": 168},
    {"section": "§23.623", "title": "Bearing factors", "page": 169},
    {"section": "§23.625", "title": "Fitting factors", "page": 170},
    {"section": "§23.627", "title": "Fatigue strength", "page": 171},
    {"section": "§23.629", "title": "Flutter", "page": 172},
    {"section": "§23.672", "title": "Stability augmentation and automatic and power-operated systems", "page": 180},
]

# AHLR categories
AHLR_CATEGORIES = {
    "FlightControl": {"count": 5, "prefix": "FC"},
    "Powerplant": {"count": 4, "prefix": "PP"},
    "Structures": {"count": 5, "prefix": "ST"},
    "Systems": {"count": 4, "prefix": "SY"},
    "Performance": {"count": 4, "prefix": "PF"},
    "Safety": {"count": 3, "prefix": "SF"},
}

# System categories
SYSTEM_CATEGORIES = {
    "FlightControl-Autopilot": {"count": 5, "parent_ahlr": ["AHLR-001", "AHLR-002"]},
    "FlightControl-FlyByWire": {"count": 4, "parent_ahlr": ["AHLR-001", "AHLR-003"]},
    "FlightControl-Actuators": {"count": 4, "parent_ahlr": ["AHLR-002", "AHLR-004"]},
    "Avionics-Display": {"count": 4, "parent_ahlr": ["AHLR-014", "AHLR-015"]},
    "Avionics-Navigation": {"count": 4, "parent_ahlr": ["AHLR-016", "AHLR-017"]},
    "Hydraulics-Primary": {"count": 3, "parent_ahlr": ["AHLR-018"]},
    "Hydraulics-Backup": {"count": 3, "parent_ahlr": ["AHLR-018", "AHLR-021"]},
    "Electrical-Power": {"count": 3, "parent_ahlr": ["AHLR-019"]},
    "Electrical-Distribution": {"count": 3, "parent_ahlr": ["AHLR-019", "AHLR-020"]},
    "FuelSystem-Storage": {"count": 2, "parent_ahlr": ["AHLR-006"]},
}


def generate_ahlr_requirements():
    """Generate Aircraft High-Level Requirements."""
    print("Generating AHLR files...")

    ahlr_id = 1
    cfr_idx = 0

    for category, info in AHLR_CATEGORIES.items():
        for i in range(info["count"]):
            req_id = f"AHLR-{ahlr_id:03d}"
            cfr_ref = CFR_SECTIONS[cfr_idx % len(CFR_SECTIONS)]

            # Intentional issues for demonstration
            issues = []
            status = "Approved"
            if req_id == "AHLR-015":
                issues.append({
                    "type": "Gap",
                    "severity": "High",
                    "description": "No system requirements defined for this AHLR"
                })
                status = "Under_Review"
            elif req_id == "AHLR-023":
                issues.append({
                    "type": "Outdated",
                    "severity": "Medium",
                    "description": "References superseded DO-178B instead of DO-178C"
                })

            requirement = {
                "requirement_id": req_id,
                "type": "Aircraft_High_Level_Requirement",
                "category": category,
                "title": f"{category} Requirement {i+1}",
                "description": f"The aircraft SHALL {get_ahlr_description(category, i)}",
                "rationale": f"Required for {category.lower()} safety and certification compliance",
                "priority": "Critical" if i < 2 else "High",
                "status": status,
                "regulatory_source": {
                    "document": "14 CFR Part 23",
                    "section": cfr_ref["section"],
                    "title": cfr_ref["title"],
                    "file_path": CFR_PART_23_PATH,
                    "page": cfr_ref["page"]
                },
                "traces_to": [],
                "traced_by": [],
                "verification_method": "Test" if i % 2 == 0 else "Analysis",
                "test_cases": [],
                "compliance_status": "Compliant" if not issues else "Non_Compliant",
                "issues": issues,
                "created_date": "2025-01-15",
                "last_modified": "2025-10-15",
                "owner": "System Safety Engineering",
                "version": "2.1"
            }

            # Save file
            filename = f"AHLR-{ahlr_id:03d}-{category}.json"
            filepath = BASE_PATH / "AHLR" / filename
            with open(filepath, 'w') as f:
                json.dump(requirement, f, indent=2)

            print(f"  Created: {filename}")
            ahlr_id += 1
            cfr_idx += 1


def get_ahlr_description(category, index):
    """Generate realistic AHLR descriptions."""
    descriptions = {
        "FlightControl": [
            "provide redundant flight control systems with automatic failover capability",
            "maintain controllability in all flight conditions and configurations",
            "provide adequate control authority for all phases of flight",
            "prevent pilot-induced oscillations through proper control system design",
            "ensure flight control system operates within specified performance limits"
        ],
        "Powerplant": [
            "provide sufficient power for all flight phases including one-engine-inoperative",
            "prevent engine failure from causing unsafe conditions",
            "monitor engine parameters and alert crew of anomalies",
            "ensure fuel supply continuity to engines under all conditions"
        ],
        "Structures": [
            "withstand limit loads without permanent deformation",
            "withstand ultimate loads without structural failure",
            "maintain structural integrity for the design life of the aircraft",
            "provide crash survivability through energy-absorbing structures",
            "prevent catastrophic failure through fail-safe design"
        ],
        "Systems": [
            "provide adequate system redundancy for critical functions",
            "ensure system failure does not endanger aircraft safety",
            "monitor system health and alert crew of failures",
            "enable safe system reconfiguration in case of failures"
        ],
        "Performance": [
            "achieve specified takeoff and landing performance",
            "maintain safe climb gradient in all configurations",
            "meet stall speed requirements with margin",
            "achieve certified cruise performance and range"
        ],
        "Safety": [
            "provide safe emergency egress for all occupants",
            "incorporate fire detection and suppression systems",
            "meet crashworthiness requirements for occupant protection"
        ]
    }
    return descriptions.get(category, ["meet applicable requirements"])[index % len(descriptions.get(category, [""]))]


def generate_system_requirements():
    """Generate System Requirements."""
    print("Generating System files...")

    sys_id = 42
    cfr_idx = 10

    for category, info in SYSTEM_CATEGORIES.items():
        for i in range(info["count"]):
            req_id = f"SYS-{sys_id:03d}"
            cfr_ref = CFR_SECTIONS[cfr_idx % len(CFR_SECTIONS)]
            parent_ahlr = info["parent_ahlr"][i % len(info["parent_ahlr"])]

            # Intentional issues
            issues = []
            status = "Approved"
            traces_to = [parent_ahlr]

            if req_id == "SYS-089":
                issues.append({
                    "type": "Orphan",
                    "severity": "Critical",
                    "description": "No parent AHLR defined - missing upward traceability"
                })
                traces_to = []
                status = "Needs_Review"
            elif req_id == "SYS-067":
                issues.append({
                    "type": "Conflict",
                    "severity": "High",
                    "description": "Conflicts with SYS-089 - contradictory requirements"
                })
            elif req_id == "SYS-078":
                issues.append({
                    "type": "Incomplete",
                    "severity": "Medium",
                    "description": "Contains TBD fields - incomplete specification"
                })
                status = "Draft"

            requirement = {
                "requirement_id": req_id,
                "type": "System_Requirement",
                "category": category,
                "title": f"{category.replace('-', ' ')} System Requirement {i+1}",
                "description": f"The {category.split('-')[0]} system SHALL {get_sys_description(category, i)}",
                "rationale": f"Derived from {parent_ahlr} to implement {category.lower()} functionality",
                "priority": "High" if i < 2 else "Medium",
                "status": status,
                "regulatory_source": {
                    "document": "14 CFR Part 23",
                    "section": cfr_ref["section"],
                    "title": cfr_ref["title"],
                    "file_path": CFR_PART_23_PATH,
                    "page": cfr_ref["page"]
                },
                "traces_to": traces_to,
                "traced_by": [],
                "verification_method": "Test",
                "test_cases": [f"TC-{sys_id+100}", f"TC-{sys_id+101}"],
                "compliance_status": "Compliant" if not issues else "Non_Compliant",
                "issues": issues,
                "created_date": "2025-02-10",
                "last_modified": "2025-10-16",
                "owner": "Systems Engineering",
                "version": "1.8",
                "interfaces": [f"ICD-{sys_id:03d}"]
            }

            filename = f"SYS-{sys_id:03d}-{category}.json"
            filepath = BASE_PATH / "System" / filename
            with open(filepath, 'w') as f:
                json.dump(requirement, f, indent=2)

            print(f"  Created: {filename}")
            sys_id += 1
            cfr_idx += 1


def get_sys_description(category, index):
    """Generate realistic system requirement descriptions."""
    sys_type = category.split('-')[0]
    subsystem = category.split('-')[1] if '-' in category else ""

    descriptions = {
        "FlightControl": [
            f"provide {subsystem.lower()} functionality with 99.999% reliability",
            f"detect and isolate {subsystem.lower()} failures within 100ms",
            f"operate within specified {subsystem.lower()} performance envelope",
            f"interface with pilot controls with less than 50ms latency",
            f"self-test {subsystem.lower()} components on powerup"
        ],
        "Avionics": [
            f"display {subsystem.lower()} information with clarity and accuracy",
            f"process {subsystem.lower()} data at minimum 20Hz update rate",
            f"provide {subsystem.lower()} backup capability in case of primary failure",
            f"integrate {subsystem.lower()} data from multiple sources"
        ],
        "Hydraulics": [
            f"maintain {subsystem.lower()} pressure between 2800-3200 PSI",
            f"provide {subsystem.lower()} system redundancy",
            f"detect {subsystem.lower()} leaks and alert crew",
            f"isolate failed {subsystem.lower()} components automatically"
        ],
        "Electrical": [
            f"provide {subsystem.lower()} at 28VDC ±2V",
            f"distribute {subsystem.lower()} with load balancing",
            f"protect {subsystem.lower()} circuits from overcurrent",
            f"monitor {subsystem.lower()} system health continuously"
        ],
        "FuelSystem": [
            f"ensure fuel {subsystem.lower()} meets capacity requirements",
            f"prevent fuel system icing through heating mechanisms",
            f"provide accurate fuel quantity indication"
        ]
    }

    category_key = sys_type
    return descriptions.get(category_key, ["meet applicable requirements"])[index % len(descriptions.get(category_key, [""]))]


def generate_technical_specs():
    """Generate Technical Specifications."""
    print("Generating Technical Specification files...")

    tech_id = 89
    cfr_idx = 20

    components = [
        "ActuatorInterface", "DisplayProcessor", "SensorFusion", "NavigationComputer",
        "HydraulicPump", "PowerSupply", "FuelValve", "ControlSurfaceActuator",
        "FlightDataRecorder", "WeatherRadar", "AutopilotServo", "AntiIceSystem",
        "LandingGearController", "CabinPressure", "OxygenSystem", "EmergencyPowerUnit",
        "FireSuppressionSystem", "CommunicationsRadio", "TransponderSystem", "TCASystem"
    ]

    for i, component in enumerate(components):
        req_id = f"TECH-{tech_id:03d}"
        cfr_ref = CFR_SECTIONS[cfr_idx % len(CFR_SECTIONS)]
        parent_sys = f"SYS-{50 + (i % 30):03d}"

        # Intentional issues
        issues = []
        status = "Approved"

        if req_id == "TECH-034":
            issues.append({
                "type": "Ambiguity",
                "severity": "Medium",
                "description": "Unclear acceptance criteria - multiple interpretations possible"
            })
            status = "Under_Review"
        elif req_id == "TECH-091":
            issues.append({
                "type": "Duplicate",
                "severity": "Low",
                "description": "Duplicate of TECH-092 - consolidation required"
            })

        requirement = {
            "requirement_id": req_id,
            "type": "Technical_Specification",
            "category": "Hardware" if i % 2 == 0 else "Software",
            "component": component,
            "title": f"{component} Technical Specification",
            "description": f"The {component} SHALL {get_tech_description(component)}",
            "rationale": f"Technical specification for implementing {parent_sys}",
            "priority": "Medium",
            "status": status,
            "regulatory_source": {
                "document": "14 CFR Part 23",
                "section": cfr_ref["section"],
                "title": cfr_ref["title"],
                "file_path": CFR_PART_23_PATH,
                "page": cfr_ref["page"]
            },
            "traces_to": [parent_sys],
            "traced_by": [f"CERT-{118 + i}"],
            "verification_method": "Test",
            "test_cases": [f"TC-{tech_id+200}", f"TC-{tech_id+201}", f"TC-{tech_id+202}"],
            "compliance_status": "Compliant" if not issues else "Needs_Review",
            "issues": issues,
            "created_date": "2025-03-20",
            "last_modified": "2025-10-17",
            "owner": "Design Engineering",
            "version": "3.2",
            "interfaces": [f"ICD-{tech_id:03d}"],
            "performance_requirements": {
                "response_time_ms": 50 + (i * 10),
                "reliability": 0.9999,
                "operating_temp_range": "-40C to +85C",
                "power_consumption_w": 5 + (i * 2)
            }
        }

        filename = f"TECH-{tech_id:03d}-{component}.json"
        filepath = BASE_PATH / "Technical" / filename
        with open(filepath, 'w') as f:
            json.dump(requirement, f, indent=2)

        print(f"  Created: {filename}")
        tech_id += 1
        cfr_idx += 1


def get_tech_description(component):
    """Generate realistic technical descriptions."""
    descriptions = {
        "ActuatorInterface": "interface with hydraulic actuators using MIL-STD-1553 protocol",
        "DisplayProcessor": "render cockpit displays at 60fps with <16ms latency",
        "SensorFusion": "fuse sensor data from multiple sources with Kalman filtering",
        "NavigationComputer": "compute navigation solution with <10m position accuracy",
        "HydraulicPump": "deliver 3000 PSI hydraulic pressure at 8 GPM flow rate",
        "PowerSupply": "provide 28VDC ±2V at 200A continuous rating",
        "FuelValve": "actuate within 500ms and seal with <0.1cc/min leakage",
        "ControlSurfaceActuator": "position control surfaces with ±0.5° accuracy",
        "FlightDataRecorder": "record flight data parameters at 8Hz minimum rate",
        "WeatherRadar": "detect weather at 160nm range with 1° beam width",
        "AutopilotServo": "control aircraft with ±2° heading accuracy",
        "AntiIceSystem": "prevent ice accumulation on critical surfaces",
        "LandingGearController": "extend/retract landing gear in <10 seconds",
        "CabinPressure": "maintain cabin pressure at 8000ft equivalent altitude",
        "OxygenSystem": "provide oxygen flow at 2-4 liters/min per occupant",
        "EmergencyPowerUnit": "provide emergency power within 5 seconds of failure",
        "FireSuppressionSystem": "discharge suppressant within 1 second of activation",
        "CommunicationsRadio": "communicate on VHF 118-136 MHz with 25kHz spacing",
        "TransponderSystem": "respond to Mode-S interrogations within 100μs",
        "TCASystem": "detect traffic threats within 40nm range"
    }
    return descriptions.get(component, f"implement {component.lower()} functionality per specification")


def generate_cert_requirements():
    """Generate Certification Requirements."""
    print("Generating Certification files...")

    cert_id = 118
    cfr_idx = 30

    cert_types = [
        "FlightTest", "StructuralTest", "SystemsTest", "SoftwareVerification",
        "HardwareVerification", "FailureModes", "SafetyAnalysis", "EnvironmentalTest",
        "EMITest", "LightningTest", "BirdStrike", "Crashworthiness",
        "FlammabilityTest", "ToxicityTest", "EmergencyEvacuation", "GroundHandling",
        "PerformanceDemo", "StallTest", "SpinTest", "Documentation"
    ]

    for i, cert_type in enumerate(cert_types):
        req_id = f"CERT-{cert_id:03d}"
        cfr_ref = CFR_SECTIONS[cfr_idx % len(CFR_SECTIONS)]
        parent_tech = f"TECH-{89 + i}"

        # Intentional issues
        issues = []
        status = "Approved"
        test_cases = [f"TC-{cert_id+100}", f"TC-{cert_id+101}"]

        if req_id == "CERT-045":
            issues.append({
                "type": "Missing_Verification",
                "severity": "High",
                "description": "No test cases defined for this certification requirement"
            })
            test_cases = []
            status = "Needs_Test_Plan"

        requirement = {
            "requirement_id": req_id,
            "type": "Certification_Requirement",
            "category": cert_type,
            "title": f"{cert_type} Certification Requirement",
            "description": f"The aircraft SHALL demonstrate compliance with 14 CFR Part 23 through {get_cert_description(cert_type)}",
            "rationale": "Required for FAA Type Certification",
            "priority": "Critical",
            "status": status,
            "regulatory_source": {
                "document": "14 CFR Part 23",
                "section": cfr_ref["section"],
                "title": cfr_ref["title"],
                "file_path": CFR_PART_23_PATH,
                "page": cfr_ref["page"]
            },
            "traces_to": [parent_tech] if i < 20 else [],
            "traced_by": [],
            "verification_method": "Test" if "Test" in cert_type else "Inspection",
            "test_cases": test_cases,
            "compliance_status": "Compliant" if not issues else "Pending_Verification",
            "issues": issues,
            "created_date": "2025-04-01",
            "last_modified": "2025-10-17",
            "owner": "Certification Engineering",
            "version": "1.0",
            "certification_basis": "14 CFR Part 23 Amendment 64",
            "approved_by": "FAA",
            "approval_date": "2025-09-15" if not issues else "TBD"
        }

        filename = f"CERT-{cert_id:03d}-Part23.{cfr_ref['section'].replace('§', '').replace('.', '_')}.json"
        filepath = BASE_PATH / "Certification" / filename
        with open(filepath, 'w') as f:
            json.dump(requirement, f, indent=2)

        print(f"  Created: {filename}")
        cert_id += 1
        cfr_idx += 1


def get_cert_description(cert_type):
    """Generate realistic certification descriptions."""
    descriptions = {
        "FlightTest": "flight testing per Part 23 Subpart B requirements",
        "StructuralTest": "static and fatigue testing of primary structures",
        "SystemsTest": "functional testing of all aircraft systems",
        "SoftwareVerification": "DO-178C Level A software verification",
        "HardwareVerification": "DO-254 hardware verification and validation",
        "FailureModes": "FMEA analysis per ARP4761 methodology",
        "SafetyAnalysis": "safety assessment and FHA/PSSA/SSA documentation",
        "EnvironmentalTest": "testing across operational temperature and altitude range",
        "EMITest": "EMI/EMC testing per DO-160 Category H",
        "LightningTest": "lightning strike testing and analysis",
        "BirdStrike": "bird strike resistance demonstration",
        "Crashworthiness": "crash test and seat/restraint system certification",
        "FlammabilityTest": "cabin materials flammability testing",
        "ToxicityTest": "cabin materials smoke and toxicity testing",
        "EmergencyEvacuation": "emergency evacuation demonstration",
        "GroundHandling": "ground handling and servicing procedures",
        "PerformanceDemo": "demonstrated performance vs. certified performance",
        "StallTest": "stall characteristics and stall warning demonstration",
        "SpinTest": "spin entry and recovery demonstration if required",
        "Documentation": "submission of Type Certificate Data Sheet and documentation"
    }
    return descriptions.get(cert_type, f"{cert_type.lower()} certification activities")


def generate_traceability_matrix():
    """Generate traceability matrix files."""
    print("Generating Traceability matrix files...")

    # Full traceability matrix
    matrix = {
        "document_title": "CALIDUS Requirements Traceability Matrix",
        "generated_date": "2025-10-17",
        "project": "Synthetic Requirements Demonstration",
        "total_requirements": 600,
        "total_links": 275,
        "coverage_percentage": 90.0,
        "trace_links": []
    }

    # Generate trace links
    for ahlr_id in range(1, 26):
        ahlr = f"AHLR-{ahlr_id:03d}"

        # Most AHLRs have system requirements
        if ahlr_id != 15:  # AHLR-015 has intentional gap
            for sys_offset in range(2):
                sys_id = 42 + (ahlr_id * 2) + sys_offset
                if sys_id <= 76:
                    sys = f"SYS-{sys_id:03d}"

                    # Link to technical specs
                    tech_id = 89 + ((sys_id - 42) % 20)
                    tech = f"TECH-{tech_id:03d}"

                    # Link to certification
                    cert_id = 118 + ((tech_id - 89) % 20)
                    cert = f"CERT-{cert_id:03d}"

                    matrix["trace_links"].append({
                        "ahlr": ahlr,
                        "system": sys,
                        "technical": tech,
                        "certification": cert,
                        "status": "Complete",
                        "cfr_reference": CFR_SECTIONS[(ahlr_id - 1) % len(CFR_SECTIONS)]["section"]
                    })

    # Add gaps and issues
    matrix["issues"] = [
        {
            "type": "Gap",
            "requirement": "AHLR-015",
            "description": "No system requirements defined",
            "severity": "High",
            "action_required": "Define SYS requirements for AHLR-015"
        },
        {
            "type": "Orphan",
            "requirement": "SYS-089",
            "description": "No parent AHLR",
            "severity": "Critical",
            "action_required": "Link SYS-089 to appropriate AHLR"
        },
        {
            "type": "Conflict",
            "requirements": ["SYS-067", "SYS-089"],
            "description": "Contradictory requirements",
            "severity": "High",
            "action_required": "Resolve conflict between SYS-067 and SYS-089"
        },
        {
            "type": "Ambiguity",
            "requirement": "TECH-034",
            "description": "Unclear acceptance criteria",
            "severity": "Medium",
            "action_required": "Clarify TECH-034 acceptance criteria"
        },
        {
            "type": "Missing_Verification",
            "requirement": "CERT-045",
            "description": "No test cases defined",
            "severity": "High",
            "action_required": "Define test cases for CERT-045"
        }
    ]

    filepath = BASE_PATH / "Traceability" / "traceability_matrix.json"
    with open(filepath, 'w') as f:
        json.dump(matrix, f, indent=2)

    print("  Created: traceability_matrix.json")

    # Generate gap analysis
    gap_analysis = {
        "document_title": "Requirements Gap Analysis",
        "generated_date": "2025-10-17",
        "summary": {
            "total_requirements": 100,
            "complete_traces": 85,
            "gaps_found": 5,
            "orphans_found": 1,
            "conflicts_found": 1,
            "ambiguities_found": 1
        },
        "gaps": [
            {
                "id": "GAP-001",
                "type": "Missing_Downstream",
                "requirement": "AHLR-015",
                "description": "AHLR-015 has no derived system requirements",
                "impact": "Cannot verify compliance with AHLR-015",
                "recommendation": "Create SYS requirements to implement AHLR-015",
                "priority": "High"
            },
            {
                "id": "GAP-002",
                "type": "Missing_Upstream",
                "requirement": "SYS-089",
                "description": "SYS-089 has no parent AHLR",
                "impact": "Unclear regulatory basis for SYS-089",
                "recommendation": "Link SYS-089 to appropriate AHLR or remove if not needed",
                "priority": "Critical"
            },
            {
                "id": "GAP-003",
                "type": "Missing_Verification",
                "requirement": "CERT-045",
                "description": "CERT-045 has no defined test cases",
                "impact": "Cannot demonstrate compliance",
                "recommendation": "Develop test plan for CERT-045",
                "priority": "High"
            }
        ]
    }

    filepath = BASE_PATH / "Traceability" / "gap_analysis.json"
    with open(filepath, 'w') as f:
        json.dump(gap_analysis, f, indent=2)

    print("  Created: gap_analysis.json")

    # Generate compliance matrix
    compliance = {
        "document_title": "14 CFR Part 23 Compliance Matrix",
        "generated_date": "2025-10-17",
        "regulation": "14 CFR Part 23",
        "total_sections": len(CFR_SECTIONS),
        "compliant_sections": int(len(CFR_SECTIONS) * 0.9),
        "non_compliant_sections": int(len(CFR_SECTIONS) * 0.1),
        "compliance_percentage": 90.0,
        "sections": []
    }

    for i, cfr_section in enumerate(CFR_SECTIONS[:30]):
        status = "Compliant"
        if i % 10 == 7:
            status = "Non_Compliant"
        elif i % 10 == 3:
            status = "Partially_Compliant"

        compliance["sections"].append({
            "section": cfr_section["section"],
            "title": cfr_section["title"],
            "page": cfr_section["page"],
            "status": status,
            "requirements": [f"AHLR-{(i % 25) + 1:03d}"],
            "test_cases": [f"TC-{100 + i}", f"TC-{101 + i}"] if status == "Compliant" else [],
            "notes": "" if status == "Compliant" else "Requires additional verification"
        })

    filepath = BASE_PATH / "Traceability" / "compliance_matrix.json"
    with open(filepath, 'w') as f:
        json.dump(compliance, f, indent=2)

    print("  Created: compliance_matrix.json")


def main():
    """Main generation function."""
    print("=" * 60)
    print("Generating Synthetic Requirements for CALIDUS")
    print("=" * 60)
    print()

    # Ensure directories exist
    (BASE_PATH / "AHLR").mkdir(parents=True, exist_ok=True)
    (BASE_PATH / "System").mkdir(parents=True, exist_ok=True)
    (BASE_PATH / "Technical").mkdir(parents=True, exist_ok=True)
    (BASE_PATH / "Certification").mkdir(parents=True, exist_ok=True)
    (BASE_PATH / "Traceability").mkdir(parents=True, exist_ok=True)

    # Generate requirements
    generate_ahlr_requirements()
    print()
    generate_system_requirements()
    print()
    generate_technical_specs()
    print()
    generate_cert_requirements()
    print()
    generate_traceability_matrix()

    print()
    print("=" * 60)
    print("✅ Generation Complete!")
    print("=" * 60)
    print(f"Total files created: 100+")
    print(f"  - AHLR: 25 files")
    print(f"  - System: 35 files")
    print(f"  - Technical: 20 files")
    print(f"  - Certification: 20 files")
    print(f"  - Traceability: 3 files")
    print()
    print(f"Location: {BASE_PATH}")
    print()
    print("Next steps:")
    print("  1. Review generated requirements")
    print("  2. Import to CALIDUS via demo page")
    print("  3. Run traceability analysis")
    print("  4. View gap analysis and troubleshooting features")
    print()


if __name__ == "__main__":
    main()
