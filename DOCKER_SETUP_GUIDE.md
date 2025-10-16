# Docker Setup and Testing Guide

## Current Status

✅ Docker Desktop downloaded to `/Applications/Docker.app`
⏳ Manual steps required to complete setup

---

## Step 1: Complete Docker Installation

### Option A: Open Docker Desktop (Recommended)

```bash
# Open Docker Desktop application
open /Applications/Docker.app
```

**What will happen**:
1. Docker Desktop will launch
2. You may be prompted to enter your password for system permissions
3. Docker will start and show a whale icon in your menu bar
4. Wait for the whale icon to stop animating (Docker is ready)

### Option B: Reinstall with sudo

If Docker.app doesn't open properly, reinstall:

```bash
# Remove incomplete installation
rm -rf /Applications/Docker.app

# Reinstall (you'll be prompted for password)
brew reinstall --cask docker

# Then open it
open /Applications/Docker.app
```

---

## Step 2: Verify Docker Installation

Once Docker Desktop is running, verify installation:

```bash
# Check Docker version
docker --version
# Expected: Docker version 4.48.0 or similar

# Check Docker Compose
docker compose version
# Expected: Docker Compose version v2.x.x or similar

# Test Docker is working
docker run hello-world
# Should download and run a test container
```

---

## Step 3: Start CALIDUS Services

### 3.1 Navigate to Project Directory

```bash
cd /Users/z/Documents/CALIDUS
```

### 3.2 Build and Start Containers

```bash
# Build and start all services
docker compose up -d --build
```

**Expected output**:
```
[+] Running 3/3
 ✔ Container calidus-db-1      Started
 ✔ Container calidus-redis-1   Started
 ✔ Container calidus-backend-1 Started
```

### 3.3 Wait for Services to be Healthy

```bash
# Check services status
docker compose ps
```

**Expected output**:
```
NAME                  IMAGE               STATUS          PORTS
calidus-backend-1     calidus-backend     Up (healthy)    0.0.0.0:8000->8000/tcp
calidus-db-1          postgres:15-alpine  Up (healthy)    0.0.0.0:5432->5432/tcp
calidus-redis-1       redis:7-alpine      Up (healthy)    0.0.0.0:6379->6379/tcp
```

**If services aren't healthy yet**, wait 10-20 seconds and check again.

---

## Step 4: Initialize Database

```bash
# Create database tables and seed demo users
docker compose exec backend python init_db.py
```

**Expected output**:
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

---

## Step 5: Run Backend Tests (CRITICAL)

This is the most important step - all tests MUST pass before Week 2.

```bash
# Run all tests with coverage
docker compose exec backend pytest -v --cov=app --cov-report=term-missing
```

### Expected Test Results:

```
==================== test session starts ====================
platform linux -- Python 3.11.x, pytest-7.4.3
cachedir: .pytest_cache
rootdir: /app
configfile: pytest.ini
plugins: cov-4.1.0, asyncio-0.21.1
collected 15 items

app/tests/test_auth.py::test_health_check PASSED                     [  6%]
app/tests/test_auth.py::test_root_endpoint PASSED                    [ 13%]
app/tests/test_auth.py::test_register_user PASSED                    [ 20%]
app/tests/test_auth.py::test_register_duplicate_username PASSED      [ 26%]
app/tests/test_auth.py::test_register_duplicate_email PASSED         [ 33%]
app/tests/test_auth.py::test_login_success PASSED                    [ 40%]
app/tests/test_auth.py::test_login_wrong_password PASSED             [ 46%]
app/tests/test_auth.py::test_login_nonexistent_user PASSED           [ 53%]
app/tests/test_auth.py::test_get_current_user PASSED                 [ 60%]
app/tests/test_auth.py::test_get_current_user_unauthorized PASSED    [ 66%]
app/tests/test_auth.py::test_get_current_user_invalid_token PASSED   [ 73%]
app/tests/test_security.py::test_password_hashing PASSED             [ 80%]
app/tests/test_security.py::test_create_and_decode_token PASSED      [ 86%]
app/tests/test_security.py::test_token_with_expiration PASSED        [ 93%]
app/tests/test_security.py::test_invalid_token PASSED                [100%]

---------- coverage: platform linux, python 3.11.x -----------
Name                                  Stmts   Miss  Cover   Missing
-------------------------------------------------------------------
app/__init__.py                           0      0   100%
app/api/__init__.py                       0      0   100%
app/api/auth.py                          28      0   100%
app/config.py                            15      0   100%
app/core/__init__.py                      0      0   100%
app/core/dependencies.py                 18      0   100%
app/core/security.py                     17      0   100%
app/database.py                          11      0   100%
app/main.py                              13      0   100%
app/models/__init__.py                    2      0   100%
app/models/user.py                        8      0   100%
app/schemas/__init__.py                   0      0   100%
app/schemas/user.py                      12      0   100%
-------------------------------------------------------------------
TOTAL                                   124      0   100%

Required test coverage of 80.0% reached. Total coverage: 100.00%
==================== 15 passed in 2.34s ====================
```

### ✅ Success Criteria:

- [x] **15 out of 15 tests PASSED** (100%)
- [x] **Coverage: ≥80%** (should be 85-100%)
- [x] **0 failed tests**
- [x] **0 errors**

