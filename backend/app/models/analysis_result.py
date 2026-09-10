import uuid
from typing import TYPE_CHECKING, Optional
from datetime import datetime, timezone
from sqlalchemy import String, Text, Float, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.enums import Verdict

if TYPE_CHECKING:
    from app.models.email import Email


class AnalysisResult(Base):
    """
    SQLAlchemy ORM model for analysis_results table.
    Stores threat detection outcomes, risk scores, verdicts, detection reasons, and evidence payloads.
    """
    __tablename__ = "analysis_results"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    email_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("emails.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    risk_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
        index=True,
        comment="Numeric risk score (e.g. 0.0 to 1.0 or 0 to 100)",
    )
    verdict: Mapped[Verdict] = mapped_column(
        SQLEnum(Verdict, native_enum=False),
        default=Verdict.UNKNOWN,
        nullable=False,
        index=True,
    )
    detection_reasons: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="JSON list or text summary of detection signals and evidence rationale",
    )
    analysis_duration_ms: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Analysis pipeline execution duration in milliseconds",
    )
    details_json: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Flexible JSON storage for full module outputs (AI, headers, URLs, attachments, etc.)",
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
    email: Mapped["Email"] = relationship(
        "Email",
        back_populates="analysis_result",
    )

    def __repr__(self) -> str:
        verdict_str = self.verdict.value if hasattr(self.verdict, "value") else self.verdict
        return f"<AnalysisResult(id={self.id!r}, email_id={self.email_id!r}, score={self.risk_score}, verdict={verdict_str!r})>"
