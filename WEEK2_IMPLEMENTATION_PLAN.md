# Week 2 Implementation Plan - Core Backend Development

**Project**: CALIDUS Requirements Management System  
**Phase**: Phase 1, Week 2  
**Date**: 2025-10-17  
**Status**: Ready to Begin

---

## Week 2 Objectives

Based on CLAUDE.md roadmap, Week 2 focuses on core backend functionality:

1. ✅ **Requirements CRUD Operations**
2. ✅ **Test Cases CRUD Operations**
3. ✅ **Traceability Link Management**
4. ✅ **Database Migrations (Alembic)**
5. ✅ **Sample Data Generation (15,000+ requirements)**
6. ✅ **Performance Testing (<200ms response time)**

---

## Implementation Sequence

### Step 1: Database Models & Schemas (Day 1-2)

#### 1.1 Requirement Model
**File**: `backend/app/models/requirement.py`

```python
from sqlalchemy import Column, Integer, String, Text, Enum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class RequirementType(enum.Enum):
    AHLR = "Aircraft_High_Level_Requirement"
    SYSTEM = "System_Requirement"
    TECHNICAL = "Technical_Specification"
    CERTIFICATION = "Certification_Requirement"

class RequirementStatus(enum.Enum):
    DRAFT = "draft"
    APPROVED = "approved"
    DEPRECATED = "deprecated"
    UNDER_REVIEW = "under_review"

class Requirement(Base):
    __tablename__ = "requirements"
    
    id = Column(Integer, primary_key=True, index=True)
    requirement_id = Column(String(50), unique=True, index=True, nullable=False)
    type = Column(Enum(RequirementType), nullable=False)
    category = Column(String(100))
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    rationale = Column(Text)
    priority = Column(String(20))  # Critical, High, Medium, Low
    status = Column(Enum(RequirementStatus), default=RequirementStatus.DRAFT)
    
    # Regulatory source
    regulatory_document = Column(String(200))
    regulatory_section = Column(String(100))
    regulatory_page = Column(Integer)
    
    # Verification
    verification_method = Column(String(50))  # Test, Analysis, Inspection, Demo
    compliance_status = Column(String(20))
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by_id = Column(Integer, ForeignKey("users.id"))
    owner = Column(String(100))
    version = Column(String(20))
    
    # Relationships
    created_by = relationship("User", back_populates="requirements")
    test_cases = relationship("TestCase", back_populates="requirement")
    parent_traces = relationship("TraceabilityLink", foreign_keys="TraceabilityLink.target_id", back_populates="target")
    child_traces = relationship("TraceabilityLink", foreign_keys="TraceabilityLink.source_id", back_populates="source")
```

#### 1.2 Test Case Model
**File**: `backend/app/models/test_case.py`

```python
class TestCaseStatus(enum.Enum):
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    BLOCKED = "blocked"

class TestCase(Base):
    __tablename__ = "test_cases"
    
    id = Column(Integer, primary_key=True, index=True)
    test_case_id = Column(String(50), unique=True, index=True, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    preconditions = Column(Text)
    test_steps = Column(Text, nullable=False)
    expected_results = Column(Text, nullable=False)
    actual_results = Column(Text)
    status = Column(Enum(TestCaseStatus), default=TestCaseStatus.PENDING)
    priority = Column(String(20))
    
    # Linking
    requirement_id = Column(Integer, ForeignKey("requirements.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    requirement = relationship("Requirement", back_populates="test_cases")
    created_by = relationship("User", back_populates="test_cases")
```

#### 1.3 Traceability Link Model
**File**: `backend/app/models/traceability.py`

```python
class TraceLinkType(enum.Enum):
    DERIVES_FROM = "derives_from"
    SATISFIES = "satisfies"
    VERIFIES = "verifies"
    DEPENDS_ON = "depends_on"

class TraceabilityLink(Base):
    __tablename__ = "traceability_links"
    
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("requirements.id"), nullable=False)
    target_id = Column(Integer, ForeignKey("requirements.id"), nullable=False)
    link_type = Column(Enum(TraceLinkType), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    source = relationship("Requirement", foreign_keys=[source_id], back_populates="child_traces")
    target = relationship("Requirement", foreign_keys=[target_id], back_populates="parent_traces")
    created_by = relationship("User")
```

