"""
shared/enums/email_status.py
─────────────────────────────────────────────────────────────────────────────
SINGLE SOURCE OF TRUTH for Email Lifecycle Status across the entire
MailTrace AI project.

Usage (Python modules — backend, database, security, ml):
    from shared.enums.email_status import EmailStatus

Usage (TypeScript/JS — frontend via shared/types/emailStatus.ts):
    import { EmailStatus } from '../shared/types/emailStatus';

IMPORTANT:
  Do NOT redefine EmailStatus in backend/app/schemas/enums.py or anywhere else.
  All modules MUST import from this file.
─────────────────────────────────────────────────────────────────────────────
"""

from enum import Enum
from typing import List


class EmailStatus(str, Enum):
    """
    Canonical enum representing every supported email lifecycle state.

    Lifecycle order:
        RECEIVED → SCANNING → DECISION → DELIVERED | WARNING | QUARANTINED | REJECTED | FAILED
        UNKNOWN is a safe fallback for unrecognised states.
    """

    # ── Ingestion ──────────────────────────────────────────────────────────
    RECEIVED = "RECEIVED"
    """Email has arrived at the MailTrace gateway and is queued."""

    # ── Analysis ──────────────────────────────────────────────────────────
    SCANNING = "SCANNING"
    """Security & ML pipeline is actively processing this email."""

    DECISION = "DECISION"
    """Risk engine is computing the final delivery decision."""

    # ── Terminal States ───────────────────────────────────────────────────
    DELIVERED = "DELIVERED"
    """Email passed all checks and has been placed in the inbox."""

    WARNING = "WARNING"
    """Email is suspicious; delivered with a visible security warning badge."""

    QUARANTINED = "QUARANTINED"
    """Email is held in the quarantine store pending review."""

    REJECTED = "REJECTED"
    """Email was definitively refused (e.g. confirmed malicious)."""

    FAILED = "FAILED"
    """Processing encountered an unrecoverable internal error."""

    # ── Fallback ──────────────────────────────────────────────────────────
    UNKNOWN = "UNKNOWN"
    """Unknown or uninitialised state — use as a safe default only."""

    # ── Helpers ────────────────────────────────────────────────────────────
    @classmethod
    def list_values(cls) -> List[str]:
        """Return list of all string values."""
        return [s.value for s in cls]

    @classmethod
    def is_valid(cls, value: str) -> bool:
        """Return True if *value* is a valid EmailStatus string."""
        return value in cls._value2member_map_

    @classmethod
    def terminal_states(cls) -> List["EmailStatus"]:
        """Return the set of states from which no further transitions occur."""
        return [cls.DELIVERED, cls.WARNING, cls.QUARANTINED, cls.REJECTED, cls.FAILED]

    @classmethod
    def active_states(cls) -> List["EmailStatus"]:
        """Return the states representing in-flight processing."""
        return [cls.RECEIVED, cls.SCANNING, cls.DECISION]


# Convenience alias used by database models
DEFAULT_EMAIL_STATUS: EmailStatus = EmailStatus.RECEIVED
