"""
shared/contracts/security_result.py
─────────────────────────────────────────────────────────────────────────────
Security Result Contract — output contract for Member 4 (Security Engine).

Each analyser in security/analysis/ returns one SecuritySignal.
The aggregated list is wrapped in SecurityResultContract and passed to the
Risk Engine (Member 6) for score computation.
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict

from shared.enums.verdict import Verdict


class SecuritySignal(BaseModel):
    """
    Represents a single threat indicator detected by a security analyser.

    Produced by:
        • Header forensics        (security/analysis/header_forensics.py)
        • Authentication checks   (security/analysis/authentication.py)
        • URL analysis            (security/analysis/url_analysis.py)
        • Attachment analysis     (security/analysis/attachment_analysis.py)
        • PII detection           (security/analysis/pii_redaction.py)
        • NLP / detection         (security/analysis/detection.py)
    """

    signal: str = Field(
        ...,
        description=(
            "Machine-readable signal identifier, e.g. 'SPF_FAIL', "
            "'LOOKALIKE_DOMAIN', 'MALICIOUS_URL'."
        ),
    )
    category: str = Field(
        ...,
        description=(
            "High-level grouping, e.g. 'AUTHENTICATION', 'HEADER', "
            "'URL', 'ATTACHMENT', 'PII', 'NLP'."
        ),
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence level for this signal (0.0 – 1.0).",
    )
    risk: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Risk contribution of this signal (0.0 – 100.0).",
    )
    evidence: Optional[str] = Field(
        default=None,
        description="Human-readable forensic evidence or explanation string.",
    )

    model_config = ConfigDict(from_attributes=True)


class SecurityResultContract(BaseModel):
    """
    Aggregated output from the Security Engine for a single email.

    The Risk Engine reads this contract to combine security signals with
    ML predictions into the final RiskDecision.
    """

    emailId: str = Field(..., description="UUID of the analysed email.")
    signals: List[SecuritySignal] = Field(
        default_factory=list,
        description="All security signals detected across all analysers.",
    )
    overallVerdict: Verdict = Field(
        default=Verdict.UNKNOWN,
        description="Aggregated verdict from the Security Engine.",
    )
    totalRiskScore: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Composite risk score calculated by security policy engine (0–100).",
    )
    rawDetails: Optional[Dict[str, Any]] = Field(
        default=None,
        description=(
            "Optional JSON-serialisable dict containing the full raw outputs "
            "from individual analysers (for forensic logging / UI evidence cards)."
        ),
    )

    model_config = ConfigDict(from_attributes=True)