---

### Step 2: Pydantic Schemas (Day 2)

#### 2.1 Requirement Schemas
**File**: `backend/app/schemas/requirement.py`

```python
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.requirement import RequirementType, RequirementStatus

class RequirementBase(BaseModel):
    requirement_id: str = Field(..., min_length=1, max_length=50)
    type: RequirementType
    category: Optional[str] = None
    title: str = Field(..., min_length=1, max_length=200)
    description: str
    rationale: Optional[str] = None
    priority: Optional[str] = "Medium"
    status: RequirementStatus = RequirementStatus.DRAFT
    regulatory_document: Optional[str] = None
    regulatory_section: Optional[str] = None
    regulatory_page: Optional[int] = None
    verification_method: Optional[str] = None
    compliance_status: Optional[str] = None
    owner: Optional[str] = None
    version: Optional[str] = "1.0"

class RequirementCreate(RequirementBase):
    pass

class RequirementUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[RequirementStatus] = None
    priority: Optional[str] = None
    # ... other optional fields

class RequirementResponse(RequirementBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    created_by_id: int
    
    class Config:
        from_attributes = True
```

---

### Step 3: API Routes (Day 3-4)

#### 3.1 Requirements API
**File**: `backend/app/api/requirements.py`

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.core.dependencies import get_current_active_user, get_db
from app.models.requirement import Requirement
from app.schemas.requirement import RequirementCreate, RequirementUpdate, RequirementResponse

router = APIRouter(prefix="/api/requirements", tags=["requirements"])

