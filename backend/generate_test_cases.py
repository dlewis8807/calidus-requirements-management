#!/usr/bin/env python3
"""
Generate 50 comprehensive test cases for the CALIDUS demo.
Test cases cover different types, statuses, and showcase various scenarios.
"""
import json
import random
from pathlib import Path
from datetime import datetime, timedelta

# Test case templates showcasing different scenarios
TEST_SCENARIOS = [
    # Flight Control Tests
    {
        "category": "FlightControl",
        "test_type": "Integration",
        "scenarios": [
            {"title": "Autopilot Failover Test", "objective": "Verify automatic failover to backup autopilot system"},
            {"title": "Flight Control Redundancy Validation", "objective": "Validate redundant flight control channels operate independently"},
            {"title": "Actuator Response Time Test", "objective": "Measure actuator response time under load conditions"},
        ]
    },
    # Avionics Tests
    {
        "category": "Avionics",
        "test_type": "System",
        "scenarios": [
            {"title": "Navigation System Accuracy Test", "objective": "Verify GPS navigation accuracy within specifications"},
            {"title": "Display System Brightness Test", "objective": "Validate display readability in all lighting conditions"},
            {"title": "TCAS Alert Response Test", "objective": "Verify Traffic Collision Avoidance System alert timing"},
        ]
    },
    # Electrical System Tests
    {
        "category": "Electrical",
        "test_type": "Unit",
        "scenarios": [
            {"title": "Power Distribution Load Test", "objective": "Test electrical distribution under maximum load"},
            {"title": "Battery Charging System Test", "objective": "Verify battery charging system maintains proper voltage"},
            {"title": "Generator Failover Test", "objective": "Test automatic generator failover on primary failure"},
        ]
    },
    # Fuel System Tests
    {
        "category": "FuelSystem",
        "test_type": "Integration",
        "scenarios": [
            {"title": "Fuel Flow Rate Test", "objective": "Measure fuel flow rate at various engine power settings"},
            {"title": "Fuel Tank Isolation Test", "objective": "Verify fuel tank isolation valves seal properly"},
            {"title": "Fuel Level Indication Test", "objective": "Validate fuel level sensors accuracy across range"},
        ]
    },
    # Landing Gear Tests
    {
        "category": "LandingGear",
        "test_type": "Functional",
        "scenarios": [
            {"title": "Gear Extension Time Test", "objective": "Measure landing gear extension time"},
            {"title": "Gear Lock Indication Test", "objective": "Verify gear lock indication system accuracy"},
            {"title": "Emergency Gear Extension Test", "objective": "Test emergency gear extension mechanism"},
        ]
    },
    # Hydraulic System Tests
    {
        "category": "Hydraulics",
        "test_type": "Performance",
        "scenarios": [
            {"title": "Hydraulic Pressure Test", "objective": "Verify hydraulic system maintains required pressure"},
            {"title": "Hydraulic Leak Detection Test", "objective": "Test hydraulic leak detection system sensitivity"},
        ]
    },
    # Environmental Control Tests
    {
        "category": "Environmental",
        "test_type": "Environmental",
        "scenarios": [
            {"title": "Cabin Pressurization Test", "objective": "Verify cabin maintains pressure at altitude"},
            {"title": "Temperature Control Test", "objective": "Validate cabin temperature control range"},
        ]
    },
    # Ice Protection Tests
    {
        "category": "IceProtection",
        "test_type": "Safety",
        "scenarios": [
            {"title": "Anti-Ice System Activation Test", "objective": "Test anti-ice system activation timing"},
            {"title": "De-Ice Boot Inflation Test", "objective": "Verify de-ice boots inflate properly"},
        ]
    },
    # Communication Tests
    {
        "category": "Communication",
        "test_type": "System",
        "scenarios": [
            {"title": "Radio Communication Range Test", "objective": "Verify radio communication range meets specifications"},
            {"title": "Emergency Locator Beacon Test", "objective": "Test ELT beacon signal strength"},
        ]
    },
    # Structural Tests
    {
        "category": "Structural",
        "test_type": "Stress",
        "scenarios": [
            {"title": "Wing Load Test", "objective": "Verify wing structure withstands design load limits"},
            {"title": "Fuselage Pressure Test", "objective": "Test fuselage pressure vessel integrity"},
            {"title": "Empennage Stress Test", "objective": "Test tail structure under design loads"},
        ]
    },
    # Additional Flight Control Tests
    {
        "category": "FlightControl",
        "test_type": "Safety",
        "scenarios": [
            {"title": "Control Surface Flutter Test", "objective": "Verify no flutter at maximum speed"},
            {"title": "Stall Warning System Test", "objective": "Test stall warning activation timing"},
            {"title": "Pitch Trim Authority Test", "objective": "Verify pitch trim system range and authority"},
        ]
    },
    # Additional Avionics Tests
    {
        "category": "Avionics",
        "test_type": "Integration",
        "scenarios": [
            {"title": "Autopilot Coupled Approach Test", "objective": "Verify autopilot performs coupled ILS approach"},
            {"title": "Weather Radar Detection Test", "objective": "Test weather radar precipitation detection"},
            {"title": "Flight Director Accuracy Test", "objective": "Verify flight director guidance accuracy"},
        ]
    },
    # Additional Electrical Tests
    {
        "category": "Electrical",
        "test_type": "Safety",
        "scenarios": [
            {"title": "Circuit Breaker Trip Test", "objective": "Verify circuit breakers trip at rated current"},
            {"title": "Emergency Power System Test", "objective": "Test emergency power system activation"},
            {"title": "Lightning Strike Protection Test", "objective": "Verify lightning protection system effectiveness"},
        ]
    },
    # Additional Fuel System Tests
    {
        "category": "FuelSystem",
        "test_type": "Safety",
        "scenarios": [
            {"title": "Fuel Crossfeed Test", "objective": "Verify fuel crossfeed system operation"},
            {"title": "Fuel Dump System Test", "objective": "Test emergency fuel dump rate and system"},
            {"title": "Fuel Filter Contamination Test", "objective": "Verify fuel filter bypass indication"},
        ]
    },
    # Additional Landing Gear Tests
    {
        "category": "LandingGear",
        "test_type": "Integration",
        "scenarios": [
            {"title": "Gear Retraction Test", "objective": "Verify landing gear retracts within time limit"},
            {"title": "Gear Door Sequence Test", "objective": "Test gear door sequencing during extension/retraction"},
            {"title": "Nose Wheel Steering Test", "objective": "Verify nose wheel steering authority and response"},
        ]
    },
    # Additional Hydraulic Tests
    {
        "category": "Hydraulics",
        "test_type": "Performance",
        "scenarios": [
            {"title": "Hydraulic Pump Performance Test", "objective": "Test hydraulic pump output under load"},
            {"title": "Hydraulic Reservoir Level Test", "objective": "Verify reservoir level sensing accuracy"},
            {"title": "Hydraulic Filter Bypass Test", "objective": "Test filter bypass indication system"},
        ]
    },
    # Additional Environmental Tests
    {
        "category": "Environmental",
        "test_type": "Functional",
        "scenarios": [
            {"title": "Air Conditioning Performance Test", "objective": "Verify A/C cooling capacity"},
            {"title": "Cabin Altitude Warning Test", "objective": "Test cabin altitude warning system"},
            {"title": "Bleed Air System Test", "objective": "Verify bleed air temperature regulation"},
        ]
    },
    # Additional Ice Protection Tests
    {
        "category": "IceProtection",
        "test_type": "Environmental",
        "scenarios": [
            {"title": "Windshield Anti-Ice Test", "objective": "Test windshield anti-ice heating effectiveness"},
            {"title": "Pitot Heat System Test", "objective": "Verify pitot tube heating prevents ice formation"},
            {"title": "Wing Ice Detection Test", "objective": "Test ice detection system sensitivity"},
        ]
    },
    # Additional Communication Tests
    {
        "category": "Communication",
        "test_type": "Integration",
        "scenarios": [
            {"title": "Intercom System Test", "objective": "Verify crew intercom audio quality"},
            {"title": "ATC Transponder Test", "objective": "Test transponder Mode C/S operation"},
            {"title": "Voice Recorder Test", "objective": "Verify cockpit voice recorder captures audio"},
        ]
    },
]

