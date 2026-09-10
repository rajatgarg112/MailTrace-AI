from app.schemas.delivery import DeliveryCreate, DeliveryStatusResponse
from app.schemas.enums import DeliveryStatusEnum, VerdictEnum


def create_delivery_transaction(payload: DeliveryCreate) -> DeliveryStatusResponse:
    """
    Service function to handle initiating an email delivery transaction.
    """
    return DeliveryStatusResponse(
        delivery_id="del_123",
        email_id="msg_001",
        status=DeliveryStatusEnum.SCANNING,
        risk_score=0.0,
        verdict=VerdictEnum.SAFE,
        message=f"Delivery transaction initiated for {payload.recipient}",
    )