### ❌ If Tests Fail:

Check the logs:
```bash
docker compose logs backend
```

Common issues:
1. **Database not ready**: Wait 10 more seconds, retry
2. **Module import errors**: Rebuild container: `docker compose up -d --build backend`
3. **Connection errors**: Check services are healthy: `docker compose ps`

---

## Step 6: Test API Endpoints

### 6.1 Health Check

```bash
curl http://localhost:8000/health
```

**Expected**: `{"status":"healthy"}`

### 6.2 Root Endpoint

```bash
curl http://localhost:8000/
```

**Expected**:
```json
{
  "app": "CALIDUS API",
  "version": "1.0.0",
  "status": "operational"
}
```

### 6.3 View API Documentation

```bash
open http://localhost:8000/docs
```

**Expected**: Swagger UI with API documentation

### 6.4 Register a Test User

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "testuser@example.com",
    "password": "testpass123"
  }'
```

**Expected**:
```json
{
  "username": "testuser",
  "email": "testuser@example.com",
  "id": 4,
  "is_active": true,
  "role": "viewer",
  "created_at": "2025-10-16T..."
}
```

### 6.5 Login

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123"
  }'
```

**Expected**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Save the `access_token`** for the next step!

### 6.6 Access Protected Endpoint

```bash
# Replace YOUR_TOKEN_HERE with the actual token from step 6.5
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Expected**:
```json
{
  "username": "testuser",
  "email": "testuser@example.com",
  "id": 4,
  "is_active": true,
  "role": "viewer",
  "created_at": "2025-10-16T..."
}
```

---

## Step 7: Verify GitHub Actions

Check automated CI/CD:

1. Go to: https://github.com/zozisteam/cls-requirement_management/actions
2. Look for the latest workflow run
3. Verify all jobs pass:
   - ✅ Backend Tests
   - ✅ Code Quality
   - ✅ Docker Build Test
   - ✅ Security Scan

---

## Week 1 Completion Checklist

Mark each item as you complete it:

### Infrastructure
- [ ] Docker Desktop installed and running
- [ ] Whale icon in menu bar (not animating)
- [ ] `docker --version` works
- [ ] `docker compose version` works

### Services
- [ ] `docker compose ps` shows all 3 services healthy
- [ ] Database initialized (tables created)
- [ ] Demo users seeded (admin, engineer, viewer)

### Testing (CRITICAL)
- [ ] **All 15 backend tests pass (100%)**
- [ ] **Test coverage ≥ 80%**
- [ ] No test errors or failures

### API Verification
- [ ] Health check returns `{"status":"healthy"}`
- [ ] Root endpoint returns app info
- [ ] Swagger docs accessible at http://localhost:8000/docs
- [ ] Can register new user
- [ ] Can login and receive JWT token
- [ ] Can access protected `/api/auth/me` endpoint

### CI/CD
- [ ] GitHub Actions workflow passes
- [ ] All 4 CI jobs successful (tests, quality, docker, security)

---

## Troubleshooting

### Issue: Docker command not found after installation

**Solution**:
```bash
# Restart your terminal or reload shell
source ~/.zshrc

# Or add Docker to PATH manually
export PATH="/Applications/Docker.app/Contents/Resources/bin:$PATH"
```

### Issue: Port 8000/5432/6379 already in use

**Solution**:
```bash
# Check what's using the ports
lsof -i :8000
lsof -i :5432
lsof -i :6379

# Kill the process or change ports in docker-compose.yml
```

### Issue: Database connection refused

**Solution**:
```bash
# Wait for database to be healthy
docker compose ps

# If db is unhealthy, restart it
docker compose restart db

# Wait 10 seconds
sleep 10
docker compose ps
```

### Issue: Tests failing

**Solution**:
```bash
# View backend logs
docker compose logs backend --tail=50

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

### Issue: Services won't start

**Solution**:
```bash
# Stop everything
docker compose down -v

# Rebuild from scratch
docker compose up -d --build --force-recreate

# Wait 20 seconds
sleep 20

# Check status
docker compose ps
```

---

## Useful Docker Commands

```bash
# View logs for all services
docker compose logs -f

# View logs for backend only
docker compose logs -f backend

# Restart a specific service
docker compose restart backend

# Stop all services
docker compose down

# Stop and remove volumes (clean slate)
docker compose down -v

# Rebuild a specific service
docker compose up -d --build backend

# Enter backend container shell
docker compose exec backend bash

# Run Python interactively
docker compose exec backend python
```

---

## Next Steps After All Tests Pass

Once you've completed all items in the checklist:

1. ✅ **Week 1 is COMPLETE!**
2. 📸 Take screenshot of test results
3. 📋 Review [WEEK1_COMPLETION_SUMMARY.md](WEEK1_COMPLETION_SUMMARY.md)
4. 🚀 Ready to begin Week 2!

Week 2 will add:
- Requirements CRUD operations
- Test cases CRUD operations
- Traceability link management
- Database migrations
- Sample data generation (15,000+ requirements)

---

**Last Updated**: October 2025
**Support**: See [SETUP.md](SETUP.md) for detailed troubleshooting
