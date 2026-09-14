from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import ENUM as PGEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import BloodGroup


class Donation(Base):
    __tablename__ = "donations"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
    )

    donor_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("donors.id"),
        nullable=False,
    )

    request_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("blood_requests.id"),
        nullable=True,
    )

    blood_bank_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("blood_banks.id"),
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

    units: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    donated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    donor = relationship(
        "Donor",
        back_populates="donations",
    )

    request = relationship(
        "BloodRequest",
        back_populates="donations",
    )

    blood_bank = relationship(
        "BloodBank",
        back_populates="donations",
    )