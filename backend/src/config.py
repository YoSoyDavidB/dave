from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App
    app_name: str = "Dave"
    debug: bool = False

    # API
    api_prefix: str = "/api/v1"

    # OpenRouter
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    default_model: str = "anthropic/claude-sonnet-4.5"

    # GitHub (for Obsidian vault)
    github_token: str = ""
    github_repo: str = ""  # format: "username/repo"
    vault_path_prefix: str = "David's Notes"  # root folder in repo

    # Database
    database_url: str = "postgresql+asyncpg://localhost:5432/dave"

    # JWT
    jwt_secret_key: str = "super-secret-jwt-key-please-change"
    # IMPORTANT: Change this in production!
    jwt_algorithm: str = "HS256"

    # Registration (for private registration endpoint)
    registration_secret: str = "change-this-registration-secret-in-production"

    # Redis
    redis_url: str = "redis://localhost:6379"

    # Qdrant
    qdrant_url: str = "http://localhost:6333"

    # Neo4j
    neo4j_url: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
