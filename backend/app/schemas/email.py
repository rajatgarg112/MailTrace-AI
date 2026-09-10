from typing import Optional, List
from pydantic import BaseModel
from app.schemas.enums import DeliveryStatusEnum, VerdictEnum


class EmailStatus(BaseModel):
    """
    Schema for tracking email security delivery status.
    """
    email_id: str
    status: DeliveryStatusEnum = DeliveryStatusEnum.SCANNING
    risk_score: float = 0.0
    verdict: VerdictEnum = VerdictEnum.SAFE


class EmailSummary(BaseModel):
    """
    Summary schema for mailbox email list items.
    """
    id: str
    sender: str
    recipient: str
    subject: str
    timestamp: str
    status: DeliveryStatusEnum = DeliveryStatusEnum.SAFE
    verdict: VerdictEnum = VerdictEnum.SAFE


class EmailDetail(EmailSummary):
    """
    Detailed schema for single email view including security findings.
    """
    body_text: Optional[str] = None
    body_html: Optional[str] = None
    risk_score: float = 0.0
    signals: List[str] = []
