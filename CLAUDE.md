# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**CALIDUS** is an AI-powered Requirements Management & Traceability Assistant for aerospace engineering projects. The system manages 15,000+ requirements in ENOVIA PLM systems with automated traceability, compliance checking, and test coverage analysis across UAE, USA, and EU aerospace regulations.

**Current Status**: Phase 2, Week 4 (80% Complete) - Interactive Traceability Graph Implemented ✅

**Repository**: https://github.com/zozisteam/cls-requirement_management

**Last Updated**: October 19, 2025

---

## Current System Status

### Database Statistics
- **Requirements**: 16,600 (AHLR: 500, System: 5,000, Technical: 10,000, Certification: 1,100)
- **Test Cases**: 28,523 (linked to requirements)
- **Traceability Links**: 15,093 (parent/child relationships)
- **Users**: 3 (admin, engineer, viewer)

### Live Pages
**Frontend** (http://localhost:3000):
- ✅ `/` - Homepage with API status
- ✅ `/login` - Authentication
- ✅ `/demo` - Interactive demo with ENOVIA PLM import
- ✅ `/dashboard` - Main dashboard with statistics
- ✅ `/dashboard/requirements` - Requirements list with filters
- ✅ `/dashboard/requirements/[id]` - Requirement detail view
- ✅ `/dashboard/test-cases` - Test cases management
- ✅ `/dashboard/traceability` - Traceability matrix and gap analysis
- ✅ `/dashboard/traceability/graph` - Interactive network graph (NEW)
- ✅ `/dashboard/admin/users` - User management (admin only)

**Backend** (http://localhost:8000):
- ✅ `/api/auth/*` - Authentication endpoints
- ✅ `/api/requirements/*` - Requirements CRUD
- ✅ `/api/test-cases/*` - Test cases CRUD
- ✅ `/api/traceability/*` - Traceability operations & graph
- ✅ `/api/users/*` - User management
- ✅ `/docs` - Swagger API documentation
- ✅ `/redoc` - ReDoc API documentation

---

## Quick Start

### Running the Backend

```bash
# Start all backend services (FastAPI + PostgreSQL + Redis)
docker compose up -d

# Initialize database (first time only)
docker compose exec backend python init_db.py

# Run tests (MUST PASS before committing)
docker compose exec backend pytest -v --cov=app

# View logs
docker compose logs -f backend

# Stop services
docker compose down
```

### Running the Frontend

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm run start
```

### Running Full Stack

```bash
# Terminal 1: Start backend
docker compose up -d

# Terminal 2: Start frontend
cd frontend && npm run dev

# Access application
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

### Demo Credentials

- **Admin**: username: `admin`, password: `demo2024`
- **Engineer**: username: `engineer`, password: `engineer2024`
- **Viewer**: username: `viewer`, password: `viewer2024`

### Local URLs

**Backend API:**
- Health check: http://localhost:8000/health
- API root: http://localhost:8000/
- Swagger docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

**Frontend:**
- Homepage: http://localhost:3000
- Login: http://localhost:3000/login
- Demo: http://localhost:3000/demo

---

## Repository Structure

```
CALIDUS/
├── backend/                    # FastAPI backend (Python 3.11)
│   ├── app/
│   │   ├── api/               # API routes (auth, requirements, etc.)
│   │   │   └── auth.py        # Authentication endpoints (register, login, me)
│   │   ├── core/              # Core utilities
│   │   │   ├── security.py    # JWT & password hashing (bcrypt)
│   │   │   └── dependencies.py # Auth dependencies & middleware
│   │   ├── models/            # SQLAlchemy ORM models
│   │   │   └── user.py        # User model with roles
│   │   ├── schemas/           # Pydantic validation schemas
│   │   │   └── user.py        # User schemas (Create, Response, Login)
│   │   ├── tests/             # pytest test suite (96% coverage)
│   │   │   ├── conftest.py    # Test fixtures & configuration
│   │   │   ├── test_auth.py   # Authentication tests (11 tests)
│   │   │   └── test_security.py # Security tests (4 tests)
│   │   ├── config.py          # Configuration management (pydantic-settings)
│   │   ├── database.py        # Database connection & session
│   │   └── main.py            # FastAPI application entry point
│   ├── init_db.py             # Database initialization & seeding
│   ├── requirements.txt       # Production dependencies
│   ├── requirements-dev.txt   # Development dependencies (pytest, black, etc.)
│   ├── pytest.ini             # pytest configuration
│   ├── Dockerfile             # Backend container definition
│   └── .env.example           # Environment variables template
│
├── frontend/                   # Next.js 14 + TypeScript + Tailwind CSS
│   ├── app/
│   │   ├── demo/              # Interactive demo page
│   │   │   └── page.tsx       # Feature preview with tabs
│   │   ├── login/             # Login page
│   │   │   └── page.tsx       # Auth with demo account quick-fill
│   │   ├── globals.css        # Global styles with Tailwind
│   │   ├── layout.tsx         # Root layout with metadata
│   │   └── page.tsx           # Homepage with API status
│   ├── components/            # Reusable React components
│   ├── lib/                   # Utilities and helpers
│   ├── public/                # Static assets
│   ├── .env.local             # Environment variables (not committed)
│   ├── .env.example           # Environment template
│   ├── next.config.js         # Next.js configuration
│   ├── tailwind.config.ts     # Tailwind CSS configuration
│   ├── tsconfig.json          # TypeScript configuration
│   ├── vercel.json            # Vercel deployment config
│   ├── package.json           # Dependencies and scripts
│   └── README.md              # Frontend documentation
│
├── docker-compose.yml          # Multi-container orchestration (backend, db, redis)
├── .github/workflows/ci.yml    # GitHub Actions CI/CD pipeline
├── .gitignore                  # Git ignore patterns
│
├── README.md                   # Main project documentation
├── SETUP.md                    # Setup and installation guide
├── DOCKER_SETUP_GUIDE.md       # Docker troubleshooting guide
├── VERCEL_DEPLOYMENT.md        # Vercel deployment guide (frontend)
├── WEEK1_SIGN_OFF.md           # Week 1 completion report
├── demo_website_plan.md        # 67-page implementation blueprint
├── phase1_week1_implementation.md # Week 1 detailed guide
│
├── objectives.md               # Project objectives and features
├── regulations.md              # Aerospace regulations reference
└── file_extensions.md          # Aerospace file formats guide
```

---

## Technology Stack

### Backend (Operational ✅)
- **Framework**: FastAPI 0.104.1
- **Server**: uvicorn 0.24.0 with hot-reload
- **Database**: PostgreSQL 15 via SQLAlchemy 2.0.23
- **Cache**: Redis 7
- **Authentication**: JWT (python-jose 3.3.0)
- **Password Hashing**: bcrypt 4.0.1 (12 rounds)
- **Validation**: Pydantic 2.5.0 with EmailStr
- **Testing**: pytest 7.4.3 + pytest-cov 4.1.0
- **Code Quality**: black, flake8, mypy

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **Database**: PostgreSQL 15-alpine
- **Cache**: Redis 7-alpine
- **CI/CD**: GitHub Actions

### Frontend (Operational ✅)
- **Framework**: Next.js 14.2.3 (App Router)
- **Language**: TypeScript 5.4.5
- **Styling**: Tailwind CSS 3.4.3
- **HTTP Client**: Axios 1.6.8
- **Deployment**: Vercel-ready
- **Features**:
  - Server-side rendering (SSR)
  - Static generation
  - API proxy for CORS handling
  - Responsive design
  - Dark mode support (planned)

---

## Development Workflow

### Before Making Changes

1. **Pull latest code**: `git pull origin main`
2. **Check services are running**: `docker compose ps`
3. **Run tests to ensure baseline**: `docker compose exec backend pytest -v`

### Making Changes

1. **Create feature branch**: `git checkout -b feature/your-feature`
2. **Write tests first** (TDD approach)
3. **Implement feature**
4. **Run tests**: `docker compose exec backend pytest -v --cov=app`
5. **Ensure coverage ≥80%**: Check coverage report
6. **Format code**: `docker compose exec backend black app/`
7. **Check linting**: `docker compose exec backend flake8 app/`

### Committing Changes

**CRITICAL**: All tests MUST pass before committing!

```bash
# Run full test suite
docker compose exec backend pytest -v --cov=app --cov-report=term-missing

# Expected: 15/15 PASSED, Coverage ≥ 80%

# If tests pass, commit
git add .
git commit -m "feat: Your feature description

🚀 Generated with Claude Code (claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Push to GitHub
git push origin your-branch
```

### Testing Standards

**MUST MEET before merging**:
- ✅ All tests pass (100% pass rate)
- ✅ Code coverage ≥ 80%
- ✅ No flake8 errors
- ✅ Code formatted with black
- ✅ Type hints present (mypy compliant)

---

## Key Commands

### Docker Operations

```bash
# Start services
docker compose up -d

# Rebuild after dependency changes
docker compose up -d --build backend

# View logs
docker compose logs -f backend        # Backend only
docker compose logs -f                # All services

# Restart a service
docker compose restart backend

# Stop all services
docker compose down

# Clean slate (removes volumes)
docker compose down -v

# Check service health
docker compose ps
```

### Database Operations

```bash
# Initialize database (creates tables + demo users)
docker compose exec backend python init_db.py

# Access PostgreSQL shell
docker compose exec db psql -U calidus -d calidus

# Create test database (if not exists)
docker compose exec db psql -U calidus -c "CREATE DATABASE calidus_test;"

# Backup database
docker compose exec db pg_dump -U calidus calidus > backup.sql

# Restore database
docker compose exec -T db psql -U calidus calidus < backup.sql
```

### Testing Commands

```bash
# Run all tests with coverage
docker compose exec backend pytest -v --cov=app --cov-report=term-missing

# Run specific test file
docker compose exec backend pytest app/tests/test_auth.py -v

# Run specific test function
docker compose exec backend pytest app/tests/test_auth.py::test_login_success -v

# Generate HTML coverage report
docker compose exec backend pytest --cov=app --cov-report=html
# View at: backend/htmlcov/index.html

# Run tests with verbose output
docker compose exec backend pytest -vv

# Run tests and stop on first failure
docker compose exec backend pytest -x
```

### Code Quality Commands

```bash
# Format code with black
docker compose exec backend black app/

# Check formatting without changes
docker compose exec backend black --check app/

# Run flake8 linting
docker compose exec backend flake8 app/ --max-line-length=120

# Run mypy type checking
docker compose exec backend mypy app/ --ignore-missing-imports

# Run all quality checks
docker compose exec backend black app/ && \
docker compose exec backend flake8 app/ && \
docker compose exec backend mypy app/
```

### Frontend Commands

```bash
# Install dependencies
cd frontend && npm install

# Development server (http://localhost:3000)
npm run dev

# Production build
npm run build

# Start production server
npm run start

# Lint code
npm run lint

# Deploy to Vercel (requires Vercel CLI)
npm install -g vercel
vercel                    # Deploy to preview
vercel --prod             # Deploy to production
```

---

## Database Schema

### Current Models (Implemented)

#### User Model
```python
class User:
    id: int                    # Primary key
    username: str              # Unique, indexed
    email: str                 # Unique, indexed, validated
    hashed_password: str       # bcrypt hashed (never plain text)
    is_active: bool            # Default: True
    role: str                  # 'admin', 'engineer', or 'viewer'
    created_at: datetime       # Auto-generated
    updated_at: datetime       # Auto-updated on change
```

#### Requirement Model
```python
class Requirement:
    id: int                    # Primary key
    requirement_id: str        # Unique identifier (e.g., "AHLR-001")
    title: str                 # Requirement title
    description: str           # Detailed description
    type: str                  # AHLR, System, Technical, Certification
    status: str                # Draft, Approved, Under Review, Deprecated
    priority: str              # Critical, High, Medium, Low
    category: str              # FlightControl, Structures, etc.
    verification_method: str   # Test, Analysis, Inspection, Demonstration
    regulatory_document: str   # e.g., "14 CFR Part 23"
    regulatory_section: str    # e.g., "§23.143"
    regulatory_page: int       # Page number
    version: str               # Version number
    created_by_id: int         # Foreign key to User
    created_at: datetime
    updated_at: datetime
```

#### TestCase Model
```python
class TestCase:
    id: int                    # Primary key
    test_case_id: str          # Unique identifier (e.g., "TC-001")
    requirement_id: int        # Foreign key to Requirement
    title: str                 # Test case title
    description: str           # Test procedure
    test_type: str             # Unit, Integration, System, Acceptance
    status: str                # Pending, Passed, Failed, Blocked
    priority: str              # Critical, High, Medium, Low
    automated: bool            # Is this test automated?
    expected_result: str       # Expected outcome
    actual_result: str         # Actual test result
    execution_duration_sec: int
    executed_by_id: int        # Foreign key to User
    created_at: datetime
    updated_at: datetime
```

#### TraceabilityLink Model
```python
class TraceabilityLink:
    id: int                    # Primary key
    source_id: int             # Source requirement ID
    target_id: int             # Target requirement ID
    link_type: str             # Derives From, Satisfies, Verifies, etc.
    description: str           # Link description
    created_by_id: int         # Foreign key to User
    created_at: datetime
```

### Upcoming Models (Phase 2+)

- **RegulationMapping**: Detailed regulation-to-requirement mappings
- **CoverageHistory**: Historical test coverage tracking
- **ChangeRequest**: Impact analysis change requests
- **ComplianceReport**: Compliance audit reports

---

## API Endpoints

### Authentication (`/api/auth`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/register` | Register new user | ❌ |
| POST | `/api/auth/login` | Login and get JWT token | ❌ |
| GET | `/api/auth/me` | Get current user info | ✅ |

### System

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/` | API root and status | ❌ |
| GET | `/health` | Health check | ❌ |
| GET | `/docs` | Swagger UI | ❌ |
| GET | `/redoc` | ReDoc documentation | ❌ |

### Requirements (`/api/requirements`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/requirements` | List requirements (with filters) | ✅ |
| GET | `/api/requirements/{id}` | Get requirement by ID | ✅ |
| GET | `/api/requirements/by-req-id/{req_id}` | Get by requirement_id string | ✅ |
| GET | `/api/requirements/stats` | Get statistics | ✅ |
| POST | `/api/requirements` | Create requirement | ✅ |
| PUT | `/api/requirements/{id}` | Update requirement | ✅ |
| DELETE | `/api/requirements/{id}` | Delete requirement | ✅ |

### Test Cases (`/api/test-cases`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/test-cases` | List test cases (with filters) | ✅ |
| GET | `/api/test-cases/{id}` | Get test case by ID | ✅ |
| GET | `/api/test-cases/stats` | Get statistics | ✅ |
| POST | `/api/test-cases` | Create test case | ✅ |
| PUT | `/api/test-cases/{id}` | Update test case | ✅ |
| PATCH | `/api/test-cases/{id}/execute` | Record test execution | ✅ |
| DELETE | `/api/test-cases/{id}` | Delete test case | ✅ |

### Traceability (`/api/traceability`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/traceability` | List traceability links | ✅ |
| GET | `/api/traceability/{id}` | Get link by ID | ✅ |
| GET | `/api/traceability/matrix/{req_id}` | Get traceability matrix | ✅ |
| GET | `/api/traceability/graph` | Get graph data (NEW) | ✅ |
| GET | `/api/traceability/orphaned` | Get orphaned requirements | ✅ |
| GET | `/api/traceability/gaps` | Get traceability gaps | ✅ |
| GET | `/api/traceability/report` | Get full report | ✅ |
| POST | `/api/traceability` | Create link | ✅ |
| POST | `/api/traceability/bulk` | Bulk create links | ✅ |
| PUT | `/api/traceability/{id}` | Update link | ✅ |
| DELETE | `/api/traceability/{id}` | Delete link | ✅ |

### Users (`/api/users`) - Admin Only

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/users` | List users | ✅ (Admin) |
| GET | `/api/users/{id}` | Get user by ID | ✅ (Admin) |
| POST | `/api/users` | Create user | ✅ (Admin) |
| PUT | `/api/users/{id}` | Update user | ✅ (Admin) |
| DELETE | `/api/users/{id}` | Delete user | ✅ (Admin) |

### Upcoming (Phase 2, Weeks 5-7)

- `/api/compliance/*` - Compliance checking and regulation mapping
- `/api/coverage/*` - Test coverage analysis and heatmaps
- `/api/impact-analysis/*` - Impact analysis and change requests

---

## Testing Philosophy

### Test-Driven Development (TDD)

1. **Write test first** - Define expected behavior
2. **Run test** - It should fail (red)
3. **Write minimal code** - Make test pass (green)
4. **Refactor** - Improve code while tests pass
5. **Repeat** - For each new feature

### Test Structure

```python
# Test file: app/tests/test_feature.py

def test_feature_success(client):
    """Test successful case with valid data"""
    response = client.post("/api/endpoint", json={"key": "value"})
    assert response.status_code == 200
    assert response.json()["key"] == "value"

def test_feature_validation_error(client):
    """Test validation with invalid data"""
    response = client.post("/api/endpoint", json={"invalid": "data"})
    assert response.status_code == 422  # Validation error

def test_feature_unauthorized(client):
    """Test auth protection"""
    response = client.get("/api/protected")
    assert response.status_code == 401
```

### Current Test Coverage (Week 1)

- **Total Tests**: 15
- **Pass Rate**: 100%
- **Coverage**: 96%
- **Modules Covered**: auth, security, models, schemas, config, main

---

## Common Tasks

### Adding a New API Endpoint

1. **Define Pydantic schema** in `app/schemas/`
2. **Create SQLAlchemy model** in `app/models/` (if needed)
3. **Write tests** in `app/tests/test_*.py`
4. **Create route** in `app/api/`
5. **Include router** in `app/main.py`
6. **Run tests** - ensure 100% pass rate
7. **Check coverage** - ensure ≥80%

### Adding a New Database Model

1. **Create model** in `app/models/your_model.py`
2. **Import in** `app/models/__init__.py`
3. **Create schemas** in `app/schemas/your_model.py`
4. **Write tests** for CRUD operations
5. **Create migration** (Week 2: Alembic)
6. **Run tests** to validate

### Debugging Failed Tests

```bash
# Run tests with verbose output
docker compose exec backend pytest -vv

# Run specific failing test
docker compose exec backend pytest app/tests/test_file.py::test_name -vv

# Add breakpoint in code
import pdb; pdb.set_trace()

# Check test database state
docker compose exec db psql -U calidus -d calidus_test -c "SELECT * FROM users;"

# View backend logs
docker compose logs backend --tail=50
```

---

## Aerospace Domain Context

### Regulatory Compliance

CALIDUS must support compliance across multiple jurisdictions:

**UAE (GCAA)**:
- General Civil Aviation Regulations (CAR)
- UAEMAR-21 (Certification)
- UAEMAR-M (Continuing Airworthiness)

**USA (FAA)**:
- 14 CFR Part 21 (Certification Procedures)
- 14 CFR Part 23 (Normal Category Airplanes)
- 14 CFR Part 25 (Transport Category)
- 14 CFR Part 33 (Aircraft Engines)
- DO-178C (Software considerations)
- MIL-HDBK-516C (Airworthiness certification)

**EU (EASA)**:
- Part-21 (Certification)
- CS-23 (Normal, Utility, Acrobatic, Commuter)
- CS-25 (Large Aeroplanes)
- EMAR-21 (Military certification)

**International**:
- ICAO Annexes (various)
- NATO STANAGs (military standards)

### Requirement Types

1. **AHLR** (Aircraft High-Level Requirements)
   - Top-level system requirements
   - Maps to certification basis

2. **System Requirements**
   - Derived from AHLR
   - Subsystem-level specifications

3. **Technical Specifications**
   - Detailed design requirements
   - Component-level specs

4. **Certification Requirements**
   - Regulatory compliance requirements
   - Tied to specific regulations

### File Formats

CALIDUS will integrate with aerospace tools producing:
- **Requirements**: .REQIF, .DOORS, .JSON, .XML, .CSV
- **CAD**: .CATPART, .SLDPRT, .STEP, .IGES
- **Simulation**: .BDF (NASTRAN), .CDB (ANSYS), .INP (ABAQUS)
- **Testing**: .TDMS (LabVIEW), .HDF5, .MAT, .CSV
- **Documentation**: .PDF, .DOCX, .PPTX

---

## Troubleshooting

### Tests Failing

**Issue**: Tests fail with database connection errors

```bash
# Ensure test database exists
docker compose exec db psql -U calidus -c "CREATE DATABASE IF NOT EXISTS calidus_test;"

# Restart backend
docker compose restart backend

# Re-run tests
docker compose exec backend pytest -v
```

**Issue**: Import errors or missing dependencies

```bash
# Rebuild container with latest requirements
docker compose up -d --build backend
```

### Docker Issues

**Issue**: Port already in use (8000, 5432, 6379)

```bash
# Check what's using the port
lsof -i :8000

# Kill process or change port in docker-compose.yml
```

**Issue**: Services not healthy

```bash
# Check logs
docker compose logs backend
docker compose logs db

# Restart services
docker compose restart

# Nuclear option: clean slate
docker compose down -v
docker compose up -d --build
```

### Code Coverage Below 80%

```bash
# Generate detailed coverage report
docker compose exec backend pytest --cov=app --cov-report=html

# Open htmlcov/index.html to see which lines are missing coverage
# Add tests for uncovered code paths
```

---

## Deployment

### Frontend Deployment (Vercel)

The frontend is production-ready and can be deployed to Vercel with zero configuration.

**Prerequisites:**
- Backend API deployed and publicly accessible
- Vercel account (free tier available)

**Quick Deploy:**

```bash
# Install Vercel CLI
npm install -g vercel

# Navigate to frontend
cd frontend

# Login to Vercel
vercel login

# Deploy to production
vercel --prod
```

**Environment Variables (Vercel Dashboard):**
- `NEXT_PUBLIC_API_URL` = Your production backend URL

**See [VERCEL_DEPLOYMENT.md](./VERCEL_DEPLOYMENT.md) for complete deployment guide.**

### Backend Deployment Options

**Option 1: Railway.app** (Recommended for quick deploy)
```bash
railway login
cd backend
railway up
```

**Option 2: Render.com** (Free tier available)
- Connect GitHub repository
- Select backend directory
- Use Docker deployment

**Option 3: Fly.io** (Easy CLI deployment)
```bash
fly auth login
cd backend
fly launch
```

**Option 4: VPS (DigitalOcean/AWS/Linode)**
```bash
# On server
git clone https://github.com/zozisteam/cls-requirement_management.git
cd cls-requirement_management
docker compose up -d
```

### Local Testing URLs

**Backend:**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

**Frontend:**
- App: http://localhost:3000
- Login: http://localhost:3000/login
- Demo: http://localhost:3000/demo

---

## Project Roadmap

### ✅ Phase 1, Week 1: Foundation (COMPLETE)
- ✅ Backend API with authentication
- ✅ JWT security implementation
- ✅ User management with role-based access
- ✅ Docker environment (PostgreSQL + Redis)
- ✅ 96% test coverage (15/15 tests passing)
- ✅ CI/CD pipeline (GitHub Actions)
- ✅ Next.js frontend with interactive demo
- ✅ Vercel deployment ready
- ✅ Comprehensive documentation
- ✅ Login page with demo account quick-fill
- ✅ Homepage with API status monitoring
- ✅ Responsive UI with Tailwind CSS

### ✅ Phase 1, Week 2: Core Backend (COMPLETE)
- ✅ Requirements CRUD operations (16,600 requirements)
- ✅ Test cases CRUD operations (28,523 test cases)
- ✅ Traceability link management (15,093 links)
- ✅ Database migrations (Alembic)
- ✅ Sample data generation (synthetic aerospace data from 14 CFR Part 23)
- ✅ Performance testing (<200ms response time)

### ✅ Phase 1, Week 3: Enhanced Frontend (COMPLETE)
- ✅ Dashboard with data visualization
- ✅ Requirements list view with filtering
- ✅ Advanced search functionality
- ✅ User management interface (admin)
- ✅ Real-time API integration
- ✅ Requirement modal with traceability navigation
- ✅ Test cases page with execution tracking
- ✅ Production build optimized

### 🟡 Phase 2, Week 4: Interactive Traceability (80% COMPLETE)
- ✅ Backend graph API (`/api/traceability/graph`)
- ✅ Orphaned requirements detection
- ✅ Gap analysis endpoint
- ✅ Interactive graph visualization (Cytoscape.js)
- ✅ Zoom/pan/filter controls
- ✅ Node coloring by requirement type
- ⏳ Export to PNG/SVG (pending)
- ⏳ Export matrix to Excel (pending)

### 📅 Phase 2, Week 5: Compliance Dashboard (NOT STARTED)
- Compliance API endpoints
- Regulation mapping (14 CFR Part 23, EASA CS-23, UAE GCAA)
- Coverage metrics and gap analysis
- Compliance reporting

### 📅 Phase 2, Week 6: Impact Analysis (NOT STARTED)
- Impact analysis algorithm
- Upstream/downstream traversal
- Risk scoring
- Change request workflow

### 📅 Phase 2, Week 7: Test Coverage Analyzer (NOT STARTED)
- Coverage heatmap (type × priority)
- Gap identification
- Test suggestions
- Coverage trends

### 📅 Phase 3 (Weeks 8-10): AI/ML Integration
- NLP models (Sentence Transformers)
- Vector database (Weaviate)
- AI-powered trace link suggestions
- Requirement categorization
- Duplication detection

### 📅 Phase 4 (Weeks 11-12): Polish & Deployment
- Production deployment (AWS/Azure/GCP)
- Performance optimization
- Security audit
- User acceptance testing
- Documentation finalization

---

## Important Notes

### Security Considerations

- ✅ **Never commit** `.env` files with real credentials
- ✅ **Change `SECRET_KEY`** in production (see `config.py`)
- ✅ **Passwords are never stored in plain text** (bcrypt hashed)
- ✅ **JWT tokens expire** after 60 minutes (configurable)
- ✅ **CORS is whitelisted** (see `config.py`)
- ✅ **SQL injection protected** (SQLAlchemy ORM only)

### Performance Notes

- Database connection pooling is enabled (SQLAlchemy)
- Redis caching ready (not yet implemented)
- Response times should be < 200ms (Week 2 testing)
- Pagination required for large datasets (Week 2)

### Code Style

- **Python**: Follow PEP 8 (enforced by black + flake8)
- **Line length**: 120 characters max
- **Imports**: Sorted (isort)
- **Type hints**: Required for all functions
- **Docstrings**: Required for all public functions
- **Comments**: Explain "why", not "what"

---

## Resources

### Documentation
- [README.md](README.md) - Project overview
- [SETUP.md](SETUP.md) - Installation guide
- [DOCKER_SETUP_GUIDE.md](DOCKER_SETUP_GUIDE.md) - Docker troubleshooting
- [WEEK1_SIGN_OFF.md](WEEK1_SIGN_OFF.md) - Week 1 completion report
- [demo_website_plan.md](demo_website_plan.md) - Full implementation plan

### External Documentation
- FastAPI: https://fastapi.tiangolo.com/
- SQLAlchemy: https://docs.sqlalchemy.org/
- Pydantic: https://docs.pydantic.dev/
- pytest: https://docs.pytest.org/
- Docker Compose: https://docs.docker.com/compose/

### GitHub
- Repository: https://github.com/zozisteam/cls-requirement_management
- Issues: https://github.com/zozisteam/cls-requirement_management/issues
- Actions (CI/CD): https://github.com/zozisteam/cls-requirement_management/actions

---

**Last Updated**: October 19, 2025
**Current Phase**: Phase 2, Week 4 (80% Complete) - Interactive Traceability Graph Implemented
**Status**: 16,600 requirements | 28,523 test cases | 15,093 trace links | Interactive graph visualization ✅
