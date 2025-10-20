# Risk Cards Implementation Plan
**CALIDUS Requirements Management System**

## Executive Summary
This plan introduces visual risk cards to the dashboard that assess and display the risk level of each requirement based on multiple factors including priority, status, traceability, test coverage, and compliance state.

## 📊 Risk Assessment Model

### Risk Factors & Scoring

Each requirement will be scored on a scale of 0-100 based on these factors:

#### 1. **Priority Risk** (Weight: 25%)
- **Critical**: 100 points (Highest Risk)
- **High**: 75 points
- **Medium**: 50 points
- **Low**: 25 points

#### 2. **Status Risk** (Weight: 20%)
- **Draft**: 100 points (Unstable)
- **Under Review**: 60 points (Pending validation)
- **Approved**: 20 points (Stable)
- **Deprecated**: 40 points (Needs replacement)

#### 3. **Traceability Risk** (Weight: 25%)
- **Orphaned** (no parents, children, or tests): 100 points (Critical)
- **Missing Parents** (System/Technical without parent): 80 points
- **Missing Children** (AHLR without children): 60 points
- **Missing Tests** (Approved requirement without tests): 70 points
- **Fully Traced**: 10 points (Low risk)

#### 4. **Test Coverage Risk** (Weight: 20%)
- **No Tests**: 100 points
- **1-2 Tests**: 60 points
- **3-5 Tests**: 30 points
- **6+ Tests**: 10 points

#### 5. **Compliance Risk** (Weight: 10%)
- **Non-Compliant**: 100 points
- **Partial**: 50 points
- **Compliant**: 10 points
- **Not Set**: 30 points

### Risk Level Classification

Final Risk Score → Risk Level:
- **🔴 CRITICAL** (80-100): Red cards - Immediate attention required
- **🟠 HIGH** (60-79): Orange cards - High priority action needed
- **🟡 MEDIUM** (40-59): Yellow cards - Monitor closely
- **🟢 LOW** (0-39): Green cards - Acceptable state

---

## 🎨 Visual Design

### Risk Card Component Design

```
┌─────────────────────────────────────────────┐
│ 🔴 CRITICAL RISK                      [85]  │
│─────────────────────────────────────────────│
│ AHLR-123: Flight Control System Stability  │
│─────────────────────────────────────────────│
│ Risk Factors:                               │
│ • ⚠️  Priority: CRITICAL                    │
│ • 📝 Status: Draft                          │
│ • 🔗 Orphaned (no traceability)             │
│ • ❌ No test coverage                       │
│─────────────────────────────────────────────│
│ [View Details]  [Take Action]              │
└─────────────────────────────────────────────┘
```

### Color Scheme
- **Critical**: `bg-red-50 border-red-500 text-red-900`
- **High**: `bg-orange-50 border-orange-500 text-orange-900`
- **Medium**: `bg-yellow-50 border-yellow-500 text-yellow-900`
- **Low**: `bg-green-50 border-green-500 text-green-900`

### Risk Dashboard Layout

```
Dashboard Top Section:
┌──────────┬──────────┬──────────┬──────────┐
│ CRITICAL │   HIGH   │  MEDIUM  │   LOW    │
│    12    │    48    │   156    │  16,284  │
└──────────┴──────────┴──────────┴──────────┘

Risk Cards Grid (Critical & High shown):
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│ CRIT 1 │ │ CRIT 2 │ │ CRIT 3 │ │ HIGH 1 │
└────────┘ └────────┘ └────────┘ └────────┘
```

---

## 🏗️ Implementation Roadmap

### Phase 1: Backend - Risk Analytics API

#### 1.1 Create Risk Calculation Module
**File**: `backend/app/services/risk_analyzer.py`

```python
class RiskAnalyzer:
    def calculate_requirement_risk(requirement, trace_links, test_cases) -> RiskScore
    def get_risk_factors(requirement) -> List[RiskFactor]
    def classify_risk_level(score: float) -> RiskLevel
```

**Key Functions**:
- `calculate_priority_risk()`: Assess based on requirement priority
- `calculate_status_risk()`: Assess based on lifecycle status
- `calculate_traceability_risk()`: Check parent/child links
- `calculate_test_coverage_risk()`: Evaluate test coverage
- `calculate_compliance_risk()`: Check compliance status
- `aggregate_risk_score()`: Weighted average of all factors

#### 1.2 Create Risk Analytics Endpoints
**File**: `backend/app/api/risk.py`

```python
GET /api/risk/overview
→ Returns risk distribution summary (count by risk level)

GET /api/risk/requirements?level=critical
→ Returns list of requirements filtered by risk level

GET /api/risk/requirement/{id}
→ Returns detailed risk analysis for one requirement

GET /api/risk/trends
→ Returns risk trends over time (for future implementation)
```

