# CALIDUS Phase 1, Week 1: Foundation with Test-Driven Development

## Overview

This document outlines the detailed implementation steps for Week 1 of the CALIDUS demo website project, with comprehensive testing requirements at each stage.

**Testing Philosophy**: Write tests first, implement features, ensure all tests pass before moving to next step.

---

## Week 1 Implementation Checklist

### Day 1-2: Project Setup & Repository Structure

#### Step 1.1: Create Project Directory Structure

```bash
CALIDUS/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI application entry
│   │   ├── config.py          # Configuration management
│   │   ├── database.py        # Database connection
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── api/               # API routes
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── requirements.py
│   │   │   └── traceability.py
│   │   ├── core/              # Core utilities
│   │   │   ├── __init__.py
│   │   │   ├── security.py    # JWT, password hashing
│   │   │   └── dependencies.py
│   │   └── tests/             # Test directory
│   │       ├── __init__.py
│   │       ├── conftest.py    # Pytest fixtures
│   │       ├── test_auth.py
│   │       ├── test_requirements.py
│   │       └── test_database.py
│   ├── requirements.txt       # Python dependencies
│   ├── requirements-dev.txt   # Dev dependencies (pytest, etc.)
│   ├── .env.example          # Environment variables template
│   ├── pytest.ini            # Pytest configuration
│   └── Dockerfile            # Backend container
│
├── frontend/                  # React frontend
│   ├── public/
│   ├── src/
│   │   ├── components/       # React components
│   │   │   ├── Auth/
│   │   │   │   ├── Login.tsx
│   │   │   │   └── Login.test.tsx
│   │   │   ├── Dashboard/
│   │   │   └── Common/
│   │   ├── services/         # API services
│   │   │   ├── api.ts
│   │   │   └── api.test.ts
│   │   ├── utils/            # Utility functions
│   │   ├── hooks/            # Custom React hooks
│   │   ├── types/            # TypeScript types
│   │   ├── App.tsx
│   │   ├── App.test.tsx
│   │   └── setupTests.ts
│   ├── package.json
│   ├── tsconfig.json
│   ├── jest.config.js        # Jest configuration
│   └── Dockerfile            # Frontend container
│
├── docker-compose.yml         # Multi-container orchestration
├── .github/
│   └── workflows/
│       └── ci.yml            # GitHub Actions CI/CD
├── README.md
└── .gitignore
```

**Tests to Pass**:
- ✅ Directory structure created correctly
- ✅ All __init__.py files exist for Python modules
- ✅ Git repository initialized with .gitignore

---

### Step 1.2: Initialize Backend with FastAPI

#### File: `backend/requirements.txt`

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
pydantic==2.5.0
pydantic-settings==2.1.0
alembic==1.12.1
redis==5.0.1
```

#### File: `backend/requirements-dev.txt`

```txt
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
httpx==0.25.2
faker==20.1.0
black==23.12.0
flake8==6.1.0
mypy==1.7.1
```

#### File: `backend/app/config.py`

```python
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Application
    app_name: str = "CALIDUS API"
    app_version: str = "1.0.0"
    debug: bool = False

    # Database
    database_url: str = "postgresql://calidus:calidus123@db:5432/calidus"
    test_database_url: str = "postgresql://calidus:calidus123@db:5432/calidus_test"

    # Redis
    redis_url: str = "redis://redis:6379/0"

    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7

    # CORS
    cors_origins: list = ["http://localhost:3000", "http://localhost:3001"]

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

#### File: `backend/app/database.py`

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    echo=settings.debug
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency for database sessions"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

#### File: `backend/app/main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.api import auth

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
```

#### File: `backend/app/models/__init__.py`

```python
from app.database import Base
from app.models.user import User

__all__ = ["Base", "User"]
```

#### File: `backend/app/models/user.py`

```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(String, default="viewer")  # admin, viewer, engineer
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

#### File: `backend/app/schemas/user.py`

```python
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str
```

#### File: `backend/app/core/security.py`

```python
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import get_settings

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and verify a JWT token"""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError:
        return None
```

