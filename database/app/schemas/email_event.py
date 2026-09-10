from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.enums import EmailStatus


class EmailEventBase(BaseModel):
    from_status: Optional[EmailStatus] = None
    to_status: EmailStatus
    event_type: str = "STATUS_CHANGE"
    details: Optional[str] = None


class EmailEventCreate(EmailEventBase):
    email_id: str
    timestamp: Optional[datetime] = None


class EmailEventResponse(EmailEventBase):
    id: str
    email_id: str
    timestamp: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
