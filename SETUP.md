# CALIDUS Setup Instructions

## Prerequisites Installation

### 1. Install Docker Desktop

**macOS**:
```bash
# Using Homebrew
brew install --cask docker

# Or download from: https://www.docker.com/products/docker-desktop
```

**Verify Docker installation**:
```bash
docker --version
docker compose version
```

### 2. Clone and Setup

```bash
cd /Users/z/Documents/CALIDUS

# Ensure you're on the main branch
git checkout -b main

# Pull any existing changes from GitHub
git pull origin main
```

## Running the Project

### Step 1: Start Docker Services

```bash
# Build and start all containers
docker compose up -d --build

# This will start:
# - PostgreSQL database (port 5432)
# - Redis cache (port 6379)
# - FastAPI backend (port 8000)
```

### Step 2: Initialize Database

```bash
# Create database tables and seed demo users
docker compose exec backend python init_db.py
```

Expected output:
```
🚀 CALIDUS Database Initialization
==================================================
Creating database tables...
✅ Database tables created successfully!
Seeding demo users...
✅ Demo users created:
   - admin / demo2024 (Admin)
   - engineer / engineer2024 (Engineer)
   - viewer / viewer2024 (Viewer)
==================================================
✅ Database initialization complete!
```

### Step 3: Verify Installation

```bash
# Check services health
docker compose ps

# Test health endpoint
curl http://localhost:8000/health
# Should return: {"status":"healthy"}

# Test root endpoint
curl http://localhost:8000/
# Should return: {"app":"CALIDUS API","version":"1.0.0","status":"operational"}

# View API documentation
open http://localhost:8000/docs
```

## Running Tests

### Backend Tests (Required Before Each Commit)

```bash
# Run all tests with coverage
docker compose exec backend pytest -v --cov=app --cov-report=term-missing

# Expected output:
# - 15+ tests passing
# - Coverage ≥ 80%
```

### Test Individual Components

```bash
# Test authentication only
docker compose exec backend pytest app/tests/test_auth.py -v

# Test security functions
docker compose exec backend pytest app/tests/test_security.py -v

# Generate HTML coverage report
docker compose exec backend pytest --cov=app --cov-report=html
# View at: open backend/htmlcov/index.html
```

## Testing the API

### 1. Register a New User

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "testuser@example.com",
    "password": "testpass123"
  }'
```

### 2. Login and Get Token

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "demo2024"
  }'
```

Save the `access_token` from the response.

### 3. Access Protected Endpoint

```bash
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

## Development Workflow

### Making Changes

1. **Edit code** in your preferred IDE
2. **Backend auto-reloads** (hot-reload enabled)
3. **Run tests** before committing:
   ```bash
   docker compose exec backend pytest -v --cov=app
   ```
4. **Ensure all tests pass** (100% pass rate required)

### Viewing Logs

```bash
# All services
docker compose logs -f

# Backend only
docker compose logs -f backend

# Database only
docker compose logs -f db
```

### Stopping Services

```bash
# Stop all services
docker compose down

# Stop and remove volumes (clean slate)
docker compose down -v
```

### Restarting After Changes

```bash
# Restart backend only
docker compose restart backend

# Rebuild and restart everything
docker compose down
docker compose up -d --build
```

## Troubleshooting

### Issue: Database connection refused

**Solution**:
```bash
# Wait for database to be healthy
docker compose ps

# If db is not healthy, restart it
docker compose restart db

# Wait 10 seconds, then check again
sleep 10
docker compose ps
```

### Issue: Port already in use

**Solution**:
```bash
# Check what's using the port
lsof -i :8000  # For backend
lsof -i :5432  # For PostgreSQL

# Kill the process or change ports in docker-compose.yml
```

### Issue: Tests failing

**Solution**:
```bash
# Recreate test database
docker compose exec backend python -c "
from app.database import create_engine
from app.config import get_settings
from app.models import Base

settings = get_settings()
engine = create_engine(settings.test_database_url)
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
"

# Re-run tests
docker compose exec backend pytest -v
```

### Issue: Backend container crashes

**Solution**:
```bash
# View error logs
docker compose logs backend

# Common fixes:
# 1. Missing dependencies - rebuild:
docker compose up -d --build backend

# 2. Database not ready - wait and restart:
docker compose restart backend
```

## Week 1 Completion Checklist

Before moving to Week 2, ensure:

- [x] All files created
- [ ] Docker containers running successfully
- [ ] Database initialized with tables
- [ ] Demo users created (admin, engineer, viewer)
- [ ] Backend tests passing (15+ tests, ≥80% coverage)
- [ ] API accessible at http://localhost:8000
- [ ] Swagger docs viewable at http://localhost:8000/docs
- [ ] Can register user via API
- [ ] Can login and receive JWT token
- [ ] Can access protected endpoint with token
- [ ] Code committed to GitHub

## Next Steps

Once all tests pass, proceed with:

1. **Commit to GitHub** (see CONTRIBUTING.md)
2. **Create Pull Request** for Week 1
3. **Begin Week 2**: Requirements CRUD operations

---

**Support**: If you encounter issues, check:
1. Docker Desktop is running
2. No port conflicts (8000, 5432, 6379)
3. Sufficient disk space (>5GB)
4. Internet connection for pulling images

**Last Updated**: October 2025
