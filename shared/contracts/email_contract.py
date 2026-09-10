"""
shared/contracts/email_contract.py
─────────────────────────────────────────────────────────────────────────────
Shared Email Object Contract — Pydantic v2 model.

This is the canonical representation of an email as it flows through the
MailTrace AI pipeline.  All modules — Backend (Member 2), Database
(Member 3), Security Engine (Member 4), ML Engine (Member 5) — MUST
conform to this schema when exchanging email data.

NOTE: This is a data-transfer contract, not a database ORM model.
      Database ORM models live in database/app/models/.
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

from shared.enums.email_status import EmailStatus, DEFAULT_EMAIL_STATUS


class AttachmentContract(BaseModel):
    """Represents a single email attachment."""

    filename: str
    content_type: str = "application/octet-stream"
    size_bytes: Optional[int] = None
    sha256: Optional[str] = None
    is_suspicious: bool = False

    model_config = ConfigDict(from_attributes=True)


class EmailContract(BaseModel):
    """
    Shared canonical Email object.

    Used as the integration boundary between:
        • Backend API responses       → Frontend consumption
        • Security Engine input       → risk scoring
        • ML Engine input             → classification
        • Risk Engine composition     → final decision
    """

    # ── Identity ──────────────────────────────────────────────────────────
    id: str = Field(..., description="UUID of the email record.")
    message_id: Optional[str] = Field(
        default=None,
        description="RFC-2822 Message-ID header value, if present.",
    )

    # ── Addressing ────────────────────────────────────────────────────────
    sender: str = Field(..., description="Display name of the sender.")
    senderEmail: str = Field(..., description="Sender's email address.")
    recipient: str = Field(..., description="Primary recipient email address.")

    # ── Content ───────────────────────────────────────────────────────────
    subject: Optional[str] = Field(default=None, description="Email subject line.")
    body: Optional[str] = Field(default=None, description="Plain-text body content.")

    # ── Metadata ──────────────────────────────────────────────────────────
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Time the email was received by the MailTrace gateway (UTC).",
    )
    attachments: List[AttachmentContract] = Field(
        default_factory=list,
        description="List of attachments associated with the email.",
    )

    # ── Security / Risk ───────────────────────────────────────────────────
    status: EmailStatus = Field(
        default=DEFAULT_EMAIL_STATUS,
        description="Current lifecycle status of the email.",
    )
    riskScore: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Composite risk score (0.0 = clean, 100.0 = definitively malicious).",
    )
    securityReasons: List[str] = Field(
        default_factory=list,
        description="Human-readable list of security signals that influenced the risk score.",
    )

    model_config = ConfigDict(from_attributes=True)
