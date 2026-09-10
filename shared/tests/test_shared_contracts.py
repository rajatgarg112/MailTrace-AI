"""
shared/tests/test_shared_contracts.py
─────────────────────────────────────────────────────────────────────────────
Verification tests for the shared foundation (Member 6).

Run with:  python -m pytest shared/tests/ -v
─────────────────────────────────────────────────────────────────────────────
"""

import sys
import os

# Allow running from project root without installing as a package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from datetime import datetime, timezone


# ── 1. Enum imports ────────────────────────────────────────────────────────

def test_email_status_import():
    from shared.enums.email_status import EmailStatus
    assert EmailStatus.RECEIVED == "RECEIVED"
    assert EmailStatus.DELIVERED == "DELIVERED"
    assert len(EmailStatus.list_values()) == 9
    assert EmailStatus.is_valid("QUARANTINED") is True
    assert EmailStatus.is_valid("GARBAGE") is False


def test_risk_decision_import():
    from shared.enums.decision import RiskDecision
    assert RiskDecision.QUARANTINED == "QUARANTINED"
    assert "FAILED" in RiskDecision.list_values()


def test_verdict_import():
    from shared.enums.verdict import Verdict
    assert Verdict.MALICIOUS == "MALICIOUS"
    assert Verdict.is_valid("SAFE") is True


# ── 2. Contract imports ────────────────────────────────────────────────────

def test_email_contract():
    from shared.contracts.email_contract import EmailContract
    email = EmailContract(
        id="test-uuid-001",
        sender="Test Sender",
        senderEmail="sender@test.com",
        recipient="recipient@test.com",
        subject="Test Subject",
        body="Hello world",
    )
    assert email.status == "RECEIVED"
    assert email.riskScore == 0.0
    assert isinstance(email.securityReasons, list)


def test_security_result_contract():
    from shared.contracts.security_result import SecurityResultContract, SecuritySignal
    signal = SecuritySignal(
        signal="SPF_FAIL",
        category="AUTHENTICATION",
        confidence=0.95,
        risk=20.0,
        evidence="SPF record lookup returned FAIL",
    )
    result = SecurityResultContract(
        emailId="test-uuid-001",
        signals=[signal],
        totalRiskScore=20.0,
    )
    assert len(result.signals) == 1
    assert result.signals[0].signal == "SPF_FAIL"


def test_ml_result_contract():
    from shared.contracts.ml_result import MLResultContract
    ml = MLResultContract(
        label="phishing",
        confidence=0.87,
        signals=["Credential harvesting language detected"],
        is_placeholder=True,
    )
    assert ml.source == "ml"
    assert ml.label == "phishing"
    assert 0.0 <= ml.confidence <= 1.0


def test_risk_decision_contract():
    from shared.contracts.risk_decision import RiskDecisionContract
    from shared.enums.decision import RiskDecision
    decision = RiskDecisionContract(
        emailId="test-uuid-001",
        riskScore=67.5,
        decision=RiskDecision.QUARANTINED,
        reasons=["SPF_FAIL", "MALICIOUS_URL"],
    )
    assert decision.decision == "QUARANTINED"
    assert isinstance(decision.timestamp, datetime)


def test_email_event_contract():
    from shared.contracts.email_event import EmailEventContract
    from shared.enums.email_status import EmailStatus
    event = EmailEventContract(
        emailId="test-uuid-001",
        event=EmailStatus.SCANNING,
        fromStatus=EmailStatus.RECEIVED,
    )
    assert event.event == "SCANNING"
    assert event.fromStatus == "RECEIVED"


# ── 3. Constants ───────────────────────────────────────────────────────────

def test_constants_import():
    from shared.constants.pipeline import (
        RISK_THRESHOLD_WARNING,
        RISK_THRESHOLD_QUARANTINE,
        RISK_THRESHOLD_REJECT,
        PHASE,
    )
    assert RISK_THRESHOLD_WARNING < RISK_THRESHOLD_QUARANTINE < RISK_THRESHOLD_REJECT
    assert PHASE == 1


# ── 4. Top-level shared package ────────────────────────────────────────────

def test_top_level_import():
    import shared
    assert hasattr(shared, "EmailStatus")
    assert hasattr(shared, "EmailContract")
    assert hasattr(shared, "MLResultContract")
    assert hasattr(shared, "RiskDecisionContract")
    assert hasattr(shared, "RISK_THRESHOLD_QUARANTINE")


# ── 5. No circular imports ─────────────────────────────────────────────────

def test_no_circular_imports():
    """Importing all modules in sequence should not raise ImportError."""
    import shared.enums.email_status
    import shared.enums.decision
    import shared.enums.verdict
    import shared.contracts.email_contract
    import shared.contracts.security_result
    import shared.contracts.ml_result
    import shared.contracts.risk_decision
    import shared.contracts.email_event
    import shared.constants.pipeline
    import shared.schemas.api_envelope
