"""
PlaceMate AI Security Configuration Module

Loads security parameters, JWT secrets, CORS settings, and environment variables.
Prevents hardcoding of sensitive credentials and keys in source code.
"""

from dataclasses import dataclass
import os
import secrets
from typing import List


@dataclass
class SecurityConfig:
    """Security environment and configuration management."""

    # Secret Key for JWT token signing & HMAC operations
    SECRET_KEY: str = os.getenv(
        "PLACEMATE_SECRET_KEY",
        "placemate_dev_secret_key_change_in_production_9f8e7d6c5b4a321",
    )
    
    # Token signing algorithm
    ALGORITHM: str = "HS256"
    
    # Token expiration in minutes
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("PLACEMATE_TOKEN_EXPIRE_MINUTES", "60")
    )
    
    # Password policy parameters
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_REQUIRE_UPPERCASE: bool = True
    PASSWORD_REQUIRE_NUMBER: bool = True
    
    # Environment mode
    ENVIRONMENT: str = os.getenv("PLACEMATE_ENV", "development").lower()
    
    # CORS Allowed Origins
    @property
    def ALLOWED_ORIGINS(self) -> List[str]:
        raw_origins = os.getenv(
            "PLACEMATE_ALLOWED_ORIGINS",
            "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173,http://localhost:8000",
        )
        return [origin.strip() for origin in raw_origins.split(",") if origin.strip()]

    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    def validate_config(self) -> List[str]:
        """Validates security settings for production readiness."""
        warnings = []
        if self.is_production():
            if "placemate_dev_secret_key" in self.SECRET_KEY:
                warnings.append("CRITICAL: Default dev SECRET_KEY is active in production mode!")
            if len(self.SECRET_KEY) < 32:
                warnings.append("WARNING: SECRET_KEY should be at least 32 characters long.")
        return warnings


# Global security configuration instance
security_config = SecurityConfig()
