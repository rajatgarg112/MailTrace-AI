import uuid
from typing import TYPE_CHECKING, Optional
from datetime import datetime, timezone
from sqlalchemy import String, Text, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.enums import EmailStatus

if TYPE_CHECKING:
    from app.models.email import Email


class EmailEvent(Base):
    """
    SQLAlchemy ORM model for email_events table.
    Tracks immutable historical lifecycle events and status transitions for emails.
    """
    __tablename__ = "email_events"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    email_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("emails.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    from_status: Mapped[Optional[EmailStatus]] = mapped_column(
        SQLEnum(EmailStatus, native_enum=False),
        nullable=True,
        index=True,
    )
    to_status: Mapped[EmailStatus] = mapped_column(
        SQLEnum(EmailStatus, native_enum=False),
        nullable=False,
        index=True,
    )
    event_type: Mapped[str] = mapped_column(
        String(100),
        default="STATUS_CHANGE",
        nullable=False,
        index=True,
    )
    details: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Optional human-readable or JSON details describing the event context",
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    email: Mapped["Email"] = relationship(
        "Email",
        back_populates="events",
    )

    def __repr__(self) -> str:
        from_str = self.from_status.value if hasattr(self.from_status, 'value') else self.from_status
        to_str = self.to_status.value if hasattr(self.to_status, 'value') else self.to_status
        return f"<EmailEvent(id={self.id!r}, email_id={self.email_id!r}, from={from_str!r}, to={to_str!r})>"

