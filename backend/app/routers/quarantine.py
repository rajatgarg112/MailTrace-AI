from typing import List
from fastapi import APIRouter
from app.schemas.email import EmailSummary
from app.services import quarantine_service

router = APIRouter(prefix="/quarantine", tags=["Quarantine"])


@router.get("", response_model=List[EmailSummary], status_code=200)
def list_quarantine_items():
    """
    List quarantine items via quarantine service.
    """
    return quarantine_service.get_quarantine_items()
