import pytest
from app.core.seed import seed_database
from app.core.database import SessionLocal
from app.models import User, Email, EmailEvent, AnalysisResult, EmailStatus, Verdict


def test_seed_database_execution():
    """Verify that seed_database() executes, inserts mock records, and is safely idempotent."""
    # First execution
    seed_database()

    session = SessionLocal()
    try:
        users = session.query(User).filter(User.email.like("%@example.dev")).all()
        assert len(users) == 2

        emails = session.query(Email).all()
        assert len(emails) >= 5

        statuses = {e.status for e in emails}
        assert EmailStatus.DELIVERED in statuses
        assert EmailStatus.WARNING in statuses
        assert EmailStatus.QUARANTINED in statuses
        assert EmailStatus.SCANNING in statuses
        assert EmailStatus.REJECTED in statuses

        events = session.query(EmailEvent).all()
        assert len(events) >= 10

        analysis_results = session.query(AnalysisResult).all()
        assert len(analysis_results) >= 3

        verdicts = {ar.verdict for ar in analysis_results}
        assert Verdict.SAFE in verdicts
        assert Verdict.SUSPICIOUS in verdicts
        assert Verdict.MALICIOUS in verdicts

    finally:
        session.close()

    # Second execution (verify idempotency)
    seed_database()

    session2 = SessionLocal()
    try:
        users_after = session2.query(User).filter(User.email.like("%@example.dev")).all()
        assert len(users_after) == 2
    finally:
        session2.close()
