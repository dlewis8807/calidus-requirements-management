# Phase 2 Implementation Plan - CALIDUS Core Features
**Start Date**: October 19, 2025
**Duration**: 4 weeks (Weeks 4-7)
**Status**: 📋 READY TO START

---

## Executive Summary

With Week 3 complete and the foundation fully operational, Phase 2 focuses on building the **core differentiating features** that make CALIDUS a next-generation requirements management system. We'll add interactive visualizations, AI-powered analysis, and advanced compliance features.

**Key Objectives:**
1. Interactive traceability visualizations with D3.js/Cytoscape
2. Compliance dashboard with regulatory mapping
3. Impact analysis tool for change management
4. Test coverage analyzer with heatmaps
5. AI-powered ambiguity detection (NLP)

---

## Current System Status (Week 3 Complete)

### ✅ What We Have
- **Backend API**: Fully functional with 16,500 requirements, 29,153 test cases
- **Database**: PostgreSQL with comprehensive schema
- **Frontend**: Complete dashboard, requirements list, test cases, user management
- **Authentication**: JWT-based with role management (admin, engineer, viewer)
- **Filtering**: Advanced filtering working on all pages
- **Real Data**: Synthetic aerospace requirements from 14 CFR Part 23

### 📊 Current Data Volume
- Requirements: 16,500 (AHLR: 500, System: 5,000, Technical: 10,000, Certification: 1,000)
- Test Cases: 29,153
- Traceability Links: Existing parent/child relationships
- Users: 3 (admin, engineer, viewer)

---

## Phase 2 Strategy: Prioritized Feature Development

After analyzing the original plan and current state, I recommend this prioritized approach:

### **Priority 1: Interactive Traceability (Week 4)** 🎯
**WHY FIRST**: Core differentiator, high visual impact, uses existing data
- Most impressive demo feature
- Leverages existing traceability data
- Clear ROI demonstration

### **Priority 2: Compliance Dashboard (Week 5)** 🎯
**WHY SECOND**: Critical aerospace requirement, builds on regulatory data
- Essential for aerospace industry
- Uses existing regulatory_document field
- Demonstrates regulatory expertise

### **Priority 3: Impact Analysis (Week 6)** 🎯
**WHY THIRD**: High-value feature, enables change management
- Practical tool for engineers
- Uses traceability graph
- Shows AI/algorithm capability

### **Priority 4: Test Coverage Analyzer (Week 7)** 🎯
**WHY FOURTH**: Quality metrics, completes the suite
- Demonstrates test management
- Visual heatmaps are compelling
- Uses existing test case data

### **Optional Extension: Ambiguity Detection** 🔮
**IF TIME PERMITS**: Advanced NLP feature
- Requires ML model integration
- Can be Phase 3 feature
- Demonstrates AI capability

---

## Week 4: Interactive Traceability Visualization

### Objective
Build an interactive, zoomable traceability graph showing requirement relationships with filtering, search, and export capabilities.

### Features to Implement

#### 4.1 Traceability Graph Visualization
**Page**: `/app/dashboard/traceability/graph/page.tsx`

**Libraries to Install**:
```bash
npm install react-flow-renderer
npm install d3
npm install cytoscape cytoscape-fcose
npm install @types/cytoscape
```

**Features**:
- **Interactive Network Graph**:
  - Nodes: Requirements (color-coded by type)
  - Edges: Traceability links (parent/child)
  - Automatic layout using force-directed algorithm

- **Visualization Controls**:
  - Zoom in/out with mouse wheel
  - Pan by dragging
  - Center on specific requirement
  - Fit to screen
  - Expand/collapse node children

- **Filtering**:
  - Filter by requirement type
  - Filter by status
  - Show/hide orphaned requirements
  - Show/hide requirements without tests

- **Interaction**:
  - Click node to see requirement details in side panel
  - Double-click to navigate to requirement detail page
  - Hover to see quick preview
  - Right-click for context menu (View, Edit, Add Child)

- **Export**:
  - Export to PNG
  - Export to SVG
  - Export to PDF
  - Export data to JSON

#### 4.2 Traceability Matrix (Enhanced)
**Page**: `/app/dashboard/traceability/matrix/page.tsx`

**Features**:
- **Matrix View**:
  - Rows: Parent requirements (AHLR, System)
  - Columns: Child requirements (Technical, Test Cases)
  - Cells: Show link status (✓ linked, ✗ missing, ⚠ incomplete)

- **Gap Analysis**:
  - Highlight orphaned requirements (red)
  - Highlight missing test coverage (yellow)
  - Show completion percentage

