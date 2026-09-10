import os
import sys
import json
from datetime import datetime, timezone, timedelta

# Ensure database directory is in sys.path when executed directly as CLI script
database_dir = os.path.realpath(os.path.join(os.path.dirname(__file__), "..", ".."))
if database_dir not in sys.path:
    sys.path.insert(0, database_dir)

from app.core.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.email import Email
from app.models.email_event import EmailEvent
from app.models.analysis_result import AnalysisResult
from app.models.enums import EmailStatus, Verdict


def seed_database() -> None:
    """
    Development-only seed script to populate mock users, emails, lifecycle events, and analysis results.
    Idempotent: clears existing mock data or safely re-applies seed entries.
    """
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)

    session = SessionLocal()
    try:
        # Check if seed data already exists to ensure idempotency
        existing_users = session.query(User).filter(User.email.like("%@example.dev")).all()
        if existing_users:
            print("Seed dataset already exists. Clearing existing mock data...")
            for u in existing_users:
                session.delete(u)
            session.commit()

        print("Seeding development dataset...")

        now = datetime.now(timezone.utc)

        # 1. Sample Users
        user1 = User(email="alice.analyst@example.dev")
        user2 = User(email="bob.employee@example.dev")
        session.add_all([user1, user2])
        session.commit()
        session.refresh(user1)
        session.refresh(user2)

        # 2. Sample Emails with various lifecycle statuses

        # Email 1: DELIVERED (Safe newsletter)
        email1 = Email(
            user_id=user1.id,
            message_id="msg-001-safe@example.dev",
            sender="newsletter@techdigest.dev",
            recipients=user1.email,
            subject="Weekly Developer Updates",
            body="Here are the latest updates in software engineering.",
            status=EmailStatus.DELIVERED,
            received_at=now - timedelta(minutes=60),
        )

        # Email 2: WARNING (Suspicious login alert)
        email2 = Email(
            user_id=user2.id,
            message_id="msg-002-suspicious@example.dev",
            sender="security-alert@fakebank.dev",
            recipients=user2.email,
            subject="Action Required: Verify Account Credentials Immediately",
            body="Your account will be suspended. Click http://login-fakebank.dev/verify",
            status=EmailStatus.WARNING,
            received_at=now - timedelta(minutes=45),
        )

        # Email 3: QUARANTINED (Phishing email with malicious score)
        email3 = Email(
            user_id=user2.id,
            message_id="msg-003-malicious@example.dev",
            sender="payroll-update@malicious-domain.dev",
            recipients=user2.email,
            subject="Urgent: Updated Direct Deposit Form",
            body="Please open the attached form to update your banking details.",
            status=EmailStatus.QUARANTINED,
            received_at=now - timedelta(minutes=30),
        )

        # Email 4: SCANNING (In-flight processing)
        email4 = Email(
            user_id=user1.id,
            message_id="msg-004-scanning@example.dev",
            sender="colleague@partner.dev",
            recipients=user1.email,
            subject="Project Roadmap Review",
            body="Can we schedule a call to review the Q4 roadmap?",
            status=EmailStatus.SCANNING,
            received_at=now - timedelta(minutes=5),
        )

        # Email 5: REJECTED (Blocked at gateway)
        email5 = Email(
            user_id=user2.id,
            message_id="msg-005-rejected@example.dev",
            sender="spammer@blacklisted-domain.dev",
            recipients=user2.email,
            subject="Exclusive Offer: Claim Your Prize Now",
            body="Congratulations! You won a prize.",
            status=EmailStatus.REJECTED,
            received_at=now - timedelta(minutes=15),
        )

        session.add_all([email1, email2, email3, email4, email5])
        session.commit()
        for e in [email1, email2, email3, email4, email5]:
            session.refresh(e)

        # 3. EmailEvents history

        # History for email1 (RECEIVED -> SCANNING -> DECISION -> DELIVERED)
        events1 = [
            EmailEvent(
                email_id=email1.id,
                from_status=None,
                to_status=EmailStatus.RECEIVED,
                timestamp=now - timedelta(minutes=60),
                event_type="INGESTED",
                details="Ingested via development seed mock",
            ),
            EmailEvent(
                email_id=email1.id,
                from_status=EmailStatus.RECEIVED,
                to_status=EmailStatus.SCANNING,
                timestamp=now - timedelta(minutes=59),
                event_type="ANALYSIS_STARTED",
            ),
            EmailEvent(
                email_id=email1.id,
                from_status=EmailStatus.SCANNING,
                to_status=EmailStatus.DECISION,
                timestamp=now - timedelta(minutes=58),
                event_type="RISK_EVALUATED",
            ),
            EmailEvent(
                email_id=email1.id,
                from_status=EmailStatus.DECISION,
                to_status=EmailStatus.DELIVERED,
                timestamp=now - timedelta(minutes=57),
                event_type="DELIVERED_TO_INBOX",
            ),
        ]

        # History for email2 (RECEIVED -> SCANNING -> DECISION -> WARNING)
        events2 = [
            EmailEvent(
                email_id=email2.id,
                from_status=None,
                to_status=EmailStatus.RECEIVED,
                timestamp=now - timedelta(minutes=45),
                event_type="INGESTED",
            ),
            EmailEvent(
                email_id=email2.id,
                from_status=EmailStatus.RECEIVED,
                to_status=EmailStatus.SCANNING,
                timestamp=now - timedelta(minutes=44),
                event_type="ANALYSIS_STARTED",
            ),
            EmailEvent(
                email_id=email2.id,
                from_status=EmailStatus.SCANNING,
                to_status=EmailStatus.WARNING,
                timestamp=now - timedelta(minutes=43),
                event_type="SUSPICIOUS_FLAG_APPLIED",
                details="Suspicious link detected in email body",
            ),
        ]

        # History for email3 (RECEIVED -> SCANNING -> DECISION -> QUARANTINED)
        events3 = [
            EmailEvent(
                email_id=email3.id,
                from_status=None,
                to_status=EmailStatus.RECEIVED,
                timestamp=now - timedelta(minutes=30),
                event_type="INGESTED",
            ),
            EmailEvent(
                email_id=email3.id,
                from_status=EmailStatus.RECEIVED,
                to_status=EmailStatus.SCANNING,
                timestamp=now - timedelta(minutes=29),
                event_type="ANALYSIS_STARTED",
            ),
            EmailEvent(
                email_id=email3.id,
                from_status=EmailStatus.SCANNING,
                to_status=EmailStatus.QUARANTINED,
                timestamp=now - timedelta(minutes=28),
                event_type="QUARANTINED",
                details="High-risk phishing indicators detected",
            ),
        ]

        session.add_all(events1 + events2 + events3)
        session.commit()

        # 4. AnalysisResult Records

        res1 = AnalysisResult(
            email_id=email1.id,
            risk_score=0.05,
            verdict=Verdict.SAFE,
            detection_reasons=json.dumps(["All SPF/DKIM checks passed", "No suspicious links detected"]),
            analysis_duration_ms=45.2,
            details_json=json.dumps({"spf": "PASS", "dkim": "PASS", "ai_score": 0.02}),
        )

        res2 = AnalysisResult(
            email_id=email2.id,
            risk_score=0.68,
            verdict=Verdict.SUSPICIOUS,
            detection_reasons=json.dumps(["Suspicious external URL present", "Domain mismatch in sender header"]),
            analysis_duration_ms=112.8,
            details_json=json.dumps({"urls_flagged": 1, "domain_age_days": 3}),
        )

        res3 = AnalysisResult(
            email_id=email3.id,
            risk_score=0.96,
            verdict=Verdict.MALICIOUS,
            detection_reasons=json.dumps(["Executive impersonation signal high", "Known phishing lure body text"]),
            analysis_duration_ms=189.4,
            details_json=json.dumps({"ai_score": 0.98, "impersonation_detected": True}),
        )

        session.add_all([res1, res2, res3])
        session.commit()

        print("Database successfully seeded with mock development dataset!")

    finally:
        session.close()


if __name__ == "__main__":
    seed_database()
