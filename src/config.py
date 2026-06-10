"""Application configuration management."""

import os
from enum import Enum


class Environment(str, Enum):
    """Application environments."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class Config:
    """Base configuration."""
    
    # Application
    APP_NAME = "AHMS Backend"
    APP_VERSION = "0.1.0"
    ENVIRONMENT = os.getenv("ENVIRONMENT", Environment.DEVELOPMENT)
    DEBUG = ENVIRONMENT in [Environment.DEVELOPMENT, Environment.TESTING]
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Database
    DATABASE_DIR = os.getenv("DATABASE_DIR", ".")
    DATABASE_URL = f"sqlite:///{os.path.join(DATABASE_DIR, 'ahms.db')}"
    SQL_ECHO = os.getenv("SQL_ECHO", "false").lower() == "true"
    
    # API
    API_TITLE = "AHMS Backend"
    API_VERSION = "0.1.0"
    API_PREFIX = "/api"
    
    # CORS
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
    
    # Telemetry
    TELEMETRY_RETENTION_DAYS = int(os.getenv("TELEMETRY_RETENTION_DAYS", "90"))
    
    # Reasoning Engine
    REASONING_CONFIDENCE_THRESHOLD = float(os.getenv("REASONING_CONFIDENCE_THRESHOLD", "0.7"))
    HEALTH_SCORE_WARNING_THRESHOLD = float(os.getenv("HEALTH_SCORE_WARNING_THRESHOLD", "0.5"))
    HEALTH_SCORE_CRITICAL_THRESHOLD = float(os.getenv("HEALTH_SCORE_CRITICAL_THRESHOLD", "0.2"))
    
    # CI Evaluation
    CI_PASS_THRESHOLD = float(os.getenv("CI_PASS_THRESHOLD", "0.8"))
    CI_WARN_THRESHOLD = float(os.getenv("CI_WARN_THRESHOLD", "0.5"))
    
    # Governance
    REQUIRE_ACTION_APPROVAL = os.getenv("REQUIRE_ACTION_APPROVAL", "true").lower() == "true"
    ENABLE_AUDIT_LOGGING = os.getenv("ENABLE_AUDIT_LOGGING", "true").lower() == "true"


class DevelopmentConfig(Config):
    """Development configuration."""
    ENVIRONMENT = Environment.DEVELOPMENT
    DEBUG = True
    SQL_ECHO = True
    CORS_ORIGINS = ["*"]


class StagingConfig(Config):
    """Staging configuration."""
    ENVIRONMENT = Environment.STAGING
    DEBUG = False
    SQL_ECHO = False
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "").split(",")


class ProductionConfig(Config):
    """Production configuration."""
    ENVIRONMENT = Environment.PRODUCTION
    DEBUG = False
    SQL_ECHO = False
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "").split(",")
    REQUIRE_ACTION_APPROVAL = True


class TestingConfig(Config):
    """Testing configuration."""
    ENVIRONMENT = Environment.TESTING
    DEBUG = True
    DATABASE_URL = "sqlite:///:memory:"
    SQL_ECHO = False


def get_config() -> Config:
    """Get appropriate configuration based on environment."""
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    if env == "production":
        return ProductionConfig()
    elif env == "staging":
        return StagingConfig()
    elif env == "testing":
        return TestingConfig()
    else:
        return DevelopmentConfig()


# Global config instance
config = get_config()
