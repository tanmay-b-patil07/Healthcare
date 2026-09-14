from datetime import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Integer,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import ENUM as PGEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import BloodGroup


class BloodInventory(Base):
    __tablename__ = "blood_inventory"

    __table_args__ = (
        UniqueConstraint(
            "blood_bank_id",
            "blood_group",
            name="uq_blood_bank_blood_group",
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
    )

    blood_bank_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("blood_banks.id"),
        nullable=False,
    )

    blood_group: Mapped[BloodGroup] = mapped_column(
        PGEnum(
            BloodGroup,
            name="blood_group",
            create_type=False,
        ),
        nullable=False,
    )

    available_units: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    reserved_units: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    blood_bank = relationship(
        "BloodBank",
        back_populates="inventory",
    )