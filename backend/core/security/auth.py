"""
PlaceMate AI — Authentication Foundation & JWT Token Engine

Handles student session token generation, cryptographically signed JWT validation,
token verification, and token payload parsing using HMAC-SHA256.
Supports stateless student registration and login verification.
"""

from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, timezone
import base64
import hashlib
import hmac
import json
from typing import Optional, Dict, Any

from backend.core.security.config import security_config
from backend.core.security.password import PasswordSecurity


@dataclass
class StudentTokenPayload:
    student_id: str
    email: str
    name: str
    role: str = "student"
    exp: Optional[int] = None
    iat: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class JWTAuth:
    """HMAC-SHA256 Token Authentication Engine"""

    @classmethod
    def _b64_encode(cls, data: bytes) -> str:
        return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")

    @classmethod
    def _b64_decode(cls, data_str: str) -> bytes:
        padding = "=" * (4 - (len(data_str) % 4))
        return base64.urlsafe_b64decode((data_str + padding).encode("utf-8"))

    @classmethod
    def create_access_token(
        cls,
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        """Creates cryptographically signed JWT access token."""
        now = datetime.now(timezone.utc)
        if expires_delta:
            expire = now + expires_delta
        else:
            expire = now + timedelta(minutes=security_config.ACCESS_TOKEN_EXPIRE_MINUTES)

        payload = data.copy()
        payload["iat"] = int(now.timestamp())
        payload["exp"] = int(expire.timestamp())

        header = {"alg": "HS256", "typ": "JWT"}

        header_b64 = cls._b64_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
        payload_b64 = cls._b64_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))

        signature_input = f"{header_b64}.{payload_b64}".encode("utf-8")
        signature = hmac.new(
            security_config.SECRET_KEY.encode("utf-8"),
            signature_input,
            hashlib.sha256,
        ).digest()

        signature_b64 = cls._b64_encode(signature)
        return f"{header_b64}.{payload_b64}.{signature_b64}"

    @classmethod
    def verify_access_token(cls, token: str) -> Optional[Dict[str, Any]]:
        """Verifies JWT signature and checks token expiration."""
        if not token or token.count(".") != 2:
            return None

        try:
            header_b64, payload_b64, signature_b64 = token.split(".")

            # Verify cryptographic signature using constant-time comparison
            signature_input = f"{header_b64}.{payload_b64}".encode("utf-8")
            expected_signature = hmac.new(
                security_config.SECRET_KEY.encode("utf-8"),
                signature_input,
                hashlib.sha256,
            ).digest()

            actual_signature = cls._b64_decode(signature_b64)
            if not hmac.compare_digest(actual_signature, expected_signature):
                return None

            # Parse payload
            payload_bytes = cls._b64_decode(payload_b64)
            payload = json.loads(payload_bytes.decode("utf-8"))

            # Check expiration
            exp = payload.get("exp")
            if exp:
                now_ts = int(datetime.now(timezone.utc).timestamp())
                if now_ts > exp:
                    return None  # Token expired

            return payload
        except Exception:
            return None
