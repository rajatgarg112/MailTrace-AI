import pytest
from datetime import datetime, timezone
from app.models.user import User
from app.models.email import Email
from app.models.enums import EmailStatus


def test_create_email_default_status(db_session):
    email = Email(
        sender="sender@example.com",
        recipients="recipient1@example.com, recipient2@example.com",
        subject="Test Phishing Analysis",
        body="Suspicious email content",
    )
    db_session.add(email)
    db_session.commit()
    db_session.refresh(email)

    assert email.id is not None
    assert len(email.id) == 36
    assert email.sender == "sender@example.com"
    assert email.status == EmailStatus.RECEIVED
    assert email.recipient_list == ["recipient1@example.com", "recipient2@example.com"]
    assert email.created_at is not None
    assert email.updated_at is not None


def test_email_recipient_list_property_setter(db_session):
    email = Email(
        sender="alert@bank.com",
        recipients="",
        subject="Account Verification",
    )
    email.recipient_list = ["victim1@company.com", "victim2@company.com"]
    db_session.add(email)
    db_session.commit()
    db_session.refresh(email)

    assert email.recipients == "victim1@company.com, victim2@company.com"
    assert email.recipient_list == ["victim1@company.com", "victim2@company.com"]


def test_email_lifecycle_statuses_support(db_session):
    statuses = [
        EmailStatus.RECEIVED,
        EmailStatus.SCANNING,
        EmailStatus.DECISION,
        EmailStatus.DELIVERED,
        EmailStatus.WARNING,
        EmailStatus.QUARANTINED,
        EmailStatus.REJECTED,
        EmailStatus.FAILED,
        EmailStatus.UNKNOWN,
    ]

    email = Email(
        sender="test@domain.com",
        recipients="target@domain.com",
        status=EmailStatus.RECEIVED,
    )
    db_session.add(email)
    db_session.commit()

    for status_value in statuses:
        email.status = status_value
        db_session.commit()
        db_session.refresh(email)
        assert email.status == status_value


def test_user_email_relationship_set_null(db_session):
    user = User(email="recipient_owner@company.com")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    email = Email(
        user_id=user.id,
        sender="external@attacker.com",
        recipients=user.email,
        subject="Urgent Transfer",
    )
    db_session.add(email)
    db_session.commit()
    db_session.refresh(user)

    assert len(user.emails) == 1
    assert user.emails[0].id == email.id
    assert email.user.id == user.id

    # Verify user deletion sets email.user_id to None (SET NULL)
    db_session.delete(user)
    db_session.commit()

    reloaded_email = db_session.query(Email).filter_by(id=email.id).first()
    assert reloaded_email is not None
    assert reloaded_email.user_id is None


def test_email_str_repr():
    email = Email(
        id="email-uuid-5678",
        sender="spoofed@fake.com",
        status=EmailStatus.QUARANTINED,
    )
    assert repr(email) == "<Email(id='email-uuid-5678', sender='spoofed@fake.com', status='QUARANTINED')>"
