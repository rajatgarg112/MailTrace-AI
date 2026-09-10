"""
PlaceMate AI Security Package Exports
"""

from security.core.security.config import security_config, SecurityConfig
from security.core.security.password import PasswordSecurity
from security.core.security.auth import JWTAuth, StudentTokenPayload
from security.core.security.authorization import (
    get_current_student,
    verify_student_ownership,
)
from security.core.security.validation import (
    InputSanitizer,
    StudentRegisterRequest,
    StudentLoginRequest,
    CompanyApplicationRequest,
    CodingProgressSubmission,
)
from security.core.security.logging import SecurityLogger
from security.core.security.middleware import setup_security_middleware

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
