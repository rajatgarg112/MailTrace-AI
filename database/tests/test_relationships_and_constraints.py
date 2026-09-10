import pytest
from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError

from app.models import (
    Base,
    User,
    Email,
    EmailEvent,
    AnalysisResult,
    EmailStatus,
    Verdict,
    DEFAULT_EMAIL_STATUS,
)


def test_package_model_exports():
    """Verify that all Phase 1 ORM models and enums are exported from app.models."""
    assert Base is not None
    assert User is not None
    assert Email is not None
    assert EmailEvent is not None
    assert AnalysisResult is not None
    assert EmailStatus is not None
    assert Verdict is not None
    assert DEFAULT_EMAIL_STATUS == EmailStatus.RECEIVED


def test_user_to_emails_1_to_many_relationship(db_session):
    """Verify User -> Emails 1-to-many relationship and foreign key set null on user delete."""
    user = User(email="mailbox_user@example.com")
    db_session.add(user)
    db_session.commit()

    email1 = Email(user_id=user.id, sender="sender1@domain.com", recipients=user.email)
    email2 = Email(user_id=user.id, sender="sender2@domain.com", recipients=user.email)
    db_session.add_all([email1, email2])
    db_session.commit()
    db_session.refresh(user)

    assert len(user.emails) == 2
    assert {e.sender for e in user.emails} == {"sender1@domain.com", "sender2@domain.com"}

    # Test user deletion sets email.user_id to NULL
    user_id = user.id
    db_session.delete(user)
    db_session.commit()

    reloaded_email1 = db_session.query(Email).filter_by(id=email1.id).first()
    assert reloaded_email1 is not None
    assert reloaded_email1.user_id is None
    assert reloaded_email1.user is None


def test_email_to_events_1_to_many_relationship(db_session):
    """Verify Email -> EmailEvents 1-to-many relationship and cascade delete."""
    email = Email(sender="attacker@domain.com", recipients="target@domain.com")
    db_session.add(email)
    db_session.commit()

    evt1 = EmailEvent(email_id=email.id, from_status=None, to_status=EmailStatus.RECEIVED)
    evt2 = EmailEvent(email_id=email.id, from_status=EmailStatus.RECEIVED, to_status=EmailStatus.SCANNING)
    db_session.add_all([evt1, evt2])
    db_session.commit()
    db_session.refresh(email)

    assert len(email.events) == 2
    assert email.events[0].to_status == EmailStatus.RECEIVED
    assert email.events[1].to_status == EmailStatus.SCANNING

    # Cascade delete verification
    email_id = email.id
    db_session.delete(email)
    db_session.commit()

    remaining_events = db_session.query(EmailEvent).filter_by(email_id=email_id).all()
    assert len(remaining_events) == 0


def test_email_to_analysis_result_1_to_1_relationship(db_session):
    """Verify Email -> AnalysisResult 1-to-1 relationship and cascade delete."""
    email = Email(sender="security@service.com", recipients="admin@company.com")
    db_session.add(email)
    db_session.commit()

    result = AnalysisResult(
        email_id=email.id,
        risk_score=0.92,
        verdict=Verdict.MALICIOUS,
        detection_reasons='["Impersonation header", "Phishing link"]',
    )
    db_session.add(result)
    db_session.commit()
    db_session.refresh(email)

    assert email.analysis_result is not None
    assert email.analysis_result.id == result.id
    assert email.analysis_result_id == result.id
    assert result.email.id == email.id

    # Cascade delete verification
    result_id = result.id
    db_session.delete(email)
    db_session.commit()

    remaining_result = db_session.query(AnalysisResult).filter_by(id=result_id).first()
    assert remaining_result is None


def test_unique_constraints(db_session):
    """Verify unique constraints on user.email and analysis_results.email_id."""
    # User email uniqueness
    u1 = User(email="dup@example.com")
    db_session.add(u1)
    db_session.commit()

    u2 = User(email="dup@example.com")
    db_session.add(u2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

    # AnalysisResult email_id 1-to-1 uniqueness
    e1 = Email(sender="s@ex.com", recipients="r@ex.com")
    db_session.add(e1)
    db_session.commit()

    ar1 = AnalysisResult(email_id=e1.id, risk_score=0.1, verdict=Verdict.SAFE)
    db_session.add(ar1)
    db_session.commit()

    ar2 = AnalysisResult(email_id=e1.id, risk_score=0.9, verdict=Verdict.MALICIOUS)
    db_session.add(ar2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_timestamp_datetime_creation(db_session):
    """Verify datetime object creation on model timestamps."""
    u = User(email="tz@example.com")
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)

    assert isinstance(u.created_at, datetime)
    assert u.created_at is not None
