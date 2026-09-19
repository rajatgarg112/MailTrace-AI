from typing import List, Optional
from app.schemas.email import EmailSummary, EmailDetail
from app.schemas.enums import DeliveryStatusEnum, VerdictEnum

# Import shared mock data store from main
# This connects the router-based endpoints to the same data that /api/mailbox/inbox uses
def _get_mock_store():
    """Lazy import to avoid circular dependency."""
    from app import main
    return main.MOCK_INBOX, main.MOCK_QUARANTINE


def get_emails() -> List[dict]:
    """
    Service function to retrieve a list of inbox emails.
    Returns the live MOCK_INBOX store.
    """
    inbox, _ = _get_mock_store()
    return inbox


def get_email_by_id(email_id: str) -> Optional[dict]:
    """
    Service function to retrieve details for a specific email by ID.
    Searches both inbox and quarantine stores.
    """
    inbox, quarantine = _get_mock_store()
    all_messages = inbox + quarantine
    for msg in all_messages:
        if msg.get("id") == email_id:
            return msg
    raise __import__("fastapi").HTTPException(
        status_code=404,
        detail=f"Email '{email_id}' not found"
    )
