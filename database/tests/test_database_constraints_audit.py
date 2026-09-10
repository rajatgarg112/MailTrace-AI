import pytest
from sqlalchemy.exc import IntegrityError
from app.models import User, Email, EmailEvent, AnalysisResult, EmailStatus, Verdict


def test_user_non_nullable_email_constraint(db_session):
    """Verify IntegrityError is raised when creating a User without an email."""
    user = User(email=None)  # type: ignore
    db_session.add(user)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_email_non_nullable_fields_constraint(db_session):
    """Verify IntegrityError is raised when creating an Email missing sender or recipients."""
    # Missing sender
    email_no_sender = Email(sender=None, recipients="user@example.com")  # type: ignore
    db_session.add(email_no_sender)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

    # Missing recipients
    email_no_recipients = Email(sender="sender@example.com", recipients=None)  # type: ignore
    db_session.add(email_no_recipients)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_email_event_non_nullable_to_status_constraint(db_session):
    """Verify IntegrityError is raised when creating an EmailEvent missing to_status."""
    email = Email(sender="s@example.com", recipients="r@example.com")
    db_session.add(email)
    db_session.commit()

    event = EmailEvent(
        email_id=email.id,
        from_status=EmailStatus.RECEIVED,
        to_status=None,  # type: ignore
    )
    db_session.add(event)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_analysis_result_non_nullable_email_id_constraint(db_session):
    """Verify IntegrityError is raised when creating an AnalysisResult missing email_id."""
    res_no_email = AnalysisResult(
        email_id=None,  # type: ignore
        risk_score=0.5,
        verdict=Verdict.SUSPICIOUS,
    )
    db_session.add(res_no_email)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_nullable_optional_fields_pass(db_session):
    """Verify that optional fields (message_id, subject, body, received_at, details) accept None cleanly."""
    email = Email(
        sender="minimal@example.com",
        recipients="target@example.com",
        message_id=None,
        subject=None,
        body=None,
        received_at=None,
    )
    db_session.add(email)
    db_session.commit()
    db_session.refresh(email)

    assert email.id is not None
    assert email.message_id is None
    assert email.subject is None
    assert email.body is None
    assert email.received_at is None