#### File: `backend/app/core/dependencies.py`

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.security import decode_access_token
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get the current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Ensure the current user is active"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
```

#### File: `backend/app/api/auth.py`

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, LoginRequest, Token
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.dependencies import get_current_active_user

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user exists
    existing_user = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )

    # Create new user
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=get_password_hash(user.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Login and receive access token"""
    user = db.query(User).filter(User.username == login_data.username).first()

    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    access_token = create_access_token(data={"sub": user.username})

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Get current user information"""
    return current_user
```

---

### Step 1.3: Backend Testing Setup

#### File: `backend/pytest.ini`

```ini
[pytest]
testpaths = app/tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --cov=app
    --cov-report=term-missing
    --cov-report=html
    --asyncio-mode=auto
```

#### File: `backend/app/tests/conftest.py`

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.config import get_settings
from app.core.security import get_password_hash
from app.models.user import User

settings = get_settings()

# Test database
SQLALCHEMY_DATABASE_URL = settings.test_database_url
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with overridden database dependency"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """Create a test user"""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpass123"),
        role="engineer",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def admin_user(db_session):
    """Create an admin user"""
    user = User(
        username="admin",
        email="admin@example.com",
        hashed_password=get_password_hash("adminpass123"),
        role="admin",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(client, test_user):
    """Get authentication headers for test user"""
    response = client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "testpass123"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
```

#### File: `backend/app/tests/test_auth.py`

```python
import pytest
from fastapi import status


def test_health_check(client):
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "healthy"}


def test_root_endpoint(client):
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "app" in data
    assert "version" in data
    assert data["status"] == "operational"


def test_register_user(client):
    """Test user registration"""
    response = client.post(
        "/api/auth/register",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "securepass123"
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@example.com"
    assert "id" in data
    assert "hashed_password" not in data  # Password should not be returned


def test_register_duplicate_username(client, test_user):
    """Test registration with existing username"""
    response = client.post(
        "/api/auth/register",
        json={
            "username": "testuser",  # Already exists
            "email": "different@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already registered" in response.json()["detail"]


def test_register_duplicate_email(client, test_user):
    """Test registration with existing email"""
    response = client.post(
        "/api/auth/register",
        json={
            "username": "differentuser",
            "email": "test@example.com",  # Already exists
            "password": "password123"
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_login_success(client, test_user):
    """Test successful login"""
    response = client.post(
        "/api/auth/login",
        json={
            "username": "testuser",
            "password": "testpass123"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, test_user):
    """Test login with incorrect password"""
    response = client.post(
        "/api/auth/login",
        json={
            "username": "testuser",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_login_nonexistent_user(client):
    """Test login with non-existent user"""
    response = client.post(
        "/api/auth/login",
        json={
            "username": "nonexistent",
            "password": "password123"
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_current_user(client, auth_headers):
    """Test getting current user information"""
    response = client.get("/api/auth/me", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"


def test_get_current_user_unauthorized(client):
    """Test accessing protected endpoint without token"""
    response = client.get("/api/auth/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_current_user_invalid_token(client):
    """Test accessing protected endpoint with invalid token"""
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
```

#### File: `backend/app/tests/test_security.py`

```python
import pytest
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token
)
from datetime import timedelta


def test_password_hashing():
    """Test password hashing and verification"""
    password = "securepassword123"
    hashed = get_password_hash(password)

    assert hashed != password  # Should be hashed
    assert verify_password(password, hashed)  # Should verify correctly
    assert not verify_password("wrongpassword", hashed)  # Wrong password fails


def test_create_and_decode_token():
    """Test JWT token creation and decoding"""
    data = {"sub": "testuser"}
    token = create_access_token(data)

    assert token is not None
    assert isinstance(token, str)

    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "testuser"
    assert "exp" in decoded


def test_token_with_expiration():
    """Test token with custom expiration"""
    data = {"sub": "testuser"}
    expires_delta = timedelta(minutes=30)
    token = create_access_token(data, expires_delta=expires_delta)

    decoded = decode_access_token(token)
    assert decoded is not None


def test_invalid_token():
    """Test decoding an invalid token"""
    invalid_token = "this.is.invalid"
    decoded = decode_access_token(invalid_token)
    assert decoded is None
```

---

### Step 1.4: Docker Configuration

#### File: `backend/Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

#### File: `backend/.env.example`

```env
# Application
APP_NAME=CALIDUS API
DEBUG=true

# Database
DATABASE_URL=postgresql://calidus:calidus123@db:5432/calidus
TEST_DATABASE_URL=postgresql://calidus:calidus123@db:5432/calidus_test

# Redis
REDIS_URL=redis://redis:6379/0

# Security (CHANGE IN PRODUCTION!)
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# CORS
CORS_ORIGINS=["http://localhost:3000", "http://localhost:3001"]
```

#### File: `docker-compose.yml`

```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: calidus
      POSTGRES_PASSWORD: calidus123
      POSTGRES_DB: calidus
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U calidus"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://calidus:calidus123@db:5432/calidus
      - TEST_DATABASE_URL=postgresql://calidus:calidus123@db:5432/calidus_test
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - ./backend:/app
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

volumes:
  postgres_data:
```

---

### Step 1.5: Initialize Frontend with React + TypeScript

#### Commands to Run:

```bash
cd frontend
npx create-react-app . --template typescript
npm install axios react-router-dom @mui/material @emotion/react @emotion/styled
npm install --save-dev @testing-library/react @testing-library/jest-dom @testing-library/user-event
npm install --save-dev @types/react-router-dom
```

#### File: `frontend/src/services/api.ts`

```typescript
import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptor to inject auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );
  }

  async login(username: string, password: string) {
    const response = await this.client.post('/api/auth/login', {
      username,
      password,
    });
    const { access_token } = response.data;
    localStorage.setItem('access_token', access_token);
    return response.data;
  }

  async register(username: string, email: string, password: string) {
    const response = await this.client.post('/api/auth/register', {
      username,
      email,
      password,
    });
    return response.data;
  }

  async getCurrentUser() {
    const response = await this.client.get('/api/auth/me');
    return response.data;
  }

  logout() {
    localStorage.removeItem('access_token');
  }

  isAuthenticated(): boolean {
    return !!localStorage.getItem('access_token');
  }
}

export default new ApiService();
```

#### File: `frontend/src/services/api.test.ts`

```typescript
import ApiService from './api';

// Mock localStorage
const localStorageMock = (() => {
  let store: { [key: string]: string } = {};

  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => {
      store[key] = value.toString();
    },
    removeItem: (key: string) => {
      delete store[key];
    },
    clear: () => {
      store = {};
    },
  };
})();

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

describe('ApiService', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  test('isAuthenticated returns false when no token', () => {
    expect(ApiService.isAuthenticated()).toBe(false);
  });

  test('isAuthenticated returns true when token exists', () => {
    localStorage.setItem('access_token', 'fake-token');
    expect(ApiService.isAuthenticated()).toBe(true);
  });

  test('logout removes token from localStorage', () => {
    localStorage.setItem('access_token', 'fake-token');
    ApiService.logout();
    expect(localStorage.getItem('access_token')).toBeNull();
  });
});
```

#### File: `frontend/src/components/Auth/Login.tsx`

```typescript
import React, { useState } from 'react';
import {
  Box,
  Button,
  TextField,
  Typography,
  Paper,
  Alert,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import ApiService from '../../services/api';

const Login: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await ApiService.login(username, password);
      navigate('/dashboard');
    } catch (err: any) {
      setError(
        err.response?.data?.detail || 'Login failed. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box
      display="flex"
      justifyContent="center"
      alignItems="center"
      minHeight="100vh"
      bgcolor="#f5f5f5"
    >
      <Paper elevation={3} sx={{ p: 4, maxWidth: 400, width: '100%' }}>
        <Typography variant="h4" component="h1" gutterBottom align="center">
          CALIDUS
        </Typography>
        <Typography variant="subtitle1" gutterBottom align="center" color="textSecondary">
          AI-Powered Requirements Traceability
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {error}
          </Alert>
        )}

        <Box component="form" onSubmit={handleSubmit} sx={{ mt: 3 }}>
          <TextField
            fullWidth
            label="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            margin="normal"
            required
            autoFocus
            disabled={loading}
          />
          <TextField
            fullWidth
            label="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            margin="normal"
            required
            disabled={loading}
          />
          <Button
            type="submit"
            fullWidth
            variant="contained"
            sx={{ mt: 3, mb: 2 }}
            disabled={loading}
          >
            {loading ? 'Logging in...' : 'Login'}
          </Button>
        </Box>

        <Typography variant="body2" align="center" color="textSecondary" sx={{ mt: 2 }}>
          Demo Credentials: admin / demo2024
        </Typography>
      </Paper>
    </Box>
  );
};

export default Login;
```

#### File: `frontend/src/components/Auth/Login.test.tsx`

```typescript
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Login from './Login';

const MockLogin = () => (
  <BrowserRouter>
    <Login />
  </BrowserRouter>
);

describe('Login Component', () => {
  test('renders login form', () => {
    render(<MockLogin />);
    expect(screen.getByText(/CALIDUS/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Username/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Login/i })).toBeInTheDocument();
  });

  test('shows demo credentials', () => {
    render(<MockLogin />);
    expect(screen.getByText(/Demo Credentials: admin \/ demo2024/i)).toBeInTheDocument();
  });

  test('updates username field', () => {
    render(<MockLogin />);
    const usernameInput = screen.getByLabelText(/Username/i) as HTMLInputElement;
    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    expect(usernameInput.value).toBe('testuser');
  });

  test('updates password field', () => {
    render(<MockLogin />);
    const passwordInput = screen.getByLabelText(/Password/i) as HTMLInputElement;
    fireEvent.change(passwordInput, { target: { value: 'testpass' } });
    expect(passwordInput.value).toBe('testpass');
  });
});
```

#### File: `frontend/src/App.tsx`

```typescript
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './components/Auth/Login';
import ApiService from './services/api';

const Dashboard: React.FC = () => {
  return (
    <div>
      <h1>Dashboard (Coming Soon)</h1>
    </div>
  );
};

const ProtectedRoute: React.FC<{ children: React.ReactElement }> = ({ children }) => {
  return ApiService.isAuthenticated() ? children : <Navigate to="/login" />;
};

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route path="/" element={<Navigate to="/login" />} />
      </Routes>
    </Router>
  );
}

export default App;
```

#### File: `frontend/Dockerfile`

```dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy application code
COPY . .

# Expose port
EXPOSE 3000

# Start the app
CMD ["npm", "start"]
```

---

## Testing Checklist & Acceptance Criteria

### ✅ Week 1 Tests Must Pass:

#### Backend Tests
```bash
cd backend
pytest -v --cov=app --cov-report=term-missing
```

**Required Coverage**: ≥ 80%

**Test Results Expected**:
- ✅ `test_health_check` - PASSED
- ✅ `test_root_endpoint` - PASSED
- ✅ `test_register_user` - PASSED
- ✅ `test_register_duplicate_username` - PASSED
- ✅ `test_register_duplicate_email` - PASSED
- ✅ `test_login_success` - PASSED
- ✅ `test_login_wrong_password` - PASSED
- ✅ `test_login_nonexistent_user` - PASSED
- ✅ `test_get_current_user` - PASSED
- ✅ `test_get_current_user_unauthorized` - PASSED
- ✅ `test_get_current_user_invalid_token` - PASSED
- ✅ `test_password_hashing` - PASSED
- ✅ `test_create_and_decode_token` - PASSED
- ✅ `test_token_with_expiration` - PASSED
- ✅ `test_invalid_token` - PASSED

#### Frontend Tests
```bash
cd frontend
npm test -- --coverage
```

**Required Coverage**: ≥ 70%

**Test Results Expected**:
- ✅ `Login component renders` - PASSED
- ✅ `Login shows demo credentials` - PASSED
- ✅ `Username field updates` - PASSED
- ✅ `Password field updates` - PASSED
- ✅ `ApiService.isAuthenticated` - PASSED
- ✅ `ApiService.logout` - PASSED

#### Integration Tests
```bash
docker-compose up -d
# Wait for services to be healthy
curl http://localhost:8000/health
# Should return: {"status":"healthy"}

curl http://localhost:3000
# Should load login page
```

#### Docker Tests
```bash
docker-compose up -d
docker-compose ps
# All services should be "healthy" or "running"

docker-compose logs backend | grep "Application startup complete"
# Should show successful startup
```

---

## Implementation Commands

### Step-by-Step Execution:

#### 1. Create Backend Structure
```bash
cd /Users/z/Documents/CALIDUS
mkdir -p backend/app/{api,core,models,schemas,tests}
touch backend/app/__init__.py
touch backend/app/{main.py,config.py,database.py}
touch backend/app/core/{__init__.py,security.py,dependencies.py}
touch backend/app/models/{__init__.py,user.py}
touch backend/app/schemas/{__init__.py,user.py}
touch backend/app/api/{__init__.py,auth.py}
touch backend/app/tests/{__init__.py,conftest.py,test_auth.py,test_security.py}
touch backend/{requirements.txt,requirements-dev.txt,pytest.ini,Dockerfile,.env.example}
```

#### 2. Create Frontend Structure
```bash
cd /Users/z/Documents/CALIDUS
npx create-react-app frontend --template typescript
cd frontend
mkdir -p src/{components/Auth,services,utils,types}
```

#### 3. Build and Test
```bash
# Start services
docker-compose up -d

# Run backend tests
docker-compose exec backend pytest -v --cov=app

# Run frontend tests
cd frontend
npm test -- --coverage --watchAll=false

# Check services health
curl http://localhost:8000/health
curl http://localhost:3000
```

---

## Week 1 Deliverables

### Documentation
- [ ] README.md with setup instructions
- [ ] API documentation (auto-generated by FastAPI)
- [ ] Test coverage reports (HTML)

### Code
- [ ] Backend API with authentication
- [ ] Frontend login page
- [ ] Docker configuration
- [ ] CI/CD pipeline (GitHub Actions)

### Tests
- [ ] Backend: 15+ test cases, ≥80% coverage
- [ ] Frontend: 6+ test cases, ≥70% coverage
- [ ] Integration: Services communicate successfully

### Deployment
- [ ] Local Docker environment running
- [ ] All services healthy
- [ ] Can register user via API
- [ ] Can login via frontend
- [ ] JWT authentication working

---

## Success Metrics

**Week 1 is COMPLETE when**:
1. ✅ All backend tests pass (pytest)
2. ✅ All frontend tests pass (jest)
3. ✅ Docker services start without errors
4. ✅ Can create user via API: `curl -X POST http://localhost:8000/api/auth/register -H "Content-Type: application/json" -d '{"username":"demo","email":"demo@example.com","password":"demo123"}'`
5. ✅ Can login via API and receive JWT token
6. ✅ Frontend loads and displays login form
7. ✅ Code coverage meets thresholds (≥80% backend, ≥70% frontend)
8. ✅ GitHub Actions CI passes (if configured)

---

## Next Week Preview

**Week 2: Core Backend Features**
- Requirements CRUD operations (with tests)
- Test cases CRUD operations (with tests)
- Traceability link management (with tests)
- Database migrations (Alembic)
- Sample data generation scripts (with validation tests)

**Testing Requirements for Week 2**:
- All new endpoints: 100% test coverage
- Database operations: Transaction rollback tests
- API integration tests: Full CRUD workflows
- Performance tests: Response time < 200ms

---

## Questions Before We Start?

Before I proceed with creating all the files, please confirm:

1. **Tech Stack Approval**: FastAPI backend + React/TypeScript frontend + PostgreSQL + Docker?
2. **Testing Standards**: 80% backend coverage, 70% frontend coverage acceptable?
3. **Timeline**: Is Week 1 (Days 1-5) timeline realistic for your team?
4. **Access**: Do you have permissions to create files in `/Users/z/Documents/CALIDUS/`?

Ready to proceed with file creation?
