from fastapi import APIRouter
from app.schemas.delivery import DeliveryCreate, DeliveryStatusResponse
from app.services import delivery_service

router = APIRouter(prefix="/deliveries", tags=["Deliveries"])


@router.post("", response_model=DeliveryStatusResponse, status_code=202)
def create_delivery(delivery: DeliveryCreate):
    """
    Initiate delivery transaction via delivery service.
    """
    return delivery_service.create_delivery_transaction(delivery)
