"""
shared/contracts/risk_decision.py
─────────────────────────────────────────────────────────────────────────────
Risk Decision Contract — final output of the MailTrace Risk Engine.

The Risk Engine (Member 6) reads SecurityResultContract + MLResultContract
and produces a single RiskDecisionContract.

The Backend (Member 2) persists this in database/app/models/analysis_result.py
and returns it to the Frontend (Member 1) for rendering.

DO NOT implement scoring or decision logic here.
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List
from pydantic import BaseModel, Field, ConfigDict

from shared.enums.decision import RiskDecision


class RiskDecisionContract(BaseModel):
    """
    Final risk assessment and delivery decision for a single email.

    Produced by:    Risk Engine (Member 6)
    Consumed by:    Backend API (Member 2)  → stored in AnalysisResult table
                    Frontend (Member 1)     → inbox status badges / verdict UI
                    Database (Member 3)     → via EmailResponse schema
    """

    # ── Identity ──────────────────────────────────────────────────────────
    emailId: str = Field(..., description="UUID of the email this decision applies to.")

    # ── Risk Quantification ───────────────────────────────────────────────
    riskScore: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description=(
            "Final composite risk score (0.0 = completely safe, 100.0 = definitively malicious). "
            "Computed by the Risk Engine from Security + ML outputs."
        ),
    )

    # ── Verdict ───────────────────────────────────────────────────────────
    decision: RiskDecision = Field(
        ...,
        description=(
            "Final delivery action: DELIVERED | WARNING | QUARANTINED | REJECTED | FAILED."
        ),
    )

    # ── Reasoning ─────────────────────────────────────────────────────────
    reasons: List[str] = Field(
        default_factory=list,
        description=(
            "Ordered list of human-readable reasons that drove this decision. "
            "Combine security signals and ML signals here for traceability."
        ),
    )

    # ── Timing ────────────────────────────────────────────────────────────
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp at which the Risk Engine produced this decision.",
    )

    model_config = ConfigDict(from_attributes=True)
