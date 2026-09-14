from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import BloodGroup


class DonorProfileCreate(BaseModel):
    blood_group: BloodGroup
    date_of_birth: date | None = None

    latitude: float | None = Field(
        default=None,
        ge=-90,
        le=90,
    )

    longitude: float | None = Field(
        default=None,
        ge=-180,
        le=180,
    )

    address: str | None = None

    is_available: bool = True

    last_donation_date: date | None = None


class DonorProfileUpdate(BaseModel):
    blood_group: BloodGroup | None = None
    date_of_birth: date | None = None

    latitude: float | None = Field(
        default=None,
        ge=-90,
        le=90,
    )

    longitude: float | None = Field(
        default=None,
        ge=-180,
        le=180,
    )

    address: str | None = None

    is_available: bool | None = None

    last_donation_date: date | None = None


class DonorProfileResponse(BaseModel):
    id: int
    user_id: int
    blood_group: BloodGroup
    date_of_birth: date | None
    latitude: float | None
    longitude: float | None
    address: str | None
    is_available: bool
    last_donation_date: date | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)