from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from geoalchemy2.elements import WKTElement
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.models.blood_request import BloodRequest
from app.models.enums import RequestStatus, UserRole
from app.models.user import User
from app.schemas.blood_request import (
    BloodRequestCreate,
    BloodRequestResponse,
    BloodRequestUpdate,
)


router = APIRouter(
    prefix="/blood-requests",
    tags=["Blood Requests"],
)


def blood_request_response(
    blood_request: BloodRequest,
    db: Session,
) -> dict:
    latitude = None
    longitude = None

    if blood_request.location is not None:
        location_text = db.execute(
            select(func.ST_AsText(BloodRequest.location))
            .where(BloodRequest.id == blood_request.id)
        ).scalar_one_or_none()

        if location_text:
            coordinates = (
                location_text
                .replace("POINT(", "")
                .replace(")", "")
                .split()
            )

            if len(coordinates) == 2:
                longitude = float(coordinates[0])
                latitude = float(coordinates[1])

    return {
        "id": blood_request.id,
        "requester_id": blood_request.requester_id,
        "hospital_id": blood_request.hospital_id,
        "blood_group": blood_request.blood_group,
        "units_required": blood_request.units_required,
        "units_fulfilled": blood_request.units_fulfilled,
        "urgency": blood_request.urgency,
        "status": blood_request.status,
        "latitude": latitude,
        "longitude": longitude,
        "address": blood_request.address,
        "required_by": blood_request.required_by,
        "created_at": blood_request.created_at,
        "updated_at": blood_request.updated_at,
    }


@router.post(
    "",
    response_model=BloodRequestResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_blood_request(
    data: BloodRequestCreate,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.id == current_user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user.role not in {
        UserRole.REQUESTER,
        UserRole.HOSPITAL,
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only requester or hospital users can create blood requests",
        )

    if data.units_required <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Units required must be greater than zero",
        )

    location = None

    if (
        data.latitude is not None
        and data.longitude is not None
    ):
        location = WKTElement(
            f"POINT({data.longitude} {data.latitude})",
            srid=4326,
        )

    now = datetime.now(timezone.utc)

    blood_request = BloodRequest(
        requester_id=current_user_id,
        hospital_id=data.hospital_id,
        blood_group=data.blood_group,
        units_required=data.units_required,
        units_fulfilled=0,
        urgency=data.urgency,
        status=RequestStatus.REQUESTED,
        location=location,
        address=data.address,
        required_by=data.required_by,
        created_at=now,
        updated_at=now,
    )

    db.add(blood_request)
    db.commit()
    db.refresh(blood_request)

    return blood_request_response(blood_request, db)


@router.get(
    "",
    response_model=list[BloodRequestResponse],
)
def get_blood_requests(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    requests = (
        db.query(BloodRequest)
        .filter(BloodRequest.requester_id == current_user_id)
        .order_by(BloodRequest.created_at.desc())
        .all()
    )

    return [
        blood_request_response(request, db)
        for request in requests
    ]


@router.get(
    "/{request_id}",
    response_model=BloodRequestResponse,
)
def get_blood_request(
    request_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    blood_request = (
        db.query(BloodRequest)
        .filter(
            BloodRequest.id == request_id,
            BloodRequest.requester_id == current_user_id,
        )
        .first()
    )

    if not blood_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blood request not found",
        )

    return blood_request_response(blood_request, db)


@router.patch(
    "/{request_id}",
    response_model=BloodRequestResponse,
)
def update_blood_request(
    request_id: int,
    data: BloodRequestUpdate,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    blood_request = (
        db.query(BloodRequest)
        .filter(
            BloodRequest.id == request_id,
            BloodRequest.requester_id == current_user_id,
        )
        .first()
    )

    if not blood_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blood request not found",
        )

    update_data = data.model_dump(
        exclude_unset=True
    )

    if "units_fulfilled" in update_data:
        units_fulfilled = update_data["units_fulfilled"]

        if units_fulfilled < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Units fulfilled cannot be negative",
            )

        if units_fulfilled > blood_request.units_required:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Units fulfilled cannot exceed units required",
            )

        blood_request.units_fulfilled = units_fulfilled

    if "urgency" in update_data:
        blood_request.urgency = update_data["urgency"]

    if "status" in update_data:
        blood_request.status = update_data["status"]

    if "address" in update_data:
        blood_request.address = update_data["address"]

    if "required_by" in update_data:
        blood_request.required_by = update_data["required_by"]

    if (
        "latitude" in update_data
        or "longitude" in update_data
    ):
        latitude = update_data.get("latitude")
        longitude = update_data.get("longitude")

        if latitude is not None and longitude is not None:
            blood_request.location = WKTElement(
                f"POINT({longitude} {latitude})",
                srid=4326,
            )

    blood_request.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(blood_request)

    return blood_request_response(blood_request, db)