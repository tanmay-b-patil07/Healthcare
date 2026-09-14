from datetime import datetime

from pydantic import BaseModel

from app.models.enums import DonorMatchStatus


class DonorMatchResponse(BaseModel):
    id: int
    request_id: int
    donor_id: int

    distance_km: float | None
    compatibility_score: float
    availability_score: float
    urgency_score: float
    total_score: float

    status: DonorMatchStatus
    created_at: datetime

    class Config:
        from_attributes = True


class DonorMatchStatusUpdate(BaseModel):
    status: DonorMatchStatus