"""
shared/contracts/email_event.py
─────────────────────────────────────────────────────────────────────────────
Email Event Contract — lifecycle event structure.

Every status transition that an email undergoes MUST emit an EmailEventContract.
These events are immutable audit records used for:
    • Database event log  (database/app/models/email_event.py)
    • Frontend timeline   (Member 1 — email detail forensic tab)
    • Security auditing   (Member 4 — evidence preservation)
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, ConfigDict

from shared.enums.email_status import EmailStatus


class EmailEventContract(BaseModel):
    """
    Immutable record of a single lifecycle event in an email's journey.

    Events are append-only — never mutated after creation.
    """

    # ── Identity ──────────────────────────────────────────────────────────
    emailId: str = Field(
        ...,
        description="UUID of the email this event belongs to.",
    )

    # ── Transition ────────────────────────────────────────────────────────
    event: EmailStatus = Field(
        ...,
        description=(
            "The new status this event represents. "
            "Follows the EmailStatus lifecycle enum."
        ),
    )
    fromStatus: Optional[EmailStatus] = Field(
        default=None,
        description="Previous status before this transition (None for initial RECEIVED event).",
    )

    # ── Timing ────────────────────────────────────────────────────────────
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp at which this event occurred.",
    )

    # ── Payload ───────────────────────────────────────────────────────────
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description=(
            "Optional JSON-serialisable dict with event-specific context, "
            "e.g. {'trigger': 'SPF_FAIL', 'module': 'security_policy'}."
        ),
    )

    model_config = ConfigDict(from_attributes=True)
