import pytest
from datetime import datetime, timezone, timedelta
from app.models.email import Email
from app.models.email_event import EmailEvent
from app.models.enums import EmailStatus
from app.schemas.email_event import EmailEventResponse


def test_create_email_event(db_session):
    email = Email(
        sender="sender@example.com",
        recipients="receiver@example.com",
        status=EmailStatus.RECEIVED,
    )
    db_session.add(email)
    db_session.commit()

    event = EmailEvent(
        email_id=email.id,
        from_status=None,
        to_status=EmailStatus.RECEIVED,
        event_type="INGESTED",
        details="Initial email ingestion from Gmail API",
    )
    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)

    assert event.id is not None
    assert len(event.id) == 36
    assert event.email_id == email.id
    assert event.from_status is None
    assert event.to_status == EmailStatus.RECEIVED
    assert event.event_type == "INGESTED"
    assert event.details == "Initial email ingestion from Gmail API"
    assert event.timestamp is not None
    assert event.email.id == email.id


def test_email_events_history_ordering(db_session):
    email = Email(
        sender="attacker@domain.com",
        recipients="victim@domain.com",
        status=EmailStatus.RECEIVED,
    )
    db_session.add(email)
    db_session.commit()

    now = datetime.now(timezone.utc)
    event1 = EmailEvent(
        email_id=email.id,
        from_status=None,
        to_status=EmailStatus.RECEIVED,
        timestamp=now,
    )
    event2 = EmailEvent(
        email_id=email.id,
        from_status=EmailStatus.RECEIVED,
        to_status=EmailStatus.SCANNING,
        timestamp=now + timedelta(seconds=2),
    )
    event3 = EmailEvent(
        email_id=email.id,
        from_status=EmailStatus.SCANNING,
        to_status=EmailStatus.DECISION,
        timestamp=now + timedelta(seconds=5),
    )
    event4 = EmailEvent(
        email_id=email.id,
        from_status=EmailStatus.DECISION,
        to_status=EmailStatus.QUARANTINED,
        timestamp=now + timedelta(seconds=6),
    )
    db_session.add_all([event1, event2, event3, event4])
    db_session.commit()
    db_session.refresh(email)

    assert len(email.events) == 4
    # Verify chronological ordering
    assert [e.to_status for e in email.events] == [
        EmailStatus.RECEIVED,
        EmailStatus.SCANNING,
        EmailStatus.DECISION,
        EmailStatus.QUARANTINED,
    ]


def test_email_event_foreign_key_cascade(db_session):
    email = Email(
        sender="test@example.com",
        recipients="user@example.com",
    )
    db_session.add(email)
    db_session.commit()

    event = EmailEvent(
        email_id=email.id,
        from_status=EmailStatus.RECEIVED,
        to_status=EmailStatus.FAILED,
        details="Pipeline failure test",
    )
    db_session.add(event)
    db_session.commit()

    event_id = event.id
    db_session.delete(email)
    db_session.commit()

    queried_event = db_session.query(EmailEvent).filter_by(id=event_id).first()
    assert queried_event is None


def test_email_event_pydantic_schema_serialization(db_session):
    email = Email(
        sender="sender@test.com",
        recipients="target@test.com",
    )
    db_session.add(email)
    db_session.commit()

    event = EmailEvent(
        email_id=email.id,
        from_status=EmailStatus.SCANNING,
        to_status=EmailStatus.WARNING,
        details="Suspicious link detected in message body",
    )
    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)

    schema_data = EmailEventResponse.model_validate(event)
    assert schema_data.id == event.id
    assert schema_data.email_id == email.id
    assert schema_data.from_status == EmailStatus.SCANNING
    assert schema_data.to_status == EmailStatus.WARNING
    assert schema_data.details == "Suspicious link detected in message body"


def test_email_event_str_repr():
    event = EmailEvent(
        id="evt-uuid-9999",
        email_id="email-uuid-1111",
        from_status=EmailStatus.RECEIVED,
        to_status=EmailStatus.SCANNING,
    )
    assert repr(event) == "<EmailEvent(id='evt-uuid-9999', email_id='email-uuid-1111', from='RECEIVED', to='SCANNING')>"