@router.post("/", response_model=RequirementResponse, status_code=201)
async def create_requirement(
    requirement: RequirementCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    # Check for duplicate requirement_id
    existing = db.query(Requirement).filter(
        Requirement.requirement_id == requirement.requirement_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Requirement ID already exists")
    
    db_requirement = Requirement(**requirement.dict(), created_by_id=current_user.id)
    db.add(db_requirement)
    db.commit()
    db.refresh(db_requirement)
    return db_requirement

@router.get("/", response_model=List[RequirementResponse])
async def list_requirements(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    query = db.query(Requirement)
    
    if type:
        query = query.filter(Requirement.type == type)
    if status:
        query = query.filter(Requirement.status == status)
    
    requirements = query.offset(skip).limit(limit).all()
    return requirements

@router.get("/{requirement_id}", response_model=RequirementResponse)
async def get_requirement(
    requirement_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    requirement = db.query(Requirement).filter(Requirement.id == requirement_id).first()
    if not requirement:
        raise HTTPException(status_code=404, detail="Requirement not found")
    return requirement

@router.put("/{requirement_id}", response_model=RequirementResponse)
async def update_requirement(
    requirement_id: int,
    requirement_update: RequirementUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    db_requirement = db.query(Requirement).filter(Requirement.id == requirement_id).first()
    if not db_requirement:
        raise HTTPException(status_code=404, detail="Requirement not found")
    
    for field, value in requirement_update.dict(exclude_unset=True).items():
        setattr(db_requirement, field, value)
    
    db.commit()
    db.refresh(db_requirement)
    return db_requirement

@router.delete("/{requirement_id}", status_code=204)
async def delete_requirement(
    requirement_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    db_requirement = db.query(Requirement).filter(Requirement.id == requirement_id).first()
    if not db_requirement:
        raise HTTPException(status_code=404, detail="Requirement not found")
    
    db.delete(db_requirement)
    db.commit()
    return None
```

---

### Step 4: Alembic Migrations (Day 4)

#### 4.1 Setup Alembic
**Commands**:
```bash
cd backend
pip install alembic
alembic init alembic
```

#### 4.2 Configure Alembic
**File**: `backend/alembic/env.py`
```python
from app.config import settings
from app.database import Base
from app.models import user, requirement, test_case, traceability

target_metadata = Base.metadata
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
```

#### 4.3 Create Initial Migration
```bash
alembic revision --autogenerate -m "Add requirements, test_cases, traceability tables"
alembic upgrade head
```

---

### Step 5: Sample Data Generation (Day 5)

**File**: `backend/generate_sample_data.py`

```python
import random
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.requirement import Requirement, RequirementType, RequirementStatus
from app.models.test_case import TestCase, TestCaseStatus
from app.models.traceability import TraceabilityLink, TraceLinkType

def generate_requirements(db: Session, count: int = 15000):
    """Generate sample requirements"""
    categories = ["FlightControl", "Avionics", "Structure", "PowerPlant", "FuelSystem"]
    priorities = ["Critical", "High", "Medium", "Low"]
    
    requirements = []
    for i in range(count):
        req_type = random.choice(list(RequirementType))
        prefix = req_type.name[:4]
        
        requirement = Requirement(
            requirement_id=f"{prefix}-{i+1:05d}",
            type=req_type,
            category=random.choice(categories),
            title=f"{req_type.value} Requirement {i+1}",
            description=f"Description for requirement {i+1}",
            priority=random.choice(priorities),
            status=random.choice(list(RequirementStatus)),
            owner="System Engineering",
            version="1.0",
            created_by_id=1
        )
        requirements.append(requirement)
        
        if i % 1000 == 0:
            print(f"Generated {i} requirements...")
    
    db.bulk_save_objects(requirements)
    db.commit()
    print(f"✅ Generated {count} requirements")

if __name__ == "__main__":
    db = SessionLocal()
    generate_requirements(db, 15000)
    db.close()
```

---

### Step 6: Performance Testing (Day 5-6)

**File**: `backend/app/tests/test_performance.py`

```python
import pytest
import time
from fastapi.testclient import TestClient

def test_list_requirements_performance(client, auth_headers):
    """Test that listing requirements returns in < 200ms"""
    start = time.time()
    response = client.get("/api/requirements?limit=100", headers=auth_headers)
    duration = (time.time() - start) * 1000  # Convert to ms
    
    assert response.status_code == 200
    assert duration < 200, f"Response took {duration}ms, should be < 200ms"

def test_get_requirement_performance(client, auth_headers):
    """Test that getting a single requirement returns in < 50ms"""
    start = time.time()
    response = client.get("/api/requirements/1", headers=auth_headers)
    duration = (time.time() - start) * 1000
    
    assert response.status_code == 200
    assert duration < 50, f"Response took {duration}ms, should be < 50ms"
```

---

## Implementation Checklist

### Models & Database
- [ ] Create Requirement model
- [ ] Create TestCase model
- [ ] Create TraceabilityLink model
- [ ] Update User model relationships
- [ ] Set up Alembic
- [ ] Create initial migration
- [ ] Run migration

### Schemas
- [ ] Requirement schemas (Create, Update, Response)
- [ ] TestCase schemas
- [ ] TraceabilityLink schemas
- [ ] Pagination schemas

### API Routes
- [ ] Requirements CRUD (`/api/requirements`)
- [ ] Test Cases CRUD (`/api/test-cases`)
- [ ] Traceability Links CRUD (`/api/traceability`)
- [ ] Filtering & search
- [ ] Pagination support

### Testing
- [ ] Requirements API tests
- [ ] Test Cases API tests
- [ ] Traceability API tests
- [ ] Performance tests (<200ms)
- [ ] Integration tests
- [ ] Maintain >90% coverage

### Data Generation
- [ ] Sample data generator script
- [ ] Generate 15,000+ requirements
- [ ] Generate test cases
- [ ] Generate traceability links
- [ ] Seed script for development

### Documentation
- [ ] API documentation (auto-generated by FastAPI)
- [ ] Update README.md
- [ ] Create Week 2 sign-off document
- [ ] Update CLAUDE.md

---

## Success Criteria

✅ **All CRUD operations functional**
✅ **15,000+ requirements in database**
✅ **Response times < 200ms**
✅ **Test coverage > 90%**
✅ **Alembic migrations working**
✅ **API documentation complete**
✅ **All tests passing**

---

## Timeline

- **Day 1-2**: Models & Schemas
- **Day 3-4**: API Routes & Alembic
- **Day 5**: Sample Data Generation
- **Day 6**: Performance Testing & Documentation
- **Day 7**: Integration & Sign-off

---

**Status**: Ready for implementation  
**Estimated Duration**: 5-7 days  
**Prerequisites**: Week 1 complete ✅
