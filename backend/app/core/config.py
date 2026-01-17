"""
Application configuration management using Pydantic Settings.
Loads configuration from environment variables with validation.
"""

from typing import Literal
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration with environment-based overrides."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_parse_none_str="null"
    )
    
    # Database Configuration
    database_url: str = Field(
        default="postgresql://ekyc_user:password@localhost:5432/ekyc_db",
        description="Database connection string (PostgreSQL or SQLite)"
    )
    
    # Redis Configuration
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection string for caching and rate limiting"
    )
    
    # Security Configuration
    jwt_secret: str = Field(
        min_length=32,
        description="Secret key for JWT token signing (minimum 32 characters)"
    )
    jwt_algorithm: str = Field(default="HS256", description="JWT signing algorithm")
    jwt_expiry_hours: int = Field(default=24, ge=1, le=168, description="JWT token expiry in hours")
    
    # Verification Provider Configuration
    verification_provider: Literal["mock", "verifyme"] = Field(
        default="mock",
        description="Verification provider to use (mock for testing, verifyme for production)"
    )
    verifyme_base_url: str = Field(
        default="https://api.verifyme.ng/v1",
        description="VerifyMe.ng API base URL"
    )
    verifyme_test_secret: str = Field(
        default="",
        description="VerifyMe.ng test secret key"
    )
    verifyme_live_secret: str = Field(
        default="",
        description="VerifyMe.ng live secret key"
    )
    use_test_keys: bool = Field(
        default=True,
        description="Use test keys instead of live keys for VerifyMe.ng"
    )
    
    # Provider Resilience Configuration
    provider_timeout_seconds: int = Field(
        default=10,
        ge=1,
        le=30,
        description="Timeout for provider API calls in seconds"
    )
    provider_max_retries: int = Field(
        default=3,
        ge=0,
        le=5,
        description="Maximum retry attempts for failed provider calls"
    )
    provider_circuit_breaker_threshold: int = Field(
        default=5,
        ge=1,
        description="Number of consecutive failures before circuit breaker opens"
    )
    provider_circuit_breaker_timeout: int = Field(
        default=60,
        ge=10,
        description="Seconds to wait before retrying after circuit breaker opens"
    )
    
    # API Configuration
    api_rate_limit_per_minute: int = Field(
        default=100,
        ge=1,
        description="Rate limit per client per minute"
    )
    api_request_timeout_seconds: int = Field(
        default=25,
        ge=5,
        description="Maximum time for complete API request processing"
    )
    allowed_origins_str: str = Field(
        default="http://localhost:3000,http://localhost:5173",
        validation_alias="allowed_origins",
        description="Comma-separated list of allowed CORS origins"
    )
    
    # Application Configuration
    environment: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Application environment"
    )
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level"
    )
    debug: bool = Field(
        default=False,
        description="Enable debug mode (disable in production)"
    )
    
    # Storage Configuration
    reports_storage_path: str = Field(
        default="./storage/reports",
        description="Local filesystem path for storing verification reports"
    )
    reports_retention_days: int = Field(
        default=30,
        ge=1,
        description="Number of days to retain reports before cleanup"
    )
    
    @property
    def allowed_origins(self) -> list[str]:
        """Parse and return allowed origins as a list."""
        if isinstance(self.allowed_origins_str, str):
            return [origin.strip() for origin in self.allowed_origins_str.split(",") if origin.strip()]
        return []
    
    @property
    def verifyme_secret(self) -> str:
        """Return the appropriate VerifyMe.ng secret based on environment."""
        return self.verifyme_test_secret if self.use_test_keys else self.verifyme_live_secret
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == "development"


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get global settings instance."""
    return settings
