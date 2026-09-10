from typing import Optional
from pydantic import BaseModel
from app.schemas.enums import DeliveryStatusEnum, VerdictEnum


class DeliveryCreate(BaseModel):
    """
    Schema for initiating an email delivery transaction.
    """
    recipient: str
    raw_email: Optional[str] = None
    source: Optional[str] = "SMTP_SIMULATION"


class DeliveryStatusResponse(BaseModel):
    """
    Schema for delivery transaction response.
    """
    delivery_id: str
    email_id: Optional[str] = None
    status: DeliveryStatusEnum = DeliveryStatusEnum.SCANNING
    risk_score: float = 0.0
    verdict: VerdictEnum = VerdictEnum.SAFE
    message: str = "Delivery transaction processing"
