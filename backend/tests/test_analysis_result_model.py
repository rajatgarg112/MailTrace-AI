import json
import pytest
from sqlalchemy.exc import IntegrityError
from app.models.email import Email
from app.models.analysis_result import AnalysisResult
from app.models.enums import EmailStatus, Verdict
from app.schemas.analysis_result import AnalysisResultResponse


def test_create_analysis_result(db_session):
    email = Email(
        sender="phisher@suspicious-domain.com",
        recipients="employee@company.com",
        subject="Urgent Security Update Needed",
        status=EmailStatus.DECISION,
    )
    db_session.add(email)
    db_session.commit()

    reasons = json.dumps([
        "SPF failed for domain",
        "High urgency keywords detected in email body",
        "Discrepancy between From header and Return-Path",
    ])
    details = json.dumps({
        "ai_confidence": 0.94,
        "spf_pass": False,
        "urls_flagged": 2,
    })

    result = AnalysisResult(
        email_id=email.id,
        risk_score=0.88,
        verdict=Verdict.MALICIOUS,
        detection_reasons=reasons,
        analysis_duration_ms=145.5,
        details_json=details,
    )
    db_session.add(result)
    db_session.commit()
    db_session.refresh(result)

    assert result.id is not None
    assert len(result.id) == 36
    assert result.email_id == email.id
    assert result.risk_score == 0.88
    assert result.verdict == Verdict.MALICIOUS
    assert result.detection_reasons == reasons
    assert result.analysis_duration_ms == 145.5
    assert result.details_json == details
    assert result.created_at is not None
    assert result.updated_at is not None

    # Bi-directional 1-to-1 relationship verification
    assert email.analysis_result.id == result.id
    assert result.email.id == email.id


def test_analysis_result_verdicts(db_session):
    verdicts = [Verdict.SAFE, Verdict.SUSPICIOUS, Verdict.MALICIOUS, Verdict.UNKNOWN]
    for v in verdicts:
        email = Email(sender="test@example.com", recipients="user@example.com")
        db_session.add(email)
        db_session.commit()

        result = AnalysisResult(
            email_id=email.id,
            risk_score=0.1 if v == Verdict.SAFE else 0.9,
            verdict=v,
        )
        db_session.add(result)
        db_session.commit()
        db_session.refresh(result)

        assert result.verdict == v


def test_analysis_result_unique_email_constraint(db_session):
    email = Email(sender="s@example.com", recipients="r@example.com")
    db_session.add(email)
    db_session.commit()

    res1 = AnalysisResult(email_id=email.id, risk_score=0.2, verdict=Verdict.SAFE)
    db_session.add(res1)
    db_session.commit()

    res2 = AnalysisResult(email_id=email.id, risk_score=0.8, verdict=Verdict.MALICIOUS)
    db_session.add(res2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_analysis_result_cascade_delete(db_session):
    email = Email(sender="s@example.com", recipients="r@example.com")
    db_session.add(email)
    db_session.commit()

    result = AnalysisResult(email_id=email.id, risk_score=0.5, verdict=Verdict.SUSPICIOUS)
    db_session.add(result)
    db_session.commit()

    result_id = result.id
    db_session.delete(email)
    db_session.commit()

    queried_result = db_session.query(AnalysisResult).filter_by(id=result_id).first()
    assert queried_result is None


def test_analysis_result_pydantic_schema_serialization(db_session):
    email = Email(sender="s@example.com", recipients="r@example.com")
    db_session.add(email)
    db_session.commit()

    result = AnalysisResult(
        email_id=email.id,
        risk_score=0.75,
        verdict=Verdict.SUSPICIOUS,
        detection_reasons='["Suspicious URL detected"]',
        analysis_duration_ms=82.1,
    )
    db_session.add(result)
    db_session.commit()
    db_session.refresh(result)

    schema_data = AnalysisResultResponse.model_validate(result)
    assert schema_data.id == result.id
    assert schema_data.email_id == email.id
    assert schema_data.risk_score == 0.75
    assert schema_data.verdict == Verdict.SUSPICIOUS
    assert schema_data.detection_reasons == '["Suspicious URL detected"]'
    assert schema_data.analysis_duration_ms == 82.1


def test_analysis_result_str_repr():
    res = AnalysisResult(
        id="res-uuid-1234",
        email_id="email-uuid-5678",
        risk_score=0.95,
        verdict=Verdict.MALICIOUS,
    )
    assert repr(res) == "<AnalysisResult(id='res-uuid-1234', email_id='email-uuid-5678', score=0.95, verdict='MALICIOUS')>"
