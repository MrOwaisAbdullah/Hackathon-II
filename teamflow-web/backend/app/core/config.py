"""Application configuration."""
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Database
    database_url: str = Field(
        default="postgresql://user:pass@localhost:5432/teamflow",
        description="Neon PostgreSQL connection URL",
    )

    # API
    api_v1_prefix: str = "/api/v1"

    # CORS
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]

    # JWT
    secret_key: str = Field(
        default="your-secret-key-change-in-production",
        description="JWT secret key",
    )

    # Environment
    environment: str = Field(
        default="development",
        description="Environment (development, staging, production)",
    )

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Ensure database_url is a valid PostgreSQL connection string."""
        if not v.startswith("postgresql://") and not v.startswith("postgresql+"):
            raise ValueError("Database URL must use postgresql:// scheme (Neon PostgreSQL)")
        return v

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
