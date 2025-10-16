# CALIDUS - AI-Powered Requirements Management & Traceability

[![GitHub](https://img.shields.io/badge/GitHub-cls--requirement__management-blue)](https://github.com/zozisteam/cls-requirement_management)

An agentic framework for automated requirements traceability, compliance checking, and verification mapping in aerospace engineering projects managing 15,000+ requirements in ENOVIA PLM systems.

## 🎯 Project Overview

CALIDUS automates end-to-end traceability between:
- Requirements (Technical, System, Certification, AHLR)
- Design elements
- Test cases
- Verification results
- Change requests and risks

Ensures full compliance across UAE, USA, and EU aerospace regulations.

## 🏗️ Architecture

- **Backend**: FastAPI (Python 3.11+)
- **Frontend**: React + TypeScript (Coming in Week 1)
- **Database**: PostgreSQL 15
- **Cache**: Redis 7
- **AI/ML**: Sentence Transformers, Weaviate (Coming in Phase 2)
- **Deployment**: Docker + Docker Compose

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Git
- Python 3.11+ (for local development)
- Node.js 18+ (for frontend development)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/zozisteam/cls-requirement_management.git
cd cls-requirement_management
```

2. **Start services with Docker**
```bash
docker-compose up -d
```

3. **Initialize the database**
```bash
docker-compose exec backend python -c "from app.database import engine; from app.models import Base; Base.metadata.create_all(bind=engine)"
```

4. **Verify installation**
```bash
# Check health
curl http://localhost:8000/health
# Should return: {"status":"healthy"}

# View API docs
open http://localhost:8000/docs
```

## 🧪 Running Tests

### Backend Tests

```bash
# Run all tests with coverage
docker-compose exec backend pytest -v --cov=app --cov-report=term-missing

# Run specific test file
docker-compose exec backend pytest app/tests/test_auth.py -v

# Generate HTML coverage report
docker-compose exec backend pytest --cov=app --cov-report=html
# View at backend/htmlcov/index.html
```

**Expected Results (Week 1)**:
- ✅ 15+ tests passing
- ✅ Coverage ≥ 80%

### Frontend Tests (Coming Soon)

```bash
cd frontend
npm test -- --coverage
```

## 📁 Project Structure

```
CALIDUS/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/               # API routes
│   │   ├── core/              # Security, dependencies
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── tests/             # Pytest tests
│   │   ├── config.py          # Configuration
│   │   ├── database.py        # Database connection
│   │   └── main.py            # FastAPI app
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── pytest.ini
│   └── Dockerfile
├── frontend/                   # React frontend (Coming Soon)
├── docker-compose.yml          # Multi-container orchestration
├── .gitignore
└── README.md
```

## 🔐 Authentication

The API uses JWT (JSON Web Tokens) for authentication.

### Register a User

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "demo",
    "email": "demo@example.com",
    "password": "demo2024"
  }'
```

### Login

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "demo",
    "password": "demo2024"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Access Protected Endpoints

```bash
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 📊 API Documentation

Interactive API documentation available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🛠️ Development

### Local Backend Development (without Docker)

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt -r requirements-dev.txt

# Set environment variables
cp .env.example .env
# Edit .env with your local database URL

# Run the server
uvicorn app.main:app --reload

# Run tests
pytest -v --cov=app
```

### Database Migrations (Coming Soon)

We use Alembic for database migrations:

```bash
# Create a migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## 📈 Development Roadmap

### ✅ Phase 1, Week 1: Foundation (CURRENT)
- [x] Project setup and repository structure
- [x] Backend API with FastAPI
- [x] User authentication (register, login, JWT)
- [x] Docker configuration
- [x] Comprehensive testing suite (15+ tests)
- [ ] Frontend login page
- [ ] CI/CD pipeline

### 📅 Phase 1, Week 2: Core Backend
- [ ] Requirements CRUD operations
- [ ] Test cases CRUD operations
- [ ] Traceability link management
- [ ] Database migrations (Alembic)
- [ ] Sample data generation

### 📅 Phase 1, Week 3: Core Frontend
- [ ] Dashboard layout
- [ ] Navigation system
- [ ] Requirements list view
- [ ] Basic search and filtering

### 📅 Phase 2 (Weeks 4-7): Core Features
- [ ] Interactive traceability visualizations
- [ ] Compliance dashboard
- [ ] Impact analysis tool
- [ ] Test coverage analyzer

### 📅 Phase 3 (Weeks 8-10): AI/ML Integration
- [ ] NLP models integration
- [ ] Vector database setup
- [ ] AI-powered trace link suggestions
- [ ] Ambiguity detection

### 📅 Phase 4 (Weeks 11-12): Polish & Deployment
- [ ] Production deployment
- [ ] Performance optimization
- [ ] Security audit
- [ ] User documentation

## 🧪 Testing Standards

All code must meet the following criteria before merging:

- **Backend**: ≥80% test coverage
- **Frontend**: ≥70% test coverage
- **All tests passing**: 100% pass rate
- **Code style**: Black (Python), Prettier (TypeScript)
- **Type checking**: mypy (Python), TypeScript strict mode

## 🤝 Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Write tests first (TDD approach)
3. Implement feature
4. Ensure all tests pass: `pytest -v --cov=app`
5. Commit with descriptive message
6. Push and create Pull Request

## 📝 Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# Application
APP_NAME=CALIDUS API
DEBUG=true

# Database
DATABASE_URL=postgresql://calidus:calidus123@db:5432/calidus
TEST_DATABASE_URL=postgresql://calidus:calidus123@db:5432/calidus_test

# Redis
REDIS_URL=redis://redis:6379/0

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# CORS
CORS_ORIGINS=["http://localhost:3000"]
```

## 🔒 Security

- Passwords hashed with bcrypt (12 rounds)
- JWT tokens with configurable expiration
- CORS protection
- SQL injection protection (SQLAlchemy ORM)
- Rate limiting (Coming Soon)

**Note**: Change `SECRET_KEY` in production!

## 📄 License

[Add your license here]

## 👥 Team

Developed by the ZOZI Team for aerospace requirements management.

## 📧 Support

For issues and questions:
- GitHub Issues: https://github.com/zozisteam/cls-requirement_management/issues
- Email: [Your email]

---

**Current Status**: Week 1 - Backend Foundation Complete ✅

**Last Updated**: October 2025
