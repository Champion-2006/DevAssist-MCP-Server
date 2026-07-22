"""
Configuration module for DevAssist MCP Server.

Loads settings from environment variables and .env file
using pydantic-settings for validation.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # GitHub Configuration
    github_token: str | None = None
    github_api_base_url: str = "https://api.github.com"

    # Codeforces Configuration
    codeforces_api_base_url: str = "https://codeforces.com/api"

    # Logging Configuration
    log_level: str = "INFO"
    log_file: str = "logs/devassist.log"

    # Server Configuration
    server_name: str = "devassist-mcp"
    server_version: str = "1.0.0"
    transport: str = "stdio"
    port: int = 8000

    # HTTP Client Configuration
    http_timeout: int = 30
    max_retries: int = 3

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


# Singleton settings instance
settings = Settings()
