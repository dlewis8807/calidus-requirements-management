# Impact Analysis - Implementation Plan

**Project:** CALIDUS - Requirements Management & Traceability Assistant
**Feature:** Impact Analysis for Requirement Changes
**Phase:** Phase 2, Week 6
**Version:** 1.0
**Date:** October 21, 2025
**Status:** Implementation Ready

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Feature Overview](#feature-overview)
3. [System Architecture](#system-architecture)
4. [Technical Design](#technical-design)
5. [API Endpoints](#api-endpoints)
6. [Database Schema](#database-schema)
7. [Frontend Components](#frontend-components)
8. [Implementation Phases](#implementation-phases)
9. [Testing Strategy](#testing-strategy)
10. [Success Criteria](#success-criteria)

---

## Executive Summary

Impact Analysis is a critical feature for aerospace requirements management that helps engineers understand the **ripple effects** of changing a requirement. When a requirement is modified, added, or deprecated, this feature will:

1. **Identify all affected requirements** (upstream and downstream)
2. **Calculate risk scores** for the proposed change
3. **Show impacted test cases** that need re-execution
4. **Flag regulatory compliance** implications
5. **Generate change impact reports** for approval workflows

**Key Benefits:**
- Prevent unintended consequences of requirement changes
- Ensure all dependent requirements are reviewed
- Maintain regulatory compliance during changes
- Accelerate change approval with comprehensive analysis
- Reduce risk of overlooking critical dependencies

**Business Value:**
- 60% reduction in change-related defects
- 75% faster change impact assessment
- 100% traceability of change effects
- Regulatory compliance maintained during changes

---

## Feature Overview

### Core Capabilities

#### 1. Upstream Impact Analysis
**Purpose:** Identify parent requirements affected by a change

**Analysis includes:**
- Direct parent requirements (via traceability links)
- Indirect ancestors (recursive traversal up the tree)
- Requirements that derive from the changed requirement
- Requirements that verify/satisfy the changed requirement

**Example:**
```
Change: AHLR-023 "Maximum Takeoff Weight: 12,500 lbs"
Upstream Impact:
  ├─ AHLR-001 "Aircraft Performance Requirements" (parent)
  ├─ CERT-045 "FAA 14 CFR §23.2005 Compliance" (certification)
  └─ SYS-120 "Structural Load Requirements" (derives from)
```

#### 2. Downstream Impact Analysis
**Purpose:** Identify child requirements and tests affected by a change

**Analysis includes:**
- Direct child requirements (system, technical, certification)
- Indirect descendants (full tree traversal)
- Test cases linked to requirement and descendants
- Design specifications derived from requirement
- Implementation components based on requirement

**Example:**
```
Change: AHLR-023 "Maximum Takeoff Weight: 12,500 lbs"
Downstream Impact:
  ├─ SYS-234 "Wing Structural Design" (child)
  │   ├─ TECH-567 "Wing Spar Load Calculations" (grandchild)
  │   └─ TC-1234 "Wing Load Test" (test case)
  ├─ SYS-235 "Landing Gear Sizing" (child)
  │   ├─ TECH-568 "Gear Strength Analysis" (grandchild)
  │   └─ TC-1235 "Gear Compression Test" (test case)
  └─ CERT-123 "Weight Verification Procedures" (certification)
      └─ TC-5678 "Weight & Balance Test" (test case)
```

#### 3. Risk Scoring Algorithm
**Purpose:** Quantify the risk level of a proposed change

**Risk factors:**
- **Depth of impact** (how many levels affected)
- **Breadth of impact** (number of requirements affected)
- **Requirement criticality** (priority levels of affected items)
- **Test coverage** (number of tests requiring re-execution)
- **Regulatory impact** (compliance requirements affected)
- **Change history** (previous changes to same requirement)

**Risk Score Formula:**
```
Risk Score = (
    (depth_weight × max_depth) +
    (breadth_weight × affected_count) +
    (critical_weight × critical_count) +
    (test_weight × test_case_count) +
    (regulatory_weight × regulatory_count) +
    (history_weight × change_frequency)
) / normalization_factor

Risk Levels:
- LOW: 0-30
- MEDIUM: 31-60
- HIGH: 61-80
- CRITICAL: 81-100
```

**Weights (configurable):**
```python
DEFAULT_WEIGHTS = {
    "depth": 0.20,      # Impact depth
    "breadth": 0.25,    # Number of affected items
    "critical": 0.25,   # Critical requirements
    "test": 0.15,       # Test cases affected
    "regulatory": 0.10, # Compliance impact
    "history": 0.05     # Change frequency
}
```

#### 4. Change Impact Report
**Purpose:** Generate comprehensive report for change approval

**Report sections:**
- **Change Summary**
  - Original requirement details
  - Proposed changes (diff view)
  - Change justification
  - Requestor and date

- **Impact Analysis Results**
  - Risk score and level
  - Total affected requirements (count by type)
  - Total affected test cases
  - Regulatory implications

- **Affected Requirements Tree**
  - Visual hierarchy of all impacted requirements
  - Color-coded by risk level
  - Expandable/collapsible tree view

- **Test Execution Plan**
  - List of all test cases requiring re-execution
  - Grouped by priority
  - Estimated effort (hours)

- **Regulatory Compliance Checklist**
  - List of affected regulatory requirements
  - Compliance verification steps
  - Required approvals

- **Recommended Actions**
  - Required reviews
  - Approvals needed
  - Timeline estimates
  - Risk mitigation steps

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (Next.js)                      │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐  ┌──────────────────┐  ┌───────────────┐ │
│  │ Requirement      │  │  Impact Analysis │  │  Change       │ │
│  │ Detail Page      │  │  Dashboard       │  │  Request Form │ │
│  │  - Analyze Impact│  │  - View Reports  │  │  - Submit     │ │
│  │  - View Results  │  │  - Compare       │  │  - Review     │ │
│  └──────────────────┘  └──────────────────┘  └───────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              ▼ REST API
┌─────────────────────────────────────────────────────────────────┐
│                    Backend API (FastAPI)                        │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐  ┌──────────────────┐  ┌───────────────┐ │
│  │ Impact Analysis  │  │  Graph Traversal │  │  Risk         │ │
│  │ Service          │  │  Engine          │  │  Scoring      │ │
│  │  - Analyze       │  │  - DFS/BFS       │  │  - Calculate  │ │
│  │  - Report        │  │  - Cycle Detect  │  │  - Weight     │ │
│  └──────────────────┘  └──────────────────┘  └───────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Database (PostgreSQL)                        │
├─────────────────────────────────────────────────────────────────┤
│  - Requirements           - Impact Analysis Reports             │
│  - Traceability Links     - Change Requests                     │
│  - Test Cases             - Risk Configurations                 │
└─────────────────────────────────────────────────────────────────┘
```

### Algorithm Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. User selects requirement to analyze                          │
└────────────────────────┬────────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. Fetch requirement and all traceability links                 │
└────────────────────────┬────────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. Traverse UPSTREAM (parents, ancestors)                       │
│    - Recursive DFS with visited set                             │
│    - Track depth and path                                       │
│    - Detect cycles                                              │
└────────────────────────┬────────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. Traverse DOWNSTREAM (children, descendants)                  │
│    - Recursive DFS with visited set                             │
│    - Track depth and path                                       │
│    - Collect test cases at each level                           │
└────────────────────────┬────────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. Calculate Risk Score                                         │
│    - Count requirements by type and priority                    │
│    - Count test cases                                           │
│    - Check regulatory compliance                                │
│    - Apply weighted formula                                     │
└────────────────────────┬────────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6. Generate Impact Report                                       │
│    - Format results                                             │
│    - Create visual tree                                         │
│    - Generate recommendations                                   │
└────────────────────────┬────────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 7. Return to user (JSON response)                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## Technical Design

### Backend Components

#### 1. Impact Analysis Service
**File:** `backend/app/services/impact_analysis.py`

```python
class ImpactAnalysisService:
    """
    Service for analyzing the impact of requirement changes.
    """

    def __init__(self, db: Session):
        self.db = db
        self.visited_upstream = set()
        self.visited_downstream = set()

    def analyze_impact(
        self,
        requirement_id: int,
        config: Optional[ImpactAnalysisConfig] = None
    ) -> ImpactAnalysisResult:
        """
        Perform complete impact analysis for a requirement.

        Args:
            requirement_id: ID of the requirement to analyze
            config: Optional configuration for weights and thresholds

        Returns:
            ImpactAnalysisResult with all affected items and risk score
        """
        pass

    def traverse_upstream(
        self,
        req_id: int,
        depth: int = 0,
        max_depth: int = 10
    ) -> List[ImpactNode]:
        """
        Recursively traverse parent requirements.
        Uses DFS with cycle detection.
        """
        pass

    def traverse_downstream(
        self,
        req_id: int,
        depth: int = 0,
        max_depth: int = 10
    ) -> List[ImpactNode]:
        """
        Recursively traverse child requirements and test cases.
        Uses DFS with cycle detection.
        """
        pass

    def calculate_risk_score(
        self,
        upstream: List[ImpactNode],
        downstream: List[ImpactNode],
        config: ImpactAnalysisConfig
    ) -> RiskScore:
        """
        Calculate risk score based on impact analysis results.
        """
        pass

    def generate_report(
        self,
        requirement: Requirement,
        result: ImpactAnalysisResult
    ) -> ImpactReport:
        """
        Generate comprehensive impact analysis report.
        """
        pass
```

#### 2. Data Models
**File:** `backend/app/models/impact_analysis.py`

```python
class ImpactAnalysisReport(Base):
    """Impact analysis report storage"""
    __tablename__ = "impact_analysis_reports"

    id = Column(Integer, primary_key=True)
    requirement_id = Column(Integer, ForeignKey("requirements.id"))
    analyzed_by_id = Column(Integer, ForeignKey("users.id"))

    # Analysis results
    risk_score = Column(Float)
    risk_level = Column(Enum(RiskLevel))
    upstream_count = Column(Integer)
    downstream_count = Column(Integer)
    test_case_count = Column(Integer)
    regulatory_impact = Column(Boolean)

    # JSON storage
    upstream_tree = Column(JSON)
    downstream_tree = Column(JSON)
    affected_requirements = Column(JSON)
    affected_test_cases = Column(JSON)
    recommendations = Column(JSON)

    # Metadata
    created_at = Column(DateTime, default=func.now())

    # Relationships
    requirement = relationship("Requirement")
    analyzed_by = relationship("User")


class ChangeRequest(Base):
    """Change request with impact analysis"""
    __tablename__ = "change_requests"

    id = Column(Integer, primary_key=True)
    requirement_id = Column(Integer, ForeignKey("requirements.id"))
    impact_report_id = Column(Integer, ForeignKey("impact_analysis_reports.id"))

    # Change details
    title = Column(String(200))
    description = Column(Text)
    justification = Column(Text)
    proposed_changes = Column(JSON)  # Before/after diff

    # Workflow
    status = Column(Enum(ChangeRequestStatus))  # PENDING, APPROVED, REJECTED, IMPLEMENTED
    requested_by_id = Column(Integer, ForeignKey("users.id"))
    reviewed_by_id = Column(Integer, ForeignKey("users.id"))

    # Metadata
    created_at = Column(DateTime, default=func.now())
    reviewed_at = Column(DateTime)

    # Relationships
    requirement = relationship("Requirement")
    impact_report = relationship("ImpactAnalysisReport")
    requested_by = relationship("User", foreign_keys=[requested_by_id])
    reviewed_by = relationship("User", foreign_keys=[reviewed_by_id])
```

#### 3. API Schemas
**File:** `backend/app/schemas/impact_analysis.py`

```python
class ImpactNode(BaseModel):
    """Single node in impact tree"""
    requirement_id: str
    id: int
    title: str
    type: str
    priority: str
    depth: int
    path: List[str]
    test_case_count: int = 0
    regulatory: bool = False


class RiskScore(BaseModel):
    """Risk score calculation result"""
    score: float  # 0-100
    level: str  # LOW, MEDIUM, HIGH, CRITICAL
    factors: Dict[str, float]  # Individual factor contributions
    explanation: str


class ImpactAnalysisResult(BaseModel):
    """Complete impact analysis result"""
    requirement: RequirementResponse

    upstream: List[ImpactNode]
    downstream: List[ImpactNode]

    risk_score: RiskScore

    stats: Dict[str, int]  # Counts by type, priority, etc.
    affected_test_cases: List[int]
    regulatory_implications: List[str]

    recommendations: List[str]
    estimated_effort_hours: float


class ImpactAnalysisConfig(BaseModel):
    """Configuration for impact analysis"""
    max_depth: int = 10
    include_test_cases: bool = True
    include_regulatory: bool = True

    weights: Dict[str, float] = {
        "depth": 0.20,
        "breadth": 0.25,
        "critical": 0.25,
        "test": 0.15,
        "regulatory": 0.10,
        "history": 0.05
    }
```

---

## API Endpoints

### 1. Analyze Impact
**Endpoint:** `POST /api/impact-analysis/analyze`

**Description:** Perform impact analysis for a requirement

**Request:**
```json
{
  "requirement_id": 123,
  "config": {
    "max_depth": 10,
    "include_test_cases": true,
    "include_regulatory": true,
    "weights": {
      "depth": 0.20,
      "breadth": 0.25,
      "critical": 0.25,
      "test": 0.15,
      "regulatory": 0.10,
      "history": 0.05
    }
  }
}
```

**Response:** `200 OK`
```json
{
  "requirement": {
    "id": 123,
    "requirement_id": "AHLR-023",
    "title": "Maximum Takeoff Weight",
    "type": "AHLR",
    "priority": "CRITICAL"
  },
  "upstream": [
    {
      "requirement_id": "AHLR-001",
      "id": 1,
      "title": "Aircraft Performance Requirements",
      "type": "AHLR",
      "priority": "CRITICAL",
      "depth": 1,
      "path": ["AHLR-023", "AHLR-001"],
      "test_case_count": 0,
      "regulatory": false
    }
  ],
  "downstream": [
    {
      "requirement_id": "SYS-234",
      "id": 234,
      "title": "Wing Structural Design",
      "type": "SYSTEM",
      "priority": "HIGH",
      "depth": 1,
      "path": ["AHLR-023", "SYS-234"],
      "test_case_count": 5,
      "regulatory": false
    }
  ],
  "risk_score": {
    "score": 75.5,
    "level": "HIGH",
    "factors": {
      "depth": 15.0,
      "breadth": 18.75,
      "critical": 20.0,
      "test": 12.5,
      "regulatory": 7.5,
      "history": 1.75
    },
    "explanation": "High risk due to critical priority and 15 affected requirements"
  },
  "stats": {
    "total_affected": 15,
    "ahlr_count": 2,
    "system_count": 8,
    "technical_count": 4,
    "certification_count": 1,
    "critical_count": 3,
    "high_count": 7,
    "medium_count": 5
  },
  "affected_test_cases": [1234, 1235, 5678],
  "regulatory_implications": [
    "14 CFR §23.2005 compliance verification required",
    "EASA CS-23 weight and balance re-certification needed"
  ],
  "recommendations": [
    "Schedule review with structural engineering team",
    "Re-execute 23 test cases across 5 test suites",
    "Update compliance documentation for FAA certification",
    "Notify certification authority of proposed change"
  ],
  "estimated_effort_hours": 48.5
}
```

### 2. Get Impact Report
**Endpoint:** `GET /api/impact-analysis/reports/{report_id}`

**Description:** Retrieve a previously generated impact analysis report

**Response:** `200 OK`
```json
{
  "id": 456,
  "requirement_id": 123,
  "analyzed_by": "John Engineer",
  "created_at": "2025-10-21T10:30:00Z",
  "risk_score": 75.5,
  "risk_level": "HIGH",
  "upstream_count": 3,
  "downstream_count": 12,
  "test_case_count": 23,
  "regulatory_impact": true,
  "report_data": { /* Full analysis result */ }
}
```

### 3. List Reports
**Endpoint:** `GET /api/impact-analysis/reports`

**Query Parameters:**
- `requirement_id` (optional): Filter by requirement
- `risk_level` (optional): Filter by risk level
- `page`, `page_size`: Pagination

**Response:** `200 OK`
```json
{
  "reports": [ /* Array of reports */ ],
  "total": 45,
  "page": 1,
  "page_size": 20
}
```

### 4. Create Change Request
**Endpoint:** `POST /api/impact-analysis/change-requests`

**Description:** Create change request with impact analysis

**Request:**
```json
{
  "requirement_id": 123,
  "title": "Increase Maximum Takeoff Weight to 13,500 lbs",
  "description": "Market research shows demand for higher payload capacity",
  "justification": "Competitive advantage and customer requests",
  "proposed_changes": {
    "before": "Maximum Takeoff Weight: 12,500 lbs",
    "after": "Maximum Takeoff Weight: 13,500 lbs"
  },
  "perform_impact_analysis": true
}
```

**Response:** `201 Created`
```json
{
  "id": 789,
  "requirement_id": 123,
  "impact_report_id": 456,
  "title": "Increase Maximum Takeoff Weight to 13,500 lbs",
  "status": "PENDING",
  "requested_by": "John Engineer",
  "created_at": "2025-10-21T10:30:00Z",
  "impact_summary": {
    "risk_level": "HIGH",
    "affected_requirements": 15,
    "affected_test_cases": 23
  }
}
```

### 5. Compare Scenarios
**Endpoint:** `POST /api/impact-analysis/compare`

**Description:** Compare impact of multiple change scenarios

**Request:**
```json
{
  "scenarios": [
    {
      "name": "Scenario A: 13,500 lbs",
      "requirement_id": 123,
      "changes": { /* ... */ }
    },
    {
      "name": "Scenario B: 14,000 lbs",
      "requirement_id": 123,
      "changes": { /* ... */ }
    }
  ]
}
```

**Response:** Side-by-side comparison of impacts

---

## Database Schema

### Migration
**File:** `backend/alembic/versions/XXXXXX_add_impact_analysis.py`

```python
def upgrade():
    # Impact Analysis Reports table
    op.create_table(
        'impact_analysis_reports',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('requirement_id', sa.Integer(), sa.ForeignKey('requirements.id')),
        sa.Column('analyzed_by_id', sa.Integer(), sa.ForeignKey('users.id')),

        sa.Column('risk_score', sa.Float()),
        sa.Column('risk_level', sa.String(20)),
        sa.Column('upstream_count', sa.Integer()),
        sa.Column('downstream_count', sa.Integer()),
        sa.Column('test_case_count', sa.Integer()),
        sa.Column('regulatory_impact', sa.Boolean(), default=False),

        sa.Column('upstream_tree', sa.JSON()),
        sa.Column('downstream_tree', sa.JSON()),
        sa.Column('affected_requirements', sa.JSON()),
        sa.Column('affected_test_cases', sa.JSON()),
        sa.Column('recommendations', sa.JSON()),

        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )

    # Change Requests table
    op.create_table(
        'change_requests',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('requirement_id', sa.Integer(), sa.ForeignKey('requirements.id')),
        sa.Column('impact_report_id', sa.Integer(), sa.ForeignKey('impact_analysis_reports.id')),

        sa.Column('title', sa.String(200)),
        sa.Column('description', sa.Text()),
        sa.Column('justification', sa.Text()),
        sa.Column('proposed_changes', sa.JSON()),

        sa.Column('status', sa.String(20), default='PENDING'),
        sa.Column('requested_by_id', sa.Integer(), sa.ForeignKey('users.id')),
        sa.Column('reviewed_by_id', sa.Integer(), sa.ForeignKey('users.id')),

        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('reviewed_at', sa.DateTime()),
    )

    # Indexes
    op.create_index('ix_impact_reports_requirement', 'impact_analysis_reports', ['requirement_id'])
    op.create_index('ix_impact_reports_risk', 'impact_analysis_reports', ['risk_level'])
    op.create_index('ix_change_requests_status', 'change_requests', ['status'])
```

---

## Frontend Components

### 1. Impact Analysis Button
**Location:** Requirement detail page
**File:** `frontend/components/requirements/ImpactAnalysisButton.tsx`

```tsx
<button
  onClick={handleAnalyzeImpact}
  className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
>
  <ChartBarIcon className="w-5 h-5 inline mr-2" />
  Analyze Impact
</button>
```

### 2. Impact Analysis Modal
**File:** `frontend/components/impact-analysis/ImpactAnalysisModal.tsx`

**Features:**
- Loading state during analysis
- Tabbed interface:
  - **Overview**: Risk score, stats, summary
  - **Upstream**: Parent requirements tree
  - **Downstream**: Child requirements and tests tree
  - **Test Cases**: List of affected test cases
  - **Regulatory**: Compliance implications
  - **Report**: Printable/exportable report

### 3. Impact Tree Visualization
**File:** `frontend/components/impact-analysis/ImpactTree.tsx`

**Features:**
- Collapsible tree structure
- Color-coded by risk level
- Icons for requirement types
- Depth indicators
- Click to navigate to requirement

### 4. Risk Score Badge
**File:** `frontend/components/impact-analysis/RiskScoreBadge.tsx`

```tsx
<div className="flex items-center gap-2">
  <div className={`text-2xl font-bold ${getRiskColor(riskLevel)}`}>
    {riskScore.toFixed(1)}
  </div>
  <div>
    <div className="text-xs text-gray-500">Risk Score</div>
    <div className={`text-sm font-semibold ${getRiskColor(riskLevel)}`}>
      {riskLevel}
    </div>
  </div>
</div>
```

### 5. Change Request Form
**File:** `frontend/components/impact-analysis/ChangeRequestForm.tsx`

**Fields:**
- Title (required)
- Description (required)
- Justification (required)
- Proposed changes (before/after)
- Auto-run impact analysis checkbox

---

## Implementation Phases

### Week 6, Day 1-2: Backend Core (16 hours)
**Goal:** Implement graph traversal and impact analysis service

**Tasks:**
- [ ] Create `impact_analysis.py` service
- [ ] Implement upstream traversal (DFS with cycle detection)
- [ ] Implement downstream traversal (DFS with cycle detection)
- [ ] Add test case collection logic
- [ ] Implement risk scoring algorithm
- [ ] Create data models (`ImpactAnalysisReport`, `ChangeRequest`)
- [ ] Write database migration
- [ ] Run migration and test with existing data

**Deliverables:**
- Working impact analysis service
- Database schema created
- Unit tests for traversal algorithms (99% coverage)

---

### Week 6, Day 3-4: Backend API (16 hours)
**Goal:** Create REST API endpoints

**Tasks:**
- [ ] Create `impact_analysis.py` API routes
- [ ] Implement `POST /api/impact-analysis/analyze` endpoint
- [ ] Implement `GET /api/impact-analysis/reports/{id}` endpoint
- [ ] Implement `GET /api/impact-analysis/reports` list endpoint
- [ ] Implement `POST /api/impact-analysis/change-requests` endpoint
- [ ] Add request/response schemas
- [ ] Add authentication and authorization
- [ ] Write integration tests (API + database)

**Deliverables:**
- Complete API with 5 endpoints
- Swagger documentation auto-generated
- Integration tests passing

---

### Week 6, Day 5: Backend Testing (8 hours)
**Goal:** Comprehensive testing and optimization

**Tasks:**
- [ ] Unit tests for impact analysis service (15+ tests)
- [ ] Integration tests for API endpoints (10+ tests)
- [ ] Performance testing with large datasets (1000+ requirements)
- [ ] Optimize graph traversal for speed (<1s for 500 requirements)
- [ ] Test cycle detection edge cases
- [ ] Test with real aerospace requirement data

**Deliverables:**
- 25+ tests passing
- 99% code coverage
- Performance benchmarks documented

---

### Week 6, Day 6-7: Frontend Components (16 hours)
**Goal:** Build UI for impact analysis

**Tasks:**
- [ ] Create `ImpactAnalysisButton` component
- [ ] Create `ImpactAnalysisModal` with tabs
- [ ] Create `ImpactTree` visualization component
- [ ] Create `RiskScoreBadge` component
- [ ] Create `ChangeRequestForm` component
- [ ] Integrate into requirement detail page
- [ ] Add loading states and error handling
- [ ] Add export to PDF/Excel functionality
- [ ] Responsive design for mobile

**Deliverables:**
- Complete UI integrated into application
- Beautiful, intuitive interface
- Export functionality working

---

### Week 6, Day 8: End-to-End Testing (8 hours)
**Goal:** Test complete workflow

**Tasks:**
- [ ] Test impact analysis on various requirements
- [ ] Test with different risk levels
- [ ] Test change request creation
- [ ] Test report viewing and export
- [ ] Performance testing (frontend + backend)
- [ ] User acceptance testing
- [ ] Bug fixes and polish

**Deliverables:**
- Fully tested feature
- Documentation updated
- Ready for production

---

## Testing Strategy

### Unit Tests

#### Backend Service Tests
**File:** `backend/app/tests/test_impact_analysis_service.py`

```python
def test_traverse_upstream_single_level():
    """Test upstream traversal with one parent"""
    pass

def test_traverse_upstream_multiple_levels():
    """Test upstream traversal with grandparents"""
    pass

def test_traverse_downstream_with_test_cases():
    """Test downstream traversal includes test cases"""
    pass

def test_cycle_detection_prevents_infinite_loop():
    """Test that circular dependencies don't cause infinite loops"""
    pass

def test_risk_score_critical_priority():
    """Test risk score calculation for critical requirements"""
    pass

def test_risk_score_low_impact():
    """Test risk score for low impact changes"""
    pass

def test_regulatory_impact_detected():
    """Test regulatory requirements are flagged"""
    pass
```

#### API Tests
**File:** `backend/app/tests/test_impact_analysis_api.py`

```python
def test_analyze_impact_success():
    """Test successful impact analysis"""
    pass

def test_analyze_impact_unauthorized():
    """Test authentication required"""
    pass

def test_analyze_impact_invalid_requirement():
    """Test 404 for non-existent requirement"""
    pass

def test_create_change_request_with_analysis():
    """Test change request creation triggers impact analysis"""
    pass
```

### Integration Tests

```python
def test_full_impact_analysis_workflow():
    """
    End-to-end test:
    1. Create requirement hierarchy
    2. Add traceability links
    3. Add test cases
    4. Run impact analysis
    5. Verify results
    """
    pass

def test_large_dataset_performance():
    """Test with 1000+ requirements"""
    pass
```

### Frontend Tests

```typescript
describe('ImpactAnalysisModal', () => {
  it('renders loading state during analysis', () => {});
  it('displays risk score correctly', () => {});
  it('renders upstream tree', () => {});
  it('renders downstream tree', () => {});
  it('handles API errors gracefully', () => {});
});
```

---

## Success Criteria

### Functional Requirements
- ✅ Analyze impact of any requirement change in <3 seconds
- ✅ Correctly identify all upstream requirements (100% accuracy)
- ✅ Correctly identify all downstream requirements (100% accuracy)
- ✅ Calculate accurate risk scores
- ✅ Generate comprehensive reports
- ✅ Create change requests with impact analysis
- ✅ Export reports to PDF/Excel

### Performance Requirements
- ✅ Analysis completes in <1 second for <100 affected requirements
- ✅ Analysis completes in <3 seconds for <500 affected requirements
- ✅ Frontend renders results in <500ms
- ✅ Handle circular dependencies gracefully (no infinite loops)

### Quality Requirements
- ✅ 99% test coverage on backend
- ✅ All unit tests pass
- ✅ All integration tests pass
- ✅ No critical bugs
- ✅ Responsive UI works on mobile/tablet/desktop

### User Experience
- ✅ Intuitive UI requiring no training
- ✅ Clear risk indicators
- ✅ Actionable recommendations
- ✅ Easy to understand reports

---

## Risk Mitigation

### Technical Risks

**Risk:** Graph traversal causes performance issues with large datasets
**Mitigation:**
- Implement max depth limit (default: 10)
- Cache traversal results
- Add pagination for large result sets
- Optimize database queries with eager loading

**Risk:** Circular dependencies cause infinite loops
**Mitigation:**
- Implement visited set tracking
- Add cycle detection
- Limit max iterations
- Log warnings when cycles detected

**Risk:** Risk scoring algorithm not accurate
**Mitigation:**
- Make weights configurable
- Collect user feedback
- Iterate on formula based on real usage
- Allow manual override

### Business Risks

**Risk:** Users don't trust automated risk scores
**Mitigation:**
- Show detailed breakdown of score factors
- Allow manual adjustment
- Provide clear explanations
- Track accuracy over time

**Risk:** Change request workflow slows down development
**Mitigation:**
- Keep UI fast and responsive
- Allow bypassing for low-risk changes
- Provide quick approval for authorized users

---

## Future Enhancements

### Phase 3 Features (Post-Week 6)
- **AI-powered recommendations** using LLM
- **Historical impact tracking** and trend analysis
- **Automated change approval** for low-risk changes
- **Integration with JIRA/ServiceNow** for change management
- **Email notifications** for affected stakeholders
- **What-if scenarios** comparing multiple changes
- **Impact heatmap** visualization
- **Compliance workflow** automation

---

## Documentation

### User Documentation
- User guide: "How to Analyze Impact of Requirement Changes"
- Video tutorial: Impact analysis walkthrough
- Best practices guide
- FAQ section

### Developer Documentation
- API documentation (auto-generated from OpenAPI)
- Algorithm documentation (graph traversal)
- Risk scoring formula documentation
- Database schema documentation

---

## Appendix

### Graph Traversal Pseudocode

```python
def traverse_upstream(req_id, visited=None, depth=0, max_depth=10):
    """
    Traverse upstream (parent) requirements using DFS.
    """
    if visited is None:
        visited = set()

    if req_id in visited or depth >= max_depth:
        return []

    visited.add(req_id)
    result = []

    # Get all parent links (target_id = req_id)
    parent_links = get_traceability_links(target_id=req_id)

    for link in parent_links:
        parent_req = get_requirement(link.source_id)

        result.append({
            'requirement': parent_req,
            'depth': depth,
            'link_type': link.link_type
        })

        # Recursive traversal
        result.extend(
            traverse_upstream(
                parent_req.id,
                visited,
                depth + 1,
                max_depth
            )
        )

    return result
```

### Risk Score Example Calculation

```python
# Example: AHLR-023 "Maximum Takeoff Weight"
affected = {
    'depth': 4,  # Max depth of impact
    'total_count': 15,  # Total affected requirements
    'critical_count': 3,
    'test_count': 23,
    'regulatory_count': 2,
    'change_frequency': 1  # Changed 1 time in last year
}

weights = {
    'depth': 0.20,
    'breadth': 0.25,
    'critical': 0.25,
    'test': 0.15,
    'regulatory': 0.10,
    'history': 0.05
}

risk_score = (
    (0.20 * min(affected['depth'] / 10 * 100, 100)) +           # 8.0
    (0.25 * min(affected['total_count'] / 20 * 100, 100)) +     # 18.75
    (0.25 * min(affected['critical_count'] / 5 * 100, 100)) +   # 15.0
    (0.15 * min(affected['test_count'] / 30 * 100, 100)) +      # 11.5
    (0.10 * min(affected['regulatory_count'] / 5 * 100, 100)) + # 4.0
    (0.05 * min(affected['change_frequency'] / 10 * 100, 100))  # 0.5
)
# = 57.75 → MEDIUM risk
```

---

**End of Implementation Plan**

**Next Steps:**
1. Review and approve plan
2. Begin Week 6, Day 1-2 implementation
3. Set up daily progress tracking
4. Schedule review at end of each phase

**Estimated Total Effort:** 5-6 days (40-48 hours)

**Status:** ✅ Ready for Implementation
