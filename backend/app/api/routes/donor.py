from fastapi import APIRouter, Depends, HTTPException, status
from geoalchemy2.elements import WKTElement
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.models.donor import Donor
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.donor import (
    DonorProfileCreate,
    DonorProfileResponse,
    DonorProfileUpdate,
)


router = APIRouter(
    prefix="/donors",
    tags=["Donors"],
)


def donor_response(
    donor: Donor,
    db: Session,
) -> dict:
    """
    Convert the Donor database object into the API response.

    Latitude and longitude are stored together in the PostGIS
    location column, so we extract them separately for the API.
    """

    latitude = None
    longitude = None

    if donor.location is not None:
        location_text = db.execute(
            select(func.ST_AsText(Donor.location))
            .where(Donor.id == donor.id)
        ).scalar_one_or_none()

        if location_text:
            # Expected format:
            # POINT(longitude latitude)
            coordinates = location_text.replace(
                "POINT(",
                ""
            ).replace(
                ")",
                ""
            ).split()

            if len(coordinates) == 2:
                longitude = float(coordinates[0])
                latitude = float(coordinates[1])

    return {
        "id": donor.id,
        "user_id": donor.user_id,
        "blood_group": donor.blood_group,
        "date_of_birth": donor.date_of_birth,
        "latitude": latitude,
        "longitude": longitude,
        "address": donor.address,
        "is_available": donor.is_available,
        "last_donation_date": donor.last_donation_date,
        "created_at": donor.created_at,
        "updated_at": donor.updated_at,
    }


@router.post(
    "/profile",
    response_model=DonorProfileResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_donor_profile(
    data: DonorProfileCreate,
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

    if user.role != UserRole.DONOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only donor users can create a donor profile",
        )

    existing_donor = (
        db.query(Donor)
        .filter(Donor.user_id == current_user_id)
        .first()
    )

    if existing_donor:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Donor profile already exists",
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

    donor = Donor(
        user_id=current_user_id,
        blood_group=data.blood_group,
        date_of_birth=data.date_of_birth,
        location=location,
        address=data.address,
        is_available=data.is_available,
        last_donation_date=data.last_donation_date,
    )

    db.add(donor)
    db.commit()
    db.refresh(donor)

    return donor_response(donor, db)


@router.get(
    "/profile",
    response_model=DonorProfileResponse,
)
def get_donor_profile(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    donor = (
        db.query(Donor)
        .filter(Donor.user_id == current_user_id)
        .first()
    )

    if not donor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Donor profile not found",
        )

    return donor_response(donor, db)


@router.patch(
    "/profile",
    response_model=DonorProfileResponse,
)
def update_donor_profile(
    data: DonorProfileUpdate,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    donor = (
        db.query(Donor)
        .filter(Donor.user_id == current_user_id)
        .first()
    )

    if not donor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Donor profile not found",
        )

    update_data = data.model_dump(
        exclude_unset=True
    )

    if "blood_group" in update_data:
        donor.blood_group = update_data["blood_group"]

    if "date_of_birth" in update_data:
        donor.date_of_birth = update_data["date_of_birth"]

    if "address" in update_data:
        donor.address = update_data["address"]

    if "is_available" in update_data:
        donor.is_available = update_data["is_available"]

    if "last_donation_date" in update_data:
        donor.last_donation_date = update_data[
            "last_donation_date"
        ]

    if (
        "latitude" in update_data
        or "longitude" in update_data
    ):
        latitude = update_data.get("latitude")
        longitude = update_data.get("longitude")

        # If only one coordinate was supplied, preserve
        # the existing coordinate.
        if latitude is None or longitude is None:
            existing_location = db.execute(
                select(func.ST_AsText(Donor.location))
                .where(Donor.id == donor.id)
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
            donor.location = WKTElement(
                f"POINT({longitude} {latitude})",
                srid=4326,
            )

    db.commit()
    db.refresh(donor)

    return donor_response(donor, db)