- **Filtering**:
  - Filter by category
  - Filter by priority
  - Show only gaps

- **Export**:
  - Export to Excel (.xlsx)
  - Export to CSV
  - Export gap report to PDF

#### 4.3 Requirement Hierarchy Tree
**Component**: `/components/traceability/HierarchyTree.tsx`

**Features**:
- Collapsible tree view
- Indent levels (AHLR → System → Technical → Test Cases)
- Color-coded icons
- Drag-and-drop to create links (optional)

### API Endpoints Needed (Backend)

**New Endpoints**:
```python
# backend/app/api/traceability.py

GET /api/traceability/graph
  - Returns graph data: nodes (requirements) and edges (links)
  - Query params: ?type=AHLR&status=approved&include_tests=true
  - Response: { nodes: [], edges: [] }

GET /api/traceability/orphaned
  - Returns requirements with no parent or child links
  - Response: [{ id, requirement_id, title, type, ... }]

GET /api/traceability/gaps
  - Returns requirements missing test coverage
  - Response: { missing_tests: [], missing_parents: [], missing_children: [] }

GET /api/traceability/export/matrix
  - Returns traceability matrix data for export
  - Response: CSV or Excel file download
```

### Database Queries Needed
```sql
-- Find orphaned requirements (no parent or child links)
SELECT r.* FROM requirements r
LEFT JOIN traceability_links tl_parent ON r.id = tl_parent.target_id
LEFT JOIN traceability_links tl_child ON r.id = tl_child.source_id
WHERE tl_parent.id IS NULL AND tl_child.id IS NULL;

-- Find requirements without test coverage
SELECT r.* FROM requirements r
LEFT JOIN test_cases tc ON r.id = tc.requirement_id
WHERE tc.id IS NULL;

-- Build graph data (nodes and edges)
SELECT
  r.id, r.requirement_id, r.title, r.type, r.status,
  tl.id as link_id, tl.source_id, tl.target_id, tl.link_type
FROM requirements r
LEFT JOIN traceability_links tl ON r.id = tl.source_id OR r.id = tl.target_id;
```

### Implementation Steps (Week 4)

**Day 1-2: Setup & Backend**
1. Install frontend dependencies (react-flow-renderer, cytoscape)
2. Create new traceability API endpoints
3. Write SQL queries for graph data, orphaned requirements, gaps
4. Test API endpoints with Postman/Swagger

**Day 3-4: Basic Graph Visualization**
5. Create graph page component
6. Implement basic Cytoscape.js visualization
7. Fetch and display requirement nodes
8. Draw edges for traceability links
9. Add zoom/pan controls

**Day 5-6: Interaction & Filtering**
10. Add node click handler (show details panel)
11. Implement filtering controls
12. Add search functionality
13. Highlight orphaned requirements
14. Add expand/collapse for large graphs

**Day 7: Export & Polish**
15. Implement export to PNG/SVG
16. Add matrix export to Excel
17. Performance optimization (lazy loading for large graphs)
18. Add loading states and error handling

### Success Criteria (Week 4)
- ✅ Interactive graph with 16,500 requirements rendered efficiently
- ✅ Zoom/pan/filter controls working smoothly
- ✅ Click to view requirement details
- ✅ Gap analysis highlights visible
- ✅ Export to PNG/SVG/Excel working
- ✅ Performance: Graph loads in <3 seconds
- ✅ Graph updates in real-time when filtering

---

## Week 5: Compliance Dashboard

### Objective
Build a comprehensive compliance dashboard showing requirement coverage against aerospace regulations (FAA 14 CFR Part 23, EASA CS-23, UAE GCAA).

### Features to Implement

#### 5.1 Compliance Overview Dashboard
**Page**: `/app/dashboard/compliance/page.tsx`

**Features**:
- **Coverage Metrics**:
  - Total requirements mapped to regulations
  - Coverage percentage by regulation (FAA, EASA, UAE)
  - Gaps by regulation
  - Compliance score (0-100)

- **Visualizations**:
  - Donut chart: Requirements by regulation
  - Bar chart: Coverage by regulation section
  - Progress bars: Compliance completion
  - Heatmap: Coverage by category × regulation

- **Regulation Cards**:
  - FAA 14 CFR Part 23 (requirements: X, coverage: Y%)
  - EASA CS-23 (requirements: X, coverage: Y%)
  - UAE GCAA UAEMAR-21 (requirements: X, coverage: Y%)
  - DO-178C (software requirements)