def generate_test_cases():
    """Generate 50 comprehensive test cases"""
    print("="*70)
    print("📝 GENERATING 50 COMPREHENSIVE TEST CASES")
    print("="*70)

    output_dir = Path("/Users/z/Documents/CALIDUS/backend/synthetic_requirements/test_cases")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Get all existing requirements to link to
    req_dir = Path("/Users/z/Documents/CALIDUS/backend/synthetic_requirements")
    all_requirements = []

    for req_type in ["AHLR", "System", "Technical", "Certification"]:
        req_path = req_dir / req_type
        if req_path.exists():
            for json_file in req_path.glob("*.json"):
                with open(json_file) as f:
                    req_data = json.load(f)
                    all_requirements.append({
                        "id": req_data["requirement_id"],
                        "category": req_data.get("category", "General"),
                        "type": req_data["type"]
                    })

    print(f"\n📦 Found {len(all_requirements)} requirements to link to")

    test_cases = []
    test_count = 0

    # Test statuses with realistic distribution
    statuses = [
        ("Passed", 0.60),      # 60% passed
        ("Failed", 0.10),      # 10% failed
        ("Not_Executed", 0.20), # 20% not executed
        ("In_Progress", 0.10)  # 10% in progress
    ]

    # Test priorities
    priorities = ["Critical", "High", "Medium", "Low"]

    # Generate test cases from scenarios
    for scenario_group in TEST_SCENARIOS:
        category = scenario_group["category"]
        test_type = scenario_group["test_type"]

        for scenario in scenario_group["scenarios"]:
            if test_count >= 50:
                break

            test_count += 1
            test_id = f"TC-{test_count:03d}"

            # Find related requirements
            related_reqs = [r["id"] for r in all_requirements if r["category"] == category]
            requirement_id = random.choice(related_reqs) if related_reqs else f"AHLR-{random.randint(1, 25):03d}"

            # Select status based on probability
            rand = random.random()
            cumulative = 0
            status = "Not_Executed"
            for stat, prob in statuses:
                cumulative += prob
                if rand <= cumulative:
                    status = stat
                    break

            # Generate realistic test data
            priority = random.choice(priorities)

            # Build test steps
            steps = generate_test_steps(scenario["title"], test_type)

            # Generate expected results
            expected_results = generate_expected_results(scenario["objective"])

            # Generate actual results if executed
            actual_results = None
            if status in ["Passed", "Failed"]:
                actual_results = generate_actual_results(status, scenario["objective"])

            # Build test case
            test_case = {
                "test_case_id": test_id,
                "title": scenario["title"],
                "description": f"Comprehensive test to {scenario['objective'].lower()}",
                "requirement_id": requirement_id,
                "test_type": test_type,
                "priority": priority,
                "status": status,
                "objective": scenario["objective"],
                "preconditions": generate_preconditions(category),
                "test_steps": steps,
                "expected_results": expected_results,
                "actual_results": actual_results,
                "test_data": generate_test_data(category),
                "environment": "Test Laboratory - Environmental Chamber",
                "tester": random.choice(["John Smith", "Maria Garcia", "David Chen", "Sarah Johnson"]),
                "execution_date": generate_execution_date(status),
                "duration_minutes": random.randint(30, 240),
                "automated": random.choice([True, False]),
                "notes": generate_notes(status),
                "created_date": "2025-01-15",
                "last_modified": datetime.now().strftime("%Y-%m-%d"),
                "version": "1.0"
            }

            test_cases.append(test_case)

            # Save individual test case
            output_file = output_dir / f"{test_id}.json"
            with open(output_file, 'w') as f:
                json.dump(test_case, f, indent=2)

            if test_count % 10 == 0:
                print(f"   ... generated {test_count} test cases")

    # Create index file
    index = {
        "document_title": "CALIDUS Test Cases Index",
        "generated_date": datetime.now().strftime("%Y-%m-%d"),
        "total_test_cases": len(test_cases),
        "test_cases_by_status": {
            "Passed": len([tc for tc in test_cases if tc["status"] == "Passed"]),
            "Failed": len([tc for tc in test_cases if tc["status"] == "Failed"]),
            "Not_Executed": len([tc for tc in test_cases if tc["status"] == "Not_Executed"]),
            "In_Progress": len([tc for tc in test_cases if tc["status"] == "In_Progress"])
        },
        "test_cases_by_type": {},
        "test_cases": [{"id": tc["test_case_id"], "title": tc["title"], "requirement": tc["requirement_id"]} for tc in test_cases]
    }

    # Count by type
    for tc in test_cases:
        test_type = tc["test_type"]
        index["test_cases_by_type"][test_type] = index["test_cases_by_type"].get(test_type, 0) + 1

    with open(output_dir / "INDEX.json", 'w') as f:
        json.dump(index, f, indent=2)

    print(f"\n✅ Generated {len(test_cases)} test cases")
    print(f"\n📊 Test Case Statistics:")
    print(f"   - Passed: {index['test_cases_by_status']['Passed']}")
    print(f"   - Failed: {index['test_cases_by_status']['Failed']}")
    print(f"   - Not Executed: {index['test_cases_by_status']['Not_Executed']}")
    print(f"   - In Progress: {index['test_cases_by_status']['In_Progress']}")
    print(f"\n📁 Files saved to: {output_dir}")

    print("\n" + "="*70)
    print("✅ TEST CASES GENERATED SUCCESSFULLY")
    print("="*70)

