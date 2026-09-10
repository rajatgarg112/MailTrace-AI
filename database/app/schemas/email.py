from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from app.models.enums import EmailStatus


class EmailBase(BaseModel):
    sender: str
    recipients: List[str]
    subject: Optional[str] = None
    body: Optional[str] = None
    message_id: Optional[str] = None


class EmailCreate(EmailBase):
    user_id: Optional[str] = None
    received_at: Optional[datetime] = None


class EmailResponse(EmailBase):
    id: str
    user_id: Optional[str] = None
    status: EmailStatus
    analysis_result_id: Optional[str] = None
    received_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