- **Gap Analysis**:
  - List of regulations with no mapped requirements
  - List of requirements with no regulation mapping
  - Suggested mappings (AI-powered - optional)

#### 5.2 Regulation Detail View
**Page**: `/app/dashboard/compliance/[regulation]/page.tsx`

**Example**: `/dashboard/compliance/14-CFR-Part-23`

**Features**:
- **Section Breakdown**:
  - 14 CFR §23.2100 - Weight and loading
  - 14 CFR §23.2105 - Performance data
  - 14 CFR §23.2110 - Stall speed
  - ... (all sections)

- **For Each Section**:
  - Number of requirements mapped
  - List of mapped requirements (with links)
  - Compliance status (Compliant, Partial, Non-compliant)
  - Missing requirements

- **Requirement Mapping Table**:
  - Columns: Requirement ID, Title, Type, Status, Regulation Section, Page
  - Filter by section, status, type
  - Export to Excel

#### 5.3 Regulation Mapper
**Component**: `/components/compliance/RegulationMapper.tsx`

**Features**:
- **Manual Mapping**:
  - Search for requirement
  - Select regulation from dropdown
  - Enter section number
  - Enter page number
  - Add rationale (optional)

- **Bulk Upload**:
  - Upload CSV with mappings (requirement_id, regulation, section, page)
  - Validate and preview before import
  - Import with conflict resolution

- **Auto-Suggestion** (AI-powered - optional):
  - Analyze requirement text
  - Suggest relevant regulation sections
  - Confidence score
  - User accepts/rejects

### API Endpoints Needed (Backend)

**New Endpoints**:
```python
# backend/app/api/compliance.py (NEW FILE)

GET /api/compliance/overview
  - Returns overall compliance metrics
  - Response: { total_requirements, mapped_requirements, coverage_percentage, by_regulation: {...} }

GET /api/compliance/regulations
  - Returns list of all regulations in system
  - Response: [{ id, name, abbreviation, authority, requirement_count, coverage_percentage }]

GET /api/compliance/regulations/{regulation_id}
  - Returns detailed breakdown for specific regulation
  - Response: { regulation_info, sections: [{ section, title, requirement_count, requirements: [...] }] }

GET /api/compliance/gaps
  - Returns unmapped requirements and regulations
  - Response: { unmapped_requirements: [], uncovered_sections: [] }

POST /api/compliance/mappings
  - Create new regulation mapping
  - Body: { requirement_id, regulation, section, page, rationale }

PUT /api/compliance/mappings/{mapping_id}
  - Update existing mapping

DELETE /api/compliance/mappings/{mapping_id}
  - Remove mapping

POST /api/compliance/mappings/bulk
  - Bulk upload mappings from CSV
  - Body: FormData with CSV file
```

### Database Schema Updates

**New Table**: `regulation_mappings`
```sql
CREATE TABLE regulation_mappings (
    id SERIAL PRIMARY KEY,
    requirement_id INTEGER NOT NULL REFERENCES requirements(id) ON DELETE CASCADE,
    regulation VARCHAR(100) NOT NULL,  -- e.g., "14 CFR Part 23"
    section VARCHAR(50),               -- e.g., "23.2110"
    page INTEGER,                      -- Page number in regulation document
    rationale TEXT,                    -- Why this requirement maps to this regulation
    created_by_id INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_regulation_mappings_requirement ON regulation_mappings(requirement_id);
CREATE INDEX idx_regulation_mappings_regulation ON regulation_mappings(regulation);
```

**Data Population**:
- Extract existing `regulatory_document`, `regulatory_section`, `regulatory_page` from requirements table
- Populate regulation_mappings table with this data
- Keep original fields for backward compatibility

### Implementation Steps (Week 5)

**Day 1-2: Database & Backend**
1. Create regulation_mappings table migration
2. Create compliance API endpoints
3. Write SQL queries for coverage metrics
4. Populate initial mappings from existing data
5. Test API endpoints

**Day 3-4: Compliance Dashboard**
6. Create compliance overview page
7. Implement coverage metric cards
8. Add donut/bar charts for regulation breakdown
9. Create gap analysis section
10. Add regulation cards with drill-down links

**Day 5-6: Regulation Detail View**
11. Create regulation detail page
12. Implement section breakdown
13. Add requirement mapping table
14. Implement filtering and search
15. Add export to Excel

**Day 7: Mapper & Polish**
16. Create regulation mapper component
17. Implement manual mapping form
18. Add CSV bulk upload
19. Add validation and error handling
20. Performance testing with large datasets