def generate_test_steps(title, test_type):
    """Generate realistic test steps"""
    base_steps = [
        "1. Power on all aircraft systems",
        "2. Perform pre-test system checks",
        "3. Configure test environment parameters"
    ]

    if "Failover" in title:
        base_steps.extend([
            "4. Monitor primary system operation",
            "5. Simulate primary system failure",
            "6. Observe automatic failover activation",
            "7. Verify backup system functionality",
            "8. Measure failover time"
        ])
    elif "Accuracy" in title or "Accuracy" in title:
        base_steps.extend([
            "4. Establish reference measurements",
            "5. Operate system under test conditions",
            "6. Record system output values",
            "7. Compare against reference standards",
            "8. Calculate accuracy deviation"
        ])
    elif "Response" in title:
        base_steps.extend([
            "4. Set baseline system state",
            "5. Apply test stimulus",
            "6. Measure response time",
            "7. Verify response within tolerance",
            "8. Repeat for statistical significance"
        ])
    else:
        base_steps.extend([
            "4. Execute primary test procedure",
            "5. Monitor system response",
            "6. Record test results",
            "7. Verify against specifications",
            "8. Document any anomalies"
        ])

    base_steps.append("9. Power down and secure test setup")
    return base_steps

def generate_expected_results(objective):
    """Generate expected results based on objective"""
    return [
        f"System shall {objective.lower()}",
        "No error messages or warnings displayed",
        "All parameters within acceptable tolerances",
        "System returns to normal operation"
    ]