**Response Schema** (`backend/app/schemas/risk.py`):
```python
class RiskScore(BaseModel):
    requirement_id: str
    risk_level: str  # critical, high, medium, low
    risk_score: float  # 0-100
    risk_factors: List[RiskFactor]

class RiskFactor(BaseModel):
    category: str  # priority, status, traceability, etc.
    score: float
    weight: float
    description: str
    severity: str
```

#### 1.3 Database Migration (Optional - for caching)
Add optional `risk_score` and `risk_level` columns to `requirements` table for caching:
```sql
ALTER TABLE requirements
ADD COLUMN risk_score DECIMAL(5,2),
ADD COLUMN risk_level VARCHAR(20),
ADD COLUMN risk_updated_at TIMESTAMP;
```

---

### Phase 2: Frontend - Risk Card Components

#### 2.1 Create RiskCard Component
**File**: `frontend/components/risk/RiskCard.tsx`

**Features**:
- Color-coded border and background based on risk level
- Risk score badge (0-100)
- Requirement ID and title
- List of risk factors with icons
- Action buttons (View Details, Take Action)
- Hover effects and animations
- Responsive design

#### 2.2 Create RiskLevel Badge
**File**: `frontend/components/risk/RiskBadge.tsx`

Small badge component for displaying risk level in lists:
```tsx
<RiskBadge level="critical" score={85} size="sm" />
```

#### 2.3 Create Risk Overview Cards
**File**: `frontend/components/risk/RiskOverview.tsx`

Summary cards showing count by risk level:
```tsx
<RiskOverview
  critical={12}
  high={48}
  medium={156}
  low={16284}
/>
```

#### 2.4 Create Risk Dashboard Section
**File**: `frontend/components/risk/RiskDashboard.tsx`

Main container for risk visualization:
- Risk distribution summary
- Top critical/high risk requirements
- Quick filters
- Export functionality

---

### Phase 3: Dashboard Integration

#### 3.1 Update Main Dashboard
**File**: `frontend/app/dashboard/page.tsx`

**Changes**:
1. Add Risk Overview section after "Welcome" banner
2. Add "High Risk Requirements" section before existing charts
3. Maintain all existing functionality
4. Add risk data to existing API calls

**New Layout**:
```
1. Welcome Banner (existing) ✓
2. Risk Overview Cards (NEW) ⭐
3. Key Metrics Cards (existing) ✓
4. High-Risk Requirements Grid (NEW) ⭐
5. Charts Row (existing) ✓
6. Quick Stats (existing) ✓
```

#### 3.2 Add Risk Column to Requirements List
**File**: `frontend/app/dashboard/requirements/page.tsx`

Add risk badge column to requirements table:
```
| ID | Title | Type | Status | Risk | Actions |
```

#### 3.3 Add Risk Tab to Requirement Detail
**File**: `frontend/components/RequirementModal.tsx`

Add "Risk Analysis" tab showing:
- Risk score breakdown
- Contributing factors
- Recommended actions
- Risk history (future enhancement)

---

### Phase 4: API Integration

#### 4.1 Create Risk API Client
**File**: `frontend/lib/api.ts`

```typescript
export const riskAPI = {
  overview: () => fetchAPI('/api/risk/overview'),
  getByLevel: (level: string) => fetchAPI(`/api/risk/requirements?level=${level}`),
  getRequirementRisk: (id: number) => fetchAPI(`/api/risk/requirement/${id}`),
};
```

#### 4.2 Create Risk Types
**File**: `frontend/lib/types.ts`

```typescript
interface RiskScore {
  requirement_id: string;
  risk_level: 'critical' | 'high' | 'medium' | 'low';
  risk_score: number;
  risk_factors: RiskFactor[];
}

interface RiskOverview {
  critical_count: number;
  high_count: number;
  medium_count: number;
  low_count: number;
  total_requirements: number;
}
```

---

## 🧪 Testing Strategy

### Backend Testing
**File**: `backend/app/tests/test_risk.py`

```python
def test_risk_calculation_critical_priority()
def test_risk_calculation_orphaned_requirement()
def test_risk_calculation_no_test_coverage()
def test_risk_overview_endpoint()
def test_risk_filtering_by_level()
def test_risk_score_consistency()
```

### Frontend Testing
- Component rendering tests
- Risk level color coding validation
- Data fetching and loading states
- Responsive design testing
- Accessibility (WCAG AA compliance)

### Integration Testing
- Verify existing dashboard still loads correctly
- Verify requirements list still functions
- Verify all existing API calls work
- Verify new risk endpoints integrate seamlessly

