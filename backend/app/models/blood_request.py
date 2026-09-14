from datetime import datetime

from geoalchemy2 import Geography
from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import ENUM as PGEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import BloodGroup, RequestStatus, UrgencyLevel


class BloodRequest(Base):
    __tablename__ = "blood_requests"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
    )

    requester_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id"),
        nullable=False,
    )

    hospital_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("hospitals.id"),
        nullable=True,
    )

    blood_group: Mapped[BloodGroup] = mapped_column(
        PGEnum(
            BloodGroup,
            name="blood_group",
            create_type=False,
        ),
        nullable=False,
    )

    units_required: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    units_fulfilled: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    urgency: Mapped[UrgencyLevel] = mapped_column(
        PGEnum(
            UrgencyLevel,
            name="urgency_level",
            create_type=False,
        ),
        nullable=False,
    )

    status: Mapped[RequestStatus] = mapped_column(
        PGEnum(
            RequestStatus,
            name="request_status",
            create_type=False,
        ),
        nullable=False,
    )

    location = mapped_column(
        Geography(
            geometry_type="POINT",
            srid=4326,
        ),
        nullable=True,
    )

    address: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    required_by: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    requester = relationship(
        "User",
        back_populates="blood_requests",
    )

    hospital = relationship(
        "Hospital",
        back_populates="blood_requests",
    )

    matches = relationship(
        "DonorMatch",
        back_populates="request",
    )

    donations = relationship(
        "Donation",
        back_populates="request",
    )

    notifications = relationship(
        "Notification",
        back_populates="request",
    )