"""
shared/contracts/ml_result.py
─────────────────────────────────────────────────────────────────────────────
ML Result Contract — output contract for Member 5 (ML Engine).

The ML Engine (ml/service/) returns an MLResultContract after analysing
an email.  The Risk Engine reads this alongside SecurityResultContract to
compute the final RiskDecision.

DO NOT add scoring or decision logic here — this is a pure data contract.
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, ConfigDict


class MLResultContract(BaseModel):
    """
    Output contract for the MailTrace AI/ML Engine.

    Produced by:    ml/service/inference_service.py  (MLInferenceService)
    Consumed by:    Risk Engine (Member 6 / shared/contracts/risk_decision.py)
                    Backend API (Member 2) for evidence storage
                    Frontend (Member 1) for security verdict cards

    Label vocabulary:
        "phishing"   – high-probability phishing / credential-harvesting
        "suspicious" – moderate risk requiring caution
        "benign"     – clean, no overt threat signals
        "unknown"    – insufficient data or processing error fallback
    """

    # ── Source ────────────────────────────────────────────────────────────
    source: str = Field(
        default="ml",
        description="Always 'ml'. Identifies this result as coming from the ML Engine.",
    )

    # ── Core Outputs ──────────────────────────────────────────────────────
    label: str = Field(
        ...,
        description=(
            "ML classification label: 'phishing' | 'suspicious' | 'benign' | 'unknown'."
        ),
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Model confidence for the predicted label (0.0 – 1.0).",
    )
    signals: List[str] = Field(
        default_factory=list,
        description=(
            "Human-readable list of threat indicators detected by the ML module, "
            "e.g. 'Credential harvesting language detected', 'IP-based URL found'."
        ),
    )

    # ── Explanation ───────────────────────────────────────────────────────
    explanation: Optional[str] = Field(
        default=None,
        description=(
            "Optional one-sentence natural-language summary explaining the label "
            "and the primary signals that drove it."
        ),
    )

    # ── Runtime Metadata ──────────────────────────────────────────────────
    model_version: Optional[str] = Field(
        default=None,
        description="Version tag of the model that produced this result.",
    )
    is_placeholder: bool = Field(
        default=False,
        description=(
            "True if this result was produced by the Phase 1 mock classifier. "
            "Must be False in production."
        ),
    )
    execution_time_ms: Optional[float] = Field(
        default=None,
        description="Wall-clock duration of the ML inference pipeline in milliseconds.",
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description=(
            "Optional JSON-serialisable dict of auxiliary metadata "
            "(word count, URL count, has_sender, etc.)."
        ),
    )

    model_config = ConfigDict(from_attributes=True)
