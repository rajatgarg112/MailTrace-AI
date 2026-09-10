import uuid
from typing import TYPE_CHECKING, Optional, List
from datetime import datetime, timezone
from sqlalchemy import String, Text, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.enums import EmailStatus, DEFAULT_EMAIL_STATUS

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.email_event import EmailEvent
    from app.models.analysis_result import AnalysisResult


class Email(Base):
    """
    SQLAlchemy ORM model for Emails table.
    """
    __tablename__ = "emails"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    message_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        index=True,
        nullable=True,
    )
    user_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    sender: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )
    recipients: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Comma-separated string of recipient email addresses",
    )
    subject: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )
    body: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    status: Mapped[EmailStatus] = mapped_column(
        SQLEnum(EmailStatus, native_enum=False),
        default=DEFAULT_EMAIL_STATUS,
        nullable=False,
        index=True,
    )
    received_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    user: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="emails",
    )
    events: Mapped[List["EmailEvent"]] = relationship(
        "EmailEvent",
        back_populates="email",
        cascade="all, delete-orphan",
        order_by="EmailEvent.timestamp.asc()",
    )
    analysis_result: Mapped[Optional["AnalysisResult"]] = relationship(
        "AnalysisResult",
        back_populates="email",
        uselist=False,
        cascade="all, delete-orphan",
    )

    @property
    def recipient_list(self) -> List[str]:
        if not self.recipients:
            return []
        return [r.strip() for r in self.recipients.split(",") if r.strip()]

    @recipient_list.setter
    def recipient_list(self, value: List[str]) -> None:
        self.recipients = ", ".join(value)

    @property
    def analysis_result_id(self) -> Optional[str]:
        return self.analysis_result.id if self.analysis_result else None

    def __repr__(self) -> str:
        return f"<Email(id={self.id!r}, sender={self.sender!r}, status={self.status.value!r})>"