### Success Criteria (Week 5)
- ✅ Compliance dashboard showing coverage metrics
- ✅ Drill-down into specific regulations (14 CFR Part 23, CS-23)
- ✅ Gap analysis identifying unmapped requirements
- ✅ Manual mapping interface working
- ✅ Bulk CSV upload working
- ✅ Export compliance report to Excel
- ✅ Real data: 1,000 certification requirements mapped

---

## Week 6: Impact Analysis Tool

### Objective
Build an impact analysis tool that traces the upstream and downstream effects of requirement changes, showing affected requirements, tests, and associated risks.

### Features to Implement

#### 6.1 Impact Analysis Dashboard
**Page**: `/app/dashboard/impact-analysis/page.tsx`

**Features**:
- **Change Selection**:
  - Select requirement to analyze
  - Enter proposed change description
  - Set change severity (Low, Medium, High, Critical)

- **Impact Visualization**:
  - **Upstream Impact** (parent requirements affected):
    - Visual tree showing affected AHLR → System requirements
    - Number of parent requirements impacted
    - Compliance implications

  - **Downstream Impact** (child requirements affected):
    - Visual tree showing affected Technical specs → Test cases
    - Number of child requirements impacted
    - Number of test cases needing updates

  - **Lateral Impact** (same-level requirements):
    - Requirements with similar regulatory mappings
    - Requirements in same category

- **Impact Metrics**:
  - Total requirements affected
  - Total test cases needing re-execution
  - Estimated effort (in story points or hours)
  - Risk score (0-100)

- **Impact Graph**:
  - Interactive graph centered on changed requirement
  - Color-coded by impact level (green → yellow → red)
  - Expandable nodes
  - Highlight critical path

#### 6.2 Change Request Workflow
**Page**: `/app/dashboard/impact-analysis/change-request/page.tsx`

**Features**:
- **Create Change Request**:
  - Requirement to change
  - Change description
  - Rationale
  - Impact analysis summary
  - Affected requirements list
  - Affected test cases list

- **Approval Workflow** (Optional):
  - Submit for review
  - Assign to approver
  - Approval/rejection with comments
  - Track change history

#### 6.3 Risk Assessment
**Component**: `/components/impact/RiskAssessment.tsx`

**Features**:
- **Risk Calculation**:
  - Based on number of affected requirements
  - Based on requirement criticality (CRITICAL > HIGH > MEDIUM > LOW)
  - Based on number of affected test cases
  - Based on compliance implications

- **Risk Score** (0-100):
  - 0-25: Low risk (green)
  - 26-50: Medium risk (yellow)
  - 51-75: High risk (orange)
  - 76-100: Critical risk (red)

- **Mitigation Suggestions**:
  - Recommended test cases to run
  - Compliance checks needed
  - Stakeholders to notify

### API Endpoints Needed (Backend)

**New Endpoints**:
```python
# backend/app/api/impact_analysis.py (NEW FILE)

POST /api/impact-analysis/analyze
  - Analyzes impact of changing a requirement
  - Body: { requirement_id, change_description, severity }
  - Response: {
      upstream_impact: [...],
      downstream_impact: [...],
      lateral_impact: [...],
      affected_requirements_count,
      affected_test_cases_count,
      risk_score,
      estimated_effort_hours
    }

GET /api/impact-analysis/graph/{requirement_id}
  - Returns graph data for impact visualization
  - Query params: ?depth=3
  - Response: { nodes: [], edges: [], center_node_id }

POST /api/impact-analysis/change-requests
  - Create a change request
  - Body: { requirement_id, change_description, rationale, impact_summary }

GET /api/impact-analysis/change-requests
  - List all change requests
  - Response: [{ id, requirement_id, status, created_at, ... }]

PUT /api/impact-analysis/change-requests/{id}/approve
  - Approve a change request

PUT /api/impact-analysis/change-requests/{id}/reject
  - Reject a change request
```

### Algorithm: Impact Analysis

**Upstream Traversal** (find affected parents):
```python
def find_upstream_impact(requirement_id, depth=10):
    """
    Traverse parent links up to specified depth
    Returns list of parent requirements that would be affected
    """
    affected = []
    queue = [(requirement_id, 0)]
    visited = set()

    while queue:
        req_id, current_depth = queue.pop(0)
        if current_depth >= depth or req_id in visited:
            continue

        visited.add(req_id)

        # Find parent links
        parents = db.query(TraceabilityLink).filter(
            TraceabilityLink.target_id == req_id
        ).all()

        for parent_link in parents:
            parent_req = db.query(Requirement).get(parent_link.source_id)
            affected.append({
                'requirement': parent_req,
                'depth': current_depth + 1,
                'link_type': parent_link.link_type
            })
            queue.append((parent_req.id, current_depth + 1))

    return affected
```

