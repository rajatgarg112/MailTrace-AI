import pytest
from app.models.enums import EmailStatus, DEFAULT_EMAIL_STATUS
from app.models.email import Email


def test_email_status_canonical_members():
    expected_statuses = {
        "RECEIVED",
        "SCANNING",
        "DECISION",
        "DELIVERED",
        "WARNING",
        "QUARANTINED",
        "REJECTED",
        "FAILED",
        "UNKNOWN",
    }
    actual_statuses = set(EmailStatus.list_values())
    assert actual_statuses == expected_statuses
    assert len(EmailStatus) == 9


def test_email_status_is_valid_helper():
    assert EmailStatus.is_valid("RECEIVED") is True
    assert EmailStatus.is_valid("QUARANTINED") is True
    assert EmailStatus.is_valid("INVALID_STATUS") is False
    assert EmailStatus.is_valid("received") is False  # Case sensitive check


def test_default_email_status():
    assert DEFAULT_EMAIL_STATUS == EmailStatus.RECEIVED


def test_email_model_uses_canonical_status(db_session):
    email = Email(
        sender="sender@example.com",
        recipients="user@example.com",
    )
    db_session.add(email)
    db_session.commit()
    db_session.refresh(email)

    assert email.status == EmailStatus.RECEIVED
    assert email.status == DEFAULT_EMAIL_STATUS
    assert isinstance(email.status, EmailStatus)
