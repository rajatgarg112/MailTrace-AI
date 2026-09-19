import uuid
from app.schemas.delivery import DeliveryCreate, DeliveryStatusResponse
from app.schemas.enums import DeliveryStatusEnum, VerdictEnum


def create_delivery_transaction(payload: DeliveryCreate) -> DeliveryStatusResponse:
    """
    Service function to handle initiating an email delivery transaction.
    Generates unique delivery and email IDs per transaction.
    """
    return DeliveryStatusResponse(
        delivery_id=f"del_{uuid.uuid4().hex[:8]}",
        email_id=f"msg_{uuid.uuid4().hex[:6]}",
        status=DeliveryStatusEnum.SCANNING,
        risk_score=0.0,
        verdict=VerdictEnum.SAFE,
        message=f"Delivery transaction initiated for {payload.recipient}",
    )