def generate_actual_results(status, objective):
    """Generate actual results based on status"""
    if status == "Passed":
        return [
            f"System successfully {objective.lower()}",
            "No errors observed during test execution",
            "All measurements within specifications",
            "System behavior nominal"
        ]
    else:  # Failed
        return [
            f"System partially {objective.lower()}",
            "Intermittent warning message observed",
            "Response time exceeded specification by 12%",
            "Requires investigation and retest"
        ]

def generate_preconditions(category):
    """Generate realistic preconditions"""
    base = [
        "Aircraft in maintenance configuration",
        "All required test equipment calibrated and available",
        "Test personnel trained and certified",
        "Safety protocols reviewed and in place"
    ]

    category_specific = {
        "FlightControl": "Flight control surfaces in neutral position",
        "Avionics": "Avionics bay temperature stabilized at 20°C",
        "Electrical": "Main electrical bus energized and stable",
        "FuelSystem": "Fuel tanks filled to test level",
        "LandingGear": "Aircraft on jacks with gear safety pins installed",
        "Hydraulics": "Hydraulic fluid level within normal range",
        "Environmental": "Cabin sealed and pressurization system operational",
        "IceProtection": "Aircraft in cold chamber at -15°C",
        "Communication": "Radio interference minimized in test area",
        "Structural": "Strain gauges installed at critical points"
    }

    if category in category_specific:
        base.insert(1, category_specific[category])

    return base

def generate_test_data(category):
    """Generate test data requirements"""
    return {
        "temperature": f"{random.randint(-20, 40)}°C",
        "humidity": f"{random.randint(20, 80)}%",
        "pressure": f"{random.randint(900, 1100)} hPa",
        "test_duration": f"{random.randint(30, 180)} minutes"
    }

def generate_execution_date(status):
    """Generate execution date based on status"""
    if status in ["Passed", "Failed"]:
        # Recent execution
        days_ago = random.randint(1, 30)
        return (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
    elif status == "In_Progress":
        return datetime.now().strftime("%Y-%m-%d")
    else:  # Not Executed
        return None

def generate_notes(status):
    """Generate notes based on status"""
    notes_map = {
        "Passed": "Test completed successfully. All acceptance criteria met.",
        "Failed": "Test failed due to response time exceeding specification. Defect report DR-2025-0123 filed.",
        "Not_Executed": "Scheduled for execution in next test cycle.",
        "In_Progress": "Test execution ongoing. Preliminary results look promising."
    }
    return notes_map.get(status, "")

if __name__ == "__main__":
    generate_test_cases()
