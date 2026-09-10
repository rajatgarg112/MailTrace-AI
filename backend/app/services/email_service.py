from typing import List, Optional
from app.schemas.email import EmailSummary, EmailDetail
from app.schemas.enums import DeliveryStatusEnum, VerdictEnum


def get_emails() -> List[EmailSummary]:
    """
    Service function to retrieve a list of emails.
    """
    return []


def get_email_by_id(email_id: str) -> Optional[EmailDetail]:
    """
    Service function to retrieve details for a specific email by ID.
    """
    return EmailDetail(
        id=email_id,
        sender="placeholder@mailtrace.local",
        recipient="user@mailtrace.local",
        subject="Placeholder Email Subject",
        timestamp="2026-09-10T14:30:00Z",
        status=DeliveryStatusEnum.SAFE,
        verdict=VerdictEnum.SAFE,
        body_text="Placeholder email body content.",
        risk_score=0.0,
        signals=[],
    )
