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
