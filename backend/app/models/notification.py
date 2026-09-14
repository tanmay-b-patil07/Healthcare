from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import ENUM as PGEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import NotificationStatus


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
    )

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id"),
        nullable=False,
    )

    request_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("blood_requests.id"),
        nullable=True,
    )

    type: Mapped[str] = mapped_column(
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        nullable=False,
    )

    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    channel: Mapped[str] = mapped_column(
        nullable=False,
    )

    status: Mapped[NotificationStatus] = mapped_column(
        PGEnum(
            NotificationStatus,
            name="notification_status",
            create_type=False,
        ),
        nullable=False,
    )

    sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    user = relationship(
        "User",
        back_populates="notifications",
    )

    request = relationship(
        "BloodRequest",
        back_populates="notifications",
    )