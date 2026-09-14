from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import BloodGroup


class BloodInventoryCreate(BaseModel):
    blood_group: BloodGroup

    available_units: int = Field(
        ge=0,
    )

    reserved_units: int = Field(
        default=0,
        ge=0,
    )


class BloodInventoryUpdate(BaseModel):
    available_units: int | None = Field(
        default=None,
        ge=0,
    )

    reserved_units: int | None = Field(
        default=None,
        ge=0,
    )


class BloodInventoryResponse(BaseModel):
    id: int
    blood_bank_id: int
    blood_group: BloodGroup
    available_units: int
    reserved_units: int
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )