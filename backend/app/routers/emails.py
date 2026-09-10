from typing import List
from fastapi import APIRouter
from app.schemas.email import EmailSummary, EmailDetail
from app.services import email_service

router = APIRouter(prefix="/emails", tags=["Emails"])


@router.get("", response_model=List[EmailSummary], status_code=200)
def list_emails():
    """
    List emails via email service.
    """
    return email_service.get_emails()


@router.get("/{email_id}", response_model=EmailDetail, status_code=200)
def get_email(email_id: str):
    """
    Get email details via email service.
    """
    return email_service.get_email_by_id(email_id)
