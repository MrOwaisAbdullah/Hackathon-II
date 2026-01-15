"""Application configuration."""
import os
from typing import List
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

    # CORS - Support comma-separated string for HuggingFace Spaces
    frontend_url: str = Field(
        default="http://localhost:3000,http://localhost:8000",
        description="Comma-separated list of allowed frontend URLs for CORS",
    )

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

    # Phase 3 AI Services (T003)
    openai_api_key: str = Field(
        default="",
        description="OpenAI API key for GPT models (fallback when OpenRouter rate limited)",
    )
    gemini_api_key: str = Field(
        default="",
        description="Gemini API key for AI model access",
    )
    openrouter_api_key: str = Field(
        default="",
        description="OpenRouter API key for embeddings and AI models",
    )
    mcp_server_url: str = Field(
        default="http://127.0.0.1:8000/mcp",
        description="MCP server URL (now mounted on main API at /mcp endpoint)",
    )
    qdrant_url: str = Field(
        default="http://localhost:6333",
        description="Qdrant Cloud URL",
    )
    qdrant_api_key: str = Field(
        default="",
        description="Qdrant Cloud API key",
    )
    log_level: str = Field(
        default="info",
        description="Logging level (debug, info, warning, error)",
    )

    # Better Auth JWT validation (C1 - Specification Analysis Finding)
    better_auth_public_key: str = Field(
        default="",
        description="Better Auth JWT public key for token validation (RS256)",
    )
    better_auth_issuer: str = Field(
        default="https://auth.teamflow.com",
        description="Better Auth JWT issuer URL",
    )
    better_auth_audience: List[str] = Field(
        default=["teamflow-api"],
        description="Valid JWT audience values",
    )

    @property
    def cors_origins(self) -> List[str]:
        """Parse frontend_url into a list of CORS origins."""
        # Check if we're in HuggingFace Spaces
        is_hf_spaces = os.getenv("SPACE_ID") is not None or os.getenv("HUGGINGFACE_SPACE_ID") is not None

        if isinstance(self.frontend_url, str):
            origins = [url.strip() for url in self.frontend_url.split(",")]
        else:
            origins = list(self.frontend_url)

        # Add common HuggingFace and Vercel domains in production
        if self.environment == "production" or is_hf_spaces:
            # Allow all vercel.app domains (for preview deployments)
            if not any("vercel.app" in origin for origin in origins):
                origins.append("https://*.vercel.app")

            # Allow huggingface.co domains
            if not any("huggingface.co" in origin for origin in origins):
                origins.append("https://huggingface.co")

        return origins

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Ensure database_url is a valid PostgreSQL connection string."""
        if not v.startswith("postgresql://") and not v.startswith("postgresql+"):
            raise ValueError("Database URL must use postgresql:// scheme (Neon PostgreSQL)")
        return v

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Ensure secret_key is strong enough."""
        if len(v) < 32 and cls.environment != "development":
            raise ValueError("SECRET_KEY must be at least 32 characters in production")
        return v

    @field_validator("mcp_server_url")
    @classmethod
    def validate_mcp_server_url(cls, v: str, info) -> str:
        """Warn if using localhost in production - MCP won't work for agents."""
        environment = info.data.get("environment", "development")
        if environment == "production" and ("127.0.0.1" in v or "localhost" in v):
            import warnings
            warnings.warn(
                "MCP_SERVER_URL points to localhost in production. "
                "Agents will NOT be able to connect to MCP tools. "
                "Set MCP_SERVER_URL to your deployed backend URL (e.g., "
                "https://your-space.hf.space/mcp for HuggingFace Spaces)."
            )
        return v

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
