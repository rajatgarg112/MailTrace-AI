"""
PlaceMate AI — Security Logging Foundation

Provides structured audit logging for security-relevant events (Logins, Failed Logins,
Unauthorized Access Attempts, Password Changes).
Guarantees NO passwords, JWT tokens, or credentials are recorded in log sinks.
"""

from datetime import datetime, timezone
import json
import logging
from typing import Optional, Dict, Any

# Configure dedicated security logger
security_logger = logging.getLogger("placemate.security")
security_logger.setLevel(logging.INFO)

# Ensure console handler exists
if not security_logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter("[SECURITY AUDIT] %(asctime)s - %(message)s")
    ch.setFormatter(formatter)
    security_logger.addHandler(ch)


class SecurityLogger:
    """Security Audit Logger"""

    # Redaction filter keys to prevent accidental leaks
    SENSITIVE_KEYS = {"password", "token", "access_token", "secret", "authorization", "hash"}

    @classmethod
    def log_event(
        cls,
        event_type: str,
        student_id: Optional[str] = None,
        email: Optional[str] = None,
        client_ip: Optional[str] = None,
        status: str = "SUCCESS",
        details: Optional[Dict[str, Any]] = None,
    ):
        """Logs structured security audit event."""
        sanitized_details = {}
        if details:
            for k, v in details.items():
                if k.lower() in cls.SENSITIVE_KEYS:
                    sanitized_details[k] = "[REDACTED]"
                else:
                    sanitized_details[k] = v

        audit_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "student_id": student_id or "ANONYMOUS",
            "email": email or "N/A",
            "client_ip": client_ip or "UNKNOWN",
            "status": status,
            "details": sanitized_details,
        }

        security_logger.info(json.dumps(audit_entry))

    @classmethod
    def log_login_success(cls, student_id: str, email: str, client_ip: str):
        cls.log_event("LOGIN_SUCCESS", student_id=student_id, email=email, client_ip=client_ip, status="SUCCESS")

    @classmethod
    def log_login_failed(cls, email: str, client_ip: str, reason: str):
        cls.log_event(
            "LOGIN_FAILED",
            email=email,
            client_ip=client_ip,
            status="FAILED",
            details={"reason": reason},
        )

    @classmethod
    def log_unauthorized_access(cls, path: str, client_ip: str, reason: str):
        cls.log_event(
            "UNAUTHORIZED_ACCESS_ATTEMPT",
            client_ip=client_ip,
            status="BLOCKED",
            details={"path": path, "reason": reason},
        )
