from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, DateTime, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import ENUM as PGEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import DonorMatchStatus


class DonorMatch(Base):
    __tablename__ = "donor_matches"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
    )

    request_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("blood_requests.id"),
        nullable=False,
    )

    donor_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("donors.id"),
        nullable=False,
    )

    distance_km: Mapped[Decimal | None] = mapped_column(
        Numeric,
        nullable=True,
    )

    compatibility_score: Mapped[Decimal] = mapped_column(
        Numeric,
        nullable=False,
    )

    availability_score: Mapped[Decimal] = mapped_column(
        Numeric,
        nullable=False,
    )

    urgency_score: Mapped[Decimal] = mapped_column(
        Numeric,
        nullable=False,
    )

    total_score: Mapped[Decimal] = mapped_column(
        Numeric,
        nullable=False,
    )

    status: Mapped[DonorMatchStatus] = mapped_column(
        PGEnum(
            DonorMatchStatus,
            name="donor_match_status",
            create_type=False,
        ),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    request = relationship(
        "BloodRequest",
        back_populates="matches",
    )

    donor = relationship(
        "Donor",
        back_populates="matches",
    )