**Downstream Traversal** (find affected children):
```python
def find_downstream_impact(requirement_id, depth=10):
    """
    Traverse child links down to specified depth
    Includes test cases
    """
    affected = []
    affected_tests = []
    queue = [(requirement_id, 0)]
    visited = set()

    while queue:
        req_id, current_depth = queue.pop(0)
        if current_depth >= depth or req_id in visited:
            continue

        visited.add(req_id)

        # Find child links
        children = db.query(TraceabilityLink).filter(
            TraceabilityLink.source_id == req_id
        ).all()

        for child_link in children:
            child_req = db.query(Requirement).get(child_link.target_id)
            affected.append({
                'requirement': child_req,
                'depth': current_depth + 1,
                'link_type': child_link.link_type
            })
            queue.append((child_req.id, current_depth + 1))

        # Find test cases
        tests = db.query(TestCase).filter(
            TestCase.requirement_id == req_id
        ).all()
        affected_tests.extend(tests)

    return affected, affected_tests
```

**Risk Score Calculation**:
```python
def calculate_risk_score(upstream_count, downstream_count, test_count, priority):
    """
    Calculate risk score (0-100) based on impact metrics
    """
    # Weight factors
    upstream_weight = 0.3
    downstream_weight = 0.3
    test_weight = 0.2
    priority_weight = 0.2

    # Normalize counts (assuming max 100 requirements affected)
    upstream_score = min(upstream_count / 100, 1.0) * 100
    downstream_score = min(downstream_count / 100, 1.0) * 100
    test_score = min(test_count / 200, 1.0) * 100

    # Priority score
    priority_scores = {
        'CRITICAL': 100,
        'HIGH': 75,
        'MEDIUM': 50,
        'LOW': 25
    }
    priority_score = priority_scores.get(priority, 50)

    # Weighted sum
    risk_score = (
        upstream_score * upstream_weight +
        downstream_score * downstream_weight +
        test_score * test_weight +
        priority_score * priority_weight
    )

    return round(risk_score, 2)
```

### Implementation Steps (Week 6)

**Day 1-2: Backend Algorithm**
1. Create impact_analysis API endpoints
2. Implement upstream/downstream traversal algorithms
3. Implement risk score calculation
4. Write tests for traversal algorithms
5. Test with realistic data

**Day 3-4: Impact Visualization**
6. Create impact analysis page
7. Implement requirement selection
8. Fetch and display impact analysis results
9. Create impact graph visualization
10. Add impact metrics cards

**Day 5-6: Change Request Workflow**
11. Create change request form
12. Implement change request submission
13. Create change request list view
14. Add approval/rejection workflow (admin only)

**Day 7: Risk & Polish**
15. Implement risk assessment component
16. Add mitigation suggestions
17. Add export impact report to PDF
18. Performance optimization
19. Add loading states and error handling

### Success Criteria (Week 6)
- ✅ Impact analysis working for any requirement
- ✅ Upstream/downstream traversal accurate
- ✅ Risk score calculated correctly
- ✅ Impact graph visualization clear and interactive
- ✅ Change request workflow functional
- ✅ Export impact report to PDF
- ✅ Performance: Analysis completes in <2 seconds

---

## Week 7: Test Coverage Analyzer

### Objective
Build a comprehensive test coverage analyzer with heatmaps, gap identification, and coverage trends to ensure requirements are adequately tested.

### Features to Implement

#### 7.1 Coverage Dashboard
**Page**: `/app/dashboard/coverage/page.tsx`

**Features**:
- **Coverage Metrics**:
  - Overall coverage percentage (X% of requirements have tests)
  - Coverage by requirement type (AHLR: X%, System: Y%, Technical: Z%)
  - Coverage by priority (Critical: X%, High: Y%, Medium: Z%, Low: W%)
  - Coverage by category (FlightControl: X%, Navigation: Y%, ...)

- **Visualizations**:
  - **Coverage Heatmap**:
    - Rows: Requirement types (AHLR, System, Technical, Certification)
    - Columns: Priority levels (Critical, High, Medium, Low)
    - Cells: Color-coded by coverage percentage (red < 50%, yellow 50-80%, green > 80%)

  - **Coverage Trend Chart**:
    - Line chart showing coverage over time
    - Historical coverage data (if tracked)
    - Target coverage line (e.g., 80%)

  - **Category Coverage Bar Chart**:
    - Horizontal bars for each category
    - Show tested vs untested requirements

