from datetime import datetime

from pydantic import BaseModel, ConfigDict


class BloodBankProfileCreate(BaseModel):
    name: str
    address: str
    latitude: float | None = None
    longitude: float | None = None


class BloodBankProfileUpdate(BaseModel):
    name: str | None = None
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None


class BloodBankProfileResponse(BaseModel):
    id: int
    user_id: int
    name: str
    address: str
    latitude: float | None = None
    longitude: float | None = None
    verification_status: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)