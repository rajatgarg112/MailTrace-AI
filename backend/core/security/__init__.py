"""
PlaceMate AI Security Package Exports
"""

from backend.core.security.config import security_config, SecurityConfig
from backend.core.security.password import PasswordSecurity
from backend.core.security.auth import JWTAuth, StudentTokenPayload
from backend.core.security.authorization import (
    get_current_student,
    verify_student_ownership,
)
from backend.core.security.validation import (
    InputSanitizer,
    StudentRegisterRequest,
    StudentLoginRequest,
    CompanyApplicationRequest,
    CodingProgressSubmission,
)
from backend.core.security.logging import SecurityLogger
from backend.core.security.middleware import setup_security_middleware

__all__ = [
    "security_config",
    "SecurityConfig",
    "PasswordSecurity",
    "JWTAuth",
    "StudentTokenPayload",
    "get_current_student",
    "verify_student_ownership",
    "InputSanitizer",
    "StudentRegisterRequest",
    "StudentLoginRequest",
    "CompanyApplicationRequest",
    "CodingProgressSubmission",
    "SecurityLogger",
    "setup_security_middleware",
]
