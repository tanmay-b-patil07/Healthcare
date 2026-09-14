from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from geoalchemy2.elements import WKTElement
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.models.hospital import Hospital
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.hospital import (
    HospitalProfileCreate,
    HospitalProfileResponse,
    HospitalProfileUpdate,
)


router = APIRouter(
    prefix="/hospitals",
    tags=["Hospitals"],
)


def hospital_response(
    hospital: Hospital,
    db: Session,
) -> dict:
    """
    Convert the Hospital database object into the API response.

    Latitude and longitude are stored together in the
    PostGIS location column.
    """

    latitude = None
    longitude = None

    if hospital.location is not None:
        location_text = db.execute(
            select(func.ST_AsText(Hospital.location))
            .where(Hospital.id == hospital.id)
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
        "id": hospital.id,
        "user_id": hospital.user_id,
        "name": hospital.name,
        "address": hospital.address,
        "latitude": latitude,
        "longitude": longitude,
        "verification_status": hospital.verification_status,
        "created_at": hospital.created_at,
        "updated_at": hospital.updated_at,
    }


@router.post(
    "/profile",
    response_model=HospitalProfileResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_hospital_profile(
    data: HospitalProfileCreate,
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

    if user.role != UserRole.HOSPITAL:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only hospital users can create a hospital profile",
        )

    existing_hospital = (
        db.query(Hospital)
        .filter(Hospital.user_id == current_user_id)
        .first()
    )

    if existing_hospital:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hospital profile already exists",
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

    hospital = Hospital(
        user_id=current_user_id,
        name=data.name,
        address=data.address,
        location=location,
        verification_status=False,
        created_at=now,
        updated_at=now,
    )

    db.add(hospital)
    db.commit()
    db.refresh(hospital)

    return hospital_response(hospital, db)


@router.get(
    "/profile",
    response_model=HospitalProfileResponse,
)
def get_hospital_profile(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    hospital = (
        db.query(Hospital)
        .filter(Hospital.user_id == current_user_id)
        .first()
    )

    if not hospital:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hospital profile not found",
        )

    return hospital_response(hospital, db)


@router.patch(
    "/profile",
    response_model=HospitalProfileResponse,
)
def update_hospital_profile(
    data: HospitalProfileUpdate,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    hospital = (
        db.query(Hospital)
        .filter(Hospital.user_id == current_user_id)
        .first()
    )

    if not hospital:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hospital profile not found",
        )

    update_data = data.model_dump(
        exclude_unset=True
    )

    if "name" in update_data:
        hospital.name = update_data["name"]

    if "address" in update_data:
        hospital.address = update_data["address"]

    if (
        "latitude" in update_data
        or "longitude" in update_data
    ):
        latitude = update_data.get("latitude")
        longitude = update_data.get("longitude")

        if latitude is None or longitude is None:
            existing_location = db.execute(
                select(func.ST_AsText(Hospital.location))
                .where(Hospital.id == hospital.id)
            ).scalar_one_or_none()

            if existing_location:
                coordinates = (
                    existing_location
                    .replace("POINT(", "")
                    .replace(")", "")
                    .split()
                )

                if len(coordinates) == 2:
                    existing_longitude = float(coordinates[0])
                    existing_latitude = float(coordinates[1])

                    if latitude is None:
                        latitude = existing_latitude

                    if longitude is None:
                        longitude = existing_longitude

        if (
            latitude is not None
            and longitude is not None
        ):
            hospital.location = WKTElement(
                f"POINT({longitude} {latitude})",
                srid=4326,
            )

    hospital.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(hospital)

    return hospital_response(hospital, db)