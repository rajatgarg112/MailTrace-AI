"""
shared/constants/pipeline.py
─────────────────────────────────────────────────────────────────────────────
Pipeline-wide constants shared across all MailTrace AI modules.

These values are used consistently in:
    • Risk Engine scoring thresholds
    • Security Policy Engine
    • ML confidence thresholds
    • API response metadata
─────────────────────────────────────────────────────────────────────────────
"""

# ── Risk Score Boundaries ─────────────────────────────────────────────────
RISK_SCORE_MIN: float = 0.0
"""Minimum possible risk score (completely clean email)."""

RISK_SCORE_MAX: float = 100.0
"""Maximum possible risk score (definitively malicious email)."""

# ── Delivery Decision Thresholds ──────────────────────────────────────────
RISK_THRESHOLD_WARNING: float = 25.0
"""Emails with risk score >= this value get a WARNING badge."""

RISK_THRESHOLD_QUARANTINE: float = 55.0
"""Emails with risk score >= this value are QUARANTINED."""

RISK_THRESHOLD_REJECT: float = 90.0
"""Emails with risk score >= this value are REJECTED outright."""

# ── ML Confidence Thresholds ──────────────────────────────────────────────
ML_CONFIDENCE_HIGH: float = 0.85
"""ML confidence >= this means high-certainty prediction."""

ML_CONFIDENCE_LOW: float = 0.40
"""ML confidence < this triggers a fallback / unknown verdict."""

# ── Email Processing ──────────────────────────────────────────────────────
MAX_ATTACHMENT_SIZE_MB: int = 25
"""Maximum attachment size accepted by the MailTrace gateway."""

MAX_RECIPIENTS_PER_EMAIL: int = 50
"""Maximum number of recipients supported per email."""

# ── Module Source Tags ────────────────────────────────────────────────────
SOURCE_SECURITY: str = "security"
"""Signal source tag for Security Engine outputs."""

SOURCE_ML: str = "ml"
"""Signal source tag for ML Engine outputs."""

SOURCE_RISK: str = "risk_engine"
"""Signal source tag for Risk Engine outputs."""

# ── Phase Flags ───────────────────────────────────────────────────────────
PHASE: int = 1
"""Current MailTrace development phase."""

IS_MOCK_MODE: bool = True
"""True in Phase 1 — real SMTP, real ML models, and live DB not yet connected."""
