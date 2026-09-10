"""
PlaceMate AI — Password Security Module

Provides secure password hashing, salt generation, constant-time verification,
and password complexity validation using OWASP-recommended PBKDF2-HMAC-SHA256.
Guarantees zero plaintext password storage and prevents timing side-channel attacks.
"""

import hashlib
import hmac
import os
import re
import secrets
from typing import Tuple, Optional
from backend.core.security.config import security_config


class PasswordSecurity:
    """Secure Password Hashing and Validation Engine"""

    ITERATIONS = 600_000  # OWASP 2026 baseline recommendation for PBKDF2-HMAC-SHA256
    SALT_SIZE = 16  # 128-bit cryptographically secure salt

    @classmethod
    def hash_password(cls, password: str) -> str:
        """Hashes plain text password with cryptographically secure random salt."""
        if not password:
            raise ValueError("Password cannot be empty")

        salt = secrets.token_bytes(cls.SALT_SIZE)
        hash_bytes = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            cls.ITERATIONS,
        )

        salt_hex = salt.hex()
        hash_hex = hash_bytes.hex()
        return f"pbkdf2:sha256:{cls.ITERATIONS}${salt_hex}${hash_hex}"

    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        """Verifies plain password against stored hash using constant-time comparison."""
        if not plain_password or not hashed_password:
            return False

        try:
            algorithm_info, salt_hex, expected_hash_hex = hashed_password.split("$")
            _, hash_name, iterations_str = algorithm_info.split(":")
            iterations = int(iterations_str)

            salt = bytes.fromhex(salt_hex)
            expected_hash = bytes.fromhex(expected_hash_hex)

            computed_hash = hashlib.pbkdf2_hmac(
                hash_name,
                plain_password.encode("utf-8"),
                salt,
                iterations,
            )

            # Constant-time comparison to prevent timing attacks
            return hmac.compare_digest(computed_hash, expected_hash)
        except Exception:
            return False

    @classmethod
    def validate_password_strength(cls, password: str) -> Tuple[bool, Optional[str]]:
        """Checks if password satisfies security complexity policy."""
        if len(password) < security_config.PASSWORD_MIN_LENGTH:
            return False, f"Password must be at least {security_config.PASSWORD_MIN_LENGTH} characters long."

        if security_config.PASSWORD_REQUIRE_UPPERCASE and not re.search(r"[A-Z]", password):
            return False, "Password must contain at least one uppercase letter (A-Z)."

        if security_config.PASSWORD_REQUIRE_NUMBER and not re.search(r"[0-9]", password):
            return False, "Password must contain at least one numeric digit (0-9)."

        return True, None