### Regression Testing Checklist
- ✅ Login functionality
- ✅ Dashboard loads with all existing metrics
- ✅ Requirements CRUD operations
- ✅ Test cases management
- ✅ Traceability matrix
- ✅ Traceability graph
- ✅ User management
- ✅ Search and filters

---

## 📁 File Structure

```
backend/
├── app/
│   ├── api/
│   │   └── risk.py                    # NEW - Risk endpoints
│   ├── services/
│   │   └── risk_analyzer.py           # NEW - Risk calculation logic
│   ├── schemas/
│   │   └── risk.py                    # NEW - Risk data models
│   └── tests/
│       └── test_risk.py               # NEW - Risk tests

frontend/
├── components/
│   └── risk/
│       ├── RiskCard.tsx               # NEW - Main risk card component
│       ├── RiskBadge.tsx              # NEW - Small risk indicator
│       ├── RiskOverview.tsx           # NEW - Risk summary cards
│       └── RiskDashboard.tsx          # NEW - Risk dashboard section
├── app/
│   └── dashboard/
│       └── page.tsx                   # UPDATED - Add risk cards
└── lib/
    ├── api.ts                         # UPDATED - Add risk API
    └── types.ts                       # UPDATED - Add risk types
```

---

## 🎯 Success Criteria

### Functional Requirements
- ✅ Risk score calculated accurately for all 16,500 requirements
- ✅ Risk cards display correctly on dashboard
- ✅ Risk filtering works (show only critical/high)
- ✅ Risk factors clearly explained
- ✅ Performance: Risk calculation < 500ms per requirement
- ✅ Dashboard load time remains < 3 seconds

### Non-Functional Requirements
- ✅ All existing functionality remains intact
- ✅ No breaking changes to existing APIs
- ✅ Responsive design (mobile, tablet, desktop)
- ✅ Accessible (keyboard navigation, screen readers)
- ✅ Test coverage ≥ 80%
- ✅ Code quality maintained (TypeScript strict mode, ESLint passing)

---

## 📊 Example Risk Scenarios

### Scenario 1: Critical Risk Requirement
```
AHLR-042: Emergency Landing System
- Priority: CRITICAL (25 points)
- Status: Draft (20 points)
- Traceability: Orphaned (25 points)
- Test Coverage: 0 tests (20 points)
- Compliance: Not set (3 points)
→ Risk Score: 93/100 → CRITICAL 🔴
```

### Scenario 2: Low Risk Requirement
```
SYS-1234: Interior Lighting Control
- Priority: Low (6.25 points)
- Status: Approved (4 points)
- Traceability: Fully traced (2.5 points)
- Test Coverage: 8 tests (2 points)
- Compliance: Compliant (1 point)
→ Risk Score: 15.75/100 → LOW 🟢
```

---

## 🚀 Implementation Timeline

### Iteration 1: Backend Foundation (2-3 hours)
- Create risk analyzer service
- Implement risk calculation algorithm
- Create risk API endpoints
- Write unit tests

### Iteration 2: Frontend Components (2-3 hours)
- Build RiskCard component
- Build RiskBadge component
- Build RiskOverview component
- Style with Tailwind CSS

### Iteration 3: Dashboard Integration (1-2 hours)
- Add risk section to main dashboard
- Update requirements list with risk badges
- Add risk tab to requirement modal
- Test all integrations

### Iteration 4: Testing & Polish (1-2 hours)
- Run full regression tests
- Fix any issues
- Performance optimization
- Documentation updates

**Total Estimated Time**: 6-10 hours

---

## 🔄 Future Enhancements (Phase 2)

1. **Risk Trends**
   - Track risk score changes over time
   - Risk reduction metrics
   - Predictive risk analysis

2. **Risk Mitigation Actions**
   - Suggested actions to reduce risk
   - Automated task creation
   - Risk mitigation workflows

3. **Risk Reporting**
   - Export risk reports (PDF, Excel)
   - Executive risk dashboards
   - Automated risk alerts

4. **Machine Learning**
   - AI-powered risk prediction
   - Pattern recognition in high-risk requirements
   - Anomaly detection

---

## ✅ Approval & Next Steps

**Please review this plan and confirm:**
1. ✓ Risk factors and weights are appropriate for aerospace requirements
2. ✓ Visual design meets expectations
3. ✓ Implementation approach is acceptable
4. ✓ Any specific customizations or changes needed

**Upon approval, I will:**
1. Begin implementation following the phases outlined
2. Provide progress updates at each phase completion
3. Ensure all existing functionality remains intact
4. Deliver a fully tested, production-ready feature

---

**Document Version**: 1.0
**Date**: October 20, 2025
**Status**: Awaiting Approval