- **Gap Analysis**:
  - List of requirements without test cases
  - Prioritized by criticality (Critical first)
  - Filter by type, status, category
  - Bulk assign test cases

#### 7.2 Coverage Detail View
**Page**: `/app/dashboard/coverage/[type]/page.tsx`

**Example**: `/dashboard/coverage/AHLR`

**Features**:
- **Requirement List**:
  - Filter: With tests / Without tests / All
  - Sort by: ID, Title, Priority, Test count
  - Columns: Requirement ID, Title, Priority, Test Count, Coverage Status

- **For Each Requirement**:
  - Test case count badge
  - Coverage indicator (icon: ✓ tested, ✗ not tested, ⚠ partial)
  - Quick action: Add test case

- **Test Effectiveness**:
  - Pass rate for each requirement's tests
  - Last execution date
  - Automated vs manual test ratio

#### 7.3 Test Coverage Heatmap
**Component**: `/components/coverage/CoverageHeatmap.tsx`

**Libraries**:
```bash
npm install recharts
npm install react-grid-heatmap
```

**Features**:
- 2D heatmap: Type × Priority
- Color scale: Red (0%) → Yellow (50%) → Green (100%)
- Tooltip on hover: Show exact percentage and count
- Click cell to drill down to requirements
- Export heatmap to PNG

#### 7.4 Test Generation Suggestions
**Component**: `/components/coverage/TestSuggestions.tsx`

**Features**:
- **AI-Powered Suggestions** (Optional):
  - Analyze requirement text
  - Suggest test scenarios
  - Suggest test type (unit, integration, system)

- **Template-Based Suggestions**:
  - For AHLR: System-level test
  - For System: Integration test
  - For Technical: Unit test

- **One-Click Test Creation**:
  - Pre-fill test case form with suggestion
  - User reviews and submits

### API Endpoints Needed (Backend)

**New Endpoints**:
```python
# backend/app/api/coverage.py (NEW FILE)

GET /api/coverage/overview
  - Returns overall coverage metrics
  - Response: {
      total_requirements,
      tested_requirements,
      coverage_percentage,
      by_type: { AHLR: {...}, System: {...}, ... },
      by_priority: { Critical: {...}, High: {...}, ... },
      by_category: { FlightControl: {...}, ... }
    }

GET /api/coverage/heatmap
  - Returns heatmap data: type × priority
  - Response: {
      rows: ['AHLR', 'System', 'Technical', 'Certification'],
      columns: ['Critical', 'High', 'Medium', 'Low'],
      data: [[85, 72, 68, 90], [78, 65, 55, 60], ...]
    }

GET /api/coverage/gaps
  - Returns requirements without test cases
  - Query params: ?type=AHLR&priority=Critical
  - Response: [{ requirement_id, title, type, priority, category }]

GET /api/coverage/trends
  - Returns historical coverage data (if tracked)
  - Response: [{ date: '2025-10-01', coverage_percentage: 65 }, ...]

POST /api/coverage/suggestions
  - Generate test case suggestions for a requirement
  - Body: { requirement_id }
  - Response: [{ test_title, test_type, test_steps, expected_results }]
```

### Database Schema Updates

**New Table**: `coverage_history` (optional, for trends)
```sql
CREATE TABLE coverage_history (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    total_requirements INTEGER NOT NULL,
    tested_requirements INTEGER NOT NULL,
    coverage_percentage DECIMAL(5,2) NOT NULL,
    by_type JSONB,  -- Store breakdown by type
    by_priority JSONB,  -- Store breakdown by priority
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_coverage_history_date ON coverage_history(date);
```

**Populate Coverage History** (cron job or manual):
```python
# Run daily to track coverage over time
def record_coverage_snapshot():
    stats = calculate_coverage_stats()
    coverage_record = CoverageHistory(
        date=datetime.now().date(),
        total_requirements=stats['total'],
        tested_requirements=stats['tested'],
        coverage_percentage=stats['percentage'],
        by_type=stats['by_type'],
        by_priority=stats['by_priority']
    )
    db.add(coverage_record)
    db.commit()
```

### SQL Queries

