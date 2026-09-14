from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from geoalchemy2.elements import WKTElement
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.models.blood_bank import BloodBank
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.blood_bank import (
    BloodBankProfileCreate,
    BloodBankProfileResponse,
    BloodBankProfileUpdate,
)


router = APIRouter(
    prefix="/blood-banks",
    tags=["Blood Banks"],
)


def blood_bank_response(
    blood_bank: BloodBank,
    db: Session,
) -> dict:
    """
    Convert the BloodBank database object into the API response.

    Latitude and longitude are stored together in the
    PostGIS location column.
    """

    latitude = None
    longitude = None

    if blood_bank.location is not None:
        location_text = db.execute(
            select(func.ST_AsText(BloodBank.location))
            .where(BloodBank.id == blood_bank.id)
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
        "id": blood_bank.id,
        "user_id": blood_bank.user_id,
        "name": blood_bank.name,
        "address": blood_bank.address,
        "latitude": latitude,
        "longitude": longitude,
        "verification_status": blood_bank.verification_status,
        "created_at": blood_bank.created_at,
        "updated_at": blood_bank.updated_at,
    }


@router.post(
    "/profile",
    response_model=BloodBankProfileResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_blood_bank_profile(
    data: BloodBankProfileCreate,
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

    if user.role != UserRole.BLOOD_BANK:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only blood bank users can create a blood bank profile",
        )

    existing_blood_bank = (
        db.query(BloodBank)
        .filter(BloodBank.user_id == current_user_id)
        .first()
    )

    if existing_blood_bank:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Blood bank profile already exists",
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

    blood_bank = BloodBank(
        user_id=current_user_id,
        name=data.name,
        address=data.address,
        location=location,
        verification_status=False,
        created_at=now,
        updated_at=now,
    )

    db.add(blood_bank)
    db.commit()
    db.refresh(blood_bank)

    return blood_bank_response(blood_bank, db)


@router.get(
    "/profile",
    response_model=BloodBankProfileResponse,
)
def get_blood_bank_profile(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    blood_bank = (
        db.query(BloodBank)
        .filter(BloodBank.user_id == current_user_id)
        .first()
    )

    if not blood_bank:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blood bank profile not found",
        )

    return blood_bank_response(blood_bank, db)


@router.patch(
    "/profile",
    response_model=BloodBankProfileResponse,
)
def update_blood_bank_profile(
    data: BloodBankProfileUpdate,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    blood_bank = (
        db.query(BloodBank)
        .filter(BloodBank.user_id == current_user_id)
        .first()
    )

    if not blood_bank:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blood bank profile not found",
        )

    update_data = data.model_dump(
        exclude_unset=True
    )

    if "name" in update_data:
        blood_bank.name = update_data["name"]

    if "address" in update_data:
        blood_bank.address = update_data["address"]

    if (
        "latitude" in update_data
        or "longitude" in update_data
    ):
        latitude = update_data.get("latitude")
        longitude = update_data.get("longitude")

        if latitude is None or longitude is None:
            existing_location = db.execute(
                select(func.ST_AsText(BloodBank.location))
                .where(BloodBank.id == blood_bank.id)
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
            blood_bank.location = WKTElement(
                f"POINT({longitude} {latitude})",
                srid=4326,
            )

    blood_bank.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(blood_bank)

    return blood_bank_response(blood_bank, db)