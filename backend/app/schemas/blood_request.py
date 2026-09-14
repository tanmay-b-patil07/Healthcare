from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import BloodGroup, RequestStatus, UrgencyLevel


class BloodRequestCreate(BaseModel):
    blood_group: BloodGroup
    units_required: int
    urgency: UrgencyLevel

    hospital_id: int | None = None

    latitude: float | None = None
    longitude: float | None = None

    address: str | None = None
    required_by: datetime | None = None


class BloodRequestUpdate(BaseModel):
    units_fulfilled: int | None = None
    urgency: UrgencyLevel | None = None
    status: RequestStatus | None = None

    latitude: float | None = None
    longitude: float | None = None

    address: str | None = None
    required_by: datetime | None = None


class BloodRequestResponse(BaseModel):
    id: int
    requester_id: int
    hospital_id: int | None

    blood_group: BloodGroup
    units_required: int
    units_fulfilled: int

    urgency: UrgencyLevel
    status: RequestStatus

    latitude: float | None
    longitude: float | None
    address: str | None

    required_by: datetime | None

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)