**Coverage by Type and Priority**:
```sql
SELECT
    r.type,
    r.priority,
    COUNT(r.id) as total_requirements,
    COUNT(DISTINCT tc.requirement_id) as tested_requirements,
    ROUND(COUNT(DISTINCT tc.requirement_id)::DECIMAL / COUNT(r.id) * 100, 2) as coverage_percentage
FROM requirements r
LEFT JOIN test_cases tc ON r.id = tc.requirement_id
GROUP BY r.type, r.priority
ORDER BY r.type, r.priority;
```

**Requirements Without Tests**:
```sql
SELECT
    r.id,
    r.requirement_id,
    r.title,
    r.type,
    r.priority,
    r.category
FROM requirements r
LEFT JOIN test_cases tc ON r.id = tc.requirement_id
WHERE tc.id IS NULL
ORDER BY
    CASE r.priority
        WHEN 'Critical' THEN 1
        WHEN 'High' THEN 2
        WHEN 'Medium' THEN 3
        WHEN 'Low' THEN 4
    END;
```

### Implementation Steps (Week 7)

**Day 1-2: Backend & Queries**
1. Create coverage API endpoints
2. Write SQL queries for coverage metrics
3. Implement heatmap data generation
4. Create coverage_history table (optional)
5. Test API endpoints

**Day 3-4: Coverage Dashboard**
6. Create coverage overview page
7. Implement coverage metric cards
8. Add coverage heatmap component
9. Add category coverage bar chart
10. Add gap analysis section

**Day 5-6: Detail View & Suggestions**
11. Create coverage detail view by type
12. Implement requirement list with filter/sort
13. Add test effectiveness indicators
14. Create test suggestion component
15. Implement one-click test creation

**Day 7: Trends & Polish**
16. Add coverage trend chart (if data available)
17. Implement export heatmap to PNG
18. Add export gap report to Excel
19. Performance optimization
20. Add loading states and error handling

### Success Criteria (Week 7)
- ✅ Coverage dashboard with accurate metrics
- ✅ Heatmap showing coverage by type × priority
- ✅ Gap analysis listing untested requirements
- ✅ Drill-down to specific requirement types
- ✅ Test suggestions working (template-based)
- ✅ Export heatmap to PNG
- ✅ Export gap report to Excel
- ✅ Performance: Dashboard loads in <2 seconds

---

## Technical Dependencies & Installation

### Frontend Libraries to Add (Phase 2)

```bash
# Week 4: Traceability Visualization
npm install react-flow-renderer
npm install d3
npm install cytoscape cytoscape-fcose
npm install @types/cytoscape
npm install file-saver  # For export functionality
npm install html2canvas  # For PNG export

# Week 5: Compliance Dashboard
npm install xlsx  # For Excel export
npm install recharts  # Charts (already installed in Week 3)
npm install jspdf  # For PDF export (optional)

# Week 6: Impact Analysis
# Uses existing libraries (react-flow-renderer, recharts)

# Week 7: Coverage Analyzer
npm install react-grid-heatmap
# recharts already installed
```

### Backend Dependencies

```bash
# Python packages (add to requirements.txt)
pip install openpyxl  # Excel file generation
pip install pandas  # Data manipulation for exports
pip install networkx  # Graph algorithms for impact analysis
pip install reportlab  # PDF generation (optional)
```

### Database Migrations

```bash
# Week 5: Compliance
alembic revision -m "create_regulation_mappings_table"
alembic upgrade head

# Week 7: Coverage History (optional)
alembic revision -m "create_coverage_history_table"
alembic upgrade head
```

---

## Testing Strategy

### Unit Tests
- Each new API endpoint must have tests
- Test graph traversal algorithms
- Test risk score calculation
- Test coverage calculation
- Target: 90% coverage for new code

### Integration Tests
- Test full impact analysis flow
- Test compliance mapping workflow
- Test export functionality (Excel, PDF)

### Performance Tests
- Graph with 10,000+ nodes renders in <5s
- Impact analysis completes in <2s
- Coverage dashboard loads in <2s
- Heatmap renders in <1s

### User Acceptance Testing
- Demo with stakeholders weekly
- Collect feedback on visualizations
- Iterate on UX improvements

---

## Risk Mitigation

### Technical Risks

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Large graph performance issues | High | Implement lazy loading, pagination, depth limits |
| Export file size too large | Medium | Add compression, pagination for exports |
| NLP model latency (ambiguity detection) | Low | Make feature optional, use caching |
| Database query performance | Medium | Add indexes, optimize queries, use caching |

### Schedule Risks

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Feature complexity underestimated | High | Prioritize MVP features, defer nice-to-haves |
| Dependency on external APIs | Low | Use mock data for development |
| Testing time insufficient | Medium | Continuous testing, automated tests |

---

## Success Metrics (Phase 2 Complete)

### Functional Metrics
- ✅ Traceability graph renders 16,500+ requirements
- ✅ Compliance dashboard shows coverage for 3+ regulations
- ✅ Impact analysis working for all requirement types
- ✅ Coverage analyzer identifies gaps accurately
- ✅ All exports working (PNG, SVG, Excel, PDF)

### Performance Metrics
- ✅ Graph loads in <5 seconds
- ✅ Dashboard loads in <2 seconds
- ✅ API responses in <200ms (95th percentile)
- ✅ No memory leaks or crashes

### Quality Metrics
- ✅ 90% test coverage for new code
- ✅ Zero critical bugs
- ✅ Accessibility standards met (WCAG 2.1 AA)

---

## Optional Extensions (If Time Permits)

### 1. AI-Powered Ambiguity Detection
**Estimated Effort**: 2-3 days

**Features**:
- NLP analysis of requirement text
- Identify ambiguous words ("shall", "should", "may")
- Detect passive voice
- Check for vague quantifiers ("approximately", "several")
- Readability score (Flesch-Kincaid)
- Suggestions for improvement

**Libraries**:
```bash
pip install transformers sentence-transformers
pip install spacy
python -m spacy download en_core_web_sm
```

**API Endpoint**:
```python
POST /api/analysis/ambiguity
  - Analyzes requirement text for ambiguity
  - Body: { requirement_id }
  - Response: {
      ambiguity_score: 0-100,
      issues: [{ type, text, suggestion, severity }],
      readability_score: 0-100
    }
```

### 2. Real-Time Collaboration
**Estimated Effort**: 3-4 days

**Features**:
- WebSocket connection for live updates
- Show who's viewing/editing a requirement
- Real-time notifications for changes
- Collaborative editing (like Google Docs)

**Technology**:
```bash
npm install socket.io-client
pip install python-socketio
```

### 3. Advanced Export Features
**Estimated Effort**: 1-2 days

**Features**:
- Export traceability graph to Visio
- Export compliance report to Word
- Custom report templates
- Scheduled automated reports (email)

---

## Phase 2 Deliverables Checklist

### Week 4: Traceability
- [ ] Interactive graph with zoom/pan
- [ ] Filter by type, status, category
- [ ] Click node for details
- [ ] Export to PNG/SVG
- [ ] Matrix export to Excel
- [ ] Orphaned requirements highlighted

### Week 5: Compliance
- [ ] Compliance overview dashboard
- [ ] Coverage by regulation
- [ ] Drill-down to regulation sections
- [ ] Gap analysis
- [ ] Manual mapping interface
- [ ] Bulk CSV upload
- [ ] Export compliance report

### Week 6: Impact Analysis
- [ ] Impact analysis for any requirement
- [ ] Upstream/downstream visualization
- [ ] Risk score calculation
- [ ] Change request workflow
- [ ] Export impact report

### Week 7: Coverage
- [ ] Coverage overview dashboard
- [ ] Coverage heatmap (type × priority)
- [ ] Gap analysis (untested requirements)
- [ ] Coverage trends (if data available)
- [ ] Test suggestions
- [ ] Export heatmap and gap report

---

## Next Steps After Phase 2

### Phase 3 (Weeks 8-10): AI/ML Integration
- Sentence Transformers for semantic search
- Vector database (Weaviate) for similarity
- AI trace link suggestions
- Requirement categorization
- Duplication detection

### Phase 4 (Weeks 11-12): Polish & Deployment
- Production deployment (AWS/Azure/GCP)
- Performance optimization
- Security audit
- User acceptance testing
- Documentation

---

## Getting Started (Week 4, Day 1)

### Immediate Actions

1. **Install Dependencies**:
```bash
cd frontend
npm install react-flow-renderer d3 cytoscape cytoscape-fcose file-saver html2canvas
```

2. **Create Traceability Graph Backend**:
```bash
cd backend
# Edit backend/app/api/traceability.py to add new endpoints
```

3. **Create Frontend Page**:
```bash
mkdir -p frontend/app/dashboard/traceability/graph
touch frontend/app/dashboard/traceability/graph/page.tsx
```

4. **Test with Current Data**:
- Run backend: `docker compose up -d`
- Run frontend: `cd frontend && npm run dev`
- Navigate to dashboard and test existing traceability features

---

**Ready to start Week 4: Interactive Traceability Visualization!** 🚀

Let's build the most impressive feature first - the interactive graph that will wow stakeholders and demonstrate the power of CALIDUS.
