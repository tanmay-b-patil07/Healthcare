from datetime import datetime, timezone
from re import match

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.models.blood_request import BloodRequest
from app.models.donor import Donor
from app.models.donor_match import DonorMatch
from app.models.enums import (
    DonorMatchStatus,
    BloodGroup,
    RequestStatus,
    UrgencyLevel,
)
from app.models.user import User
from app.schemas.donar_match import (
    DonorMatchResponse,
    DonorMatchStatusUpdate,
)


router = APIRouter(
    prefix="/donor-matches",
    tags=["Donor Matches"],
)


# ---------------------------------------------------------
# BLOOD COMPATIBILITY
# ---------------------------------------------------------

COMPATIBLE_DONORS = {
    BloodGroup.A_POSITIVE: {
        BloodGroup.A_POSITIVE,
        BloodGroup.A_NEGATIVE,
        BloodGroup.O_POSITIVE,
        BloodGroup.O_NEGATIVE,
    },
    BloodGroup.A_NEGATIVE: {
        BloodGroup.A_NEGATIVE,
        BloodGroup.O_NEGATIVE,
    },
    BloodGroup.B_POSITIVE: {
        BloodGroup.B_POSITIVE,
        BloodGroup.B_NEGATIVE,
        BloodGroup.O_POSITIVE,
        BloodGroup.O_NEGATIVE,
    },
    BloodGroup.B_NEGATIVE: {
        BloodGroup.B_NEGATIVE,
        BloodGroup.O_NEGATIVE,
    },
    BloodGroup.AB_POSITIVE: {
        BloodGroup.A_POSITIVE,
        BloodGroup.A_NEGATIVE,
        BloodGroup.B_POSITIVE,
        BloodGroup.B_NEGATIVE,
        BloodGroup.AB_POSITIVE,
        BloodGroup.AB_NEGATIVE,
        BloodGroup.O_POSITIVE,
        BloodGroup.O_NEGATIVE,
    },
    BloodGroup.AB_NEGATIVE: {
        BloodGroup.A_NEGATIVE,
        BloodGroup.B_NEGATIVE,
        BloodGroup.AB_NEGATIVE,
        BloodGroup.O_NEGATIVE,
    },
    BloodGroup.O_POSITIVE: {
        BloodGroup.O_POSITIVE,
        BloodGroup.O_NEGATIVE,
    },
    BloodGroup.O_NEGATIVE: {
        BloodGroup.O_NEGATIVE,
    },
}


# ---------------------------------------------------------
# GENERATE MATCHES
# ---------------------------------------------------------

@router.post(
    "/{request_id}/generate",
    response_model=list[DonorMatchResponse],
)
def generate_matches(
    request_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    # Find blood request
    blood_request = (
        db.query(BloodRequest)
        .filter(BloodRequest.id == request_id)
        .first()
    )

    if not blood_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blood request not found",
        )

    # Check current user
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

    # Only requester or hospital can generate matches
    if (
        current_user_id != blood_request.requester_id
        and (
            blood_request.hospital_id is None
            or user.role.value != "HOSPITAL"
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the requester or hospital can generate donor matches",
        )

    compatible_groups = COMPATIBLE_DONORS[
        blood_request.blood_group
    ]

    donors = (
        db.query(Donor)
        .filter(
            Donor.is_available.is_(True),
            Donor.blood_group.in_(compatible_groups),
        )
        .all()
    )

    matches = []

    # Urgency score
    urgency_scores = {
        UrgencyLevel.CRITICAL: 100,
        UrgencyLevel.HIGH: 75,
        UrgencyLevel.MEDIUM: 50,
        UrgencyLevel.LOW: 25,
    }

    urgency_score = urgency_scores[
        blood_request.urgency
    ]

    for donor in donors:

        # Avoid duplicate match
        existing_match = (
            db.query(DonorMatch)
            .filter(
                DonorMatch.request_id == request_id,
                DonorMatch.donor_id == donor.id,
            )
            .first()
        )

        if existing_match:
            matches.append(existing_match)
            continue

        # -------------------------------------------------
        # DISTANCE
        # -------------------------------------------------

        distance_km = None

        if (
            donor.location is not None
            and blood_request.location is not None
        ):
            distance_meters = db.execute(
                select(
                    func.ST_Distance(
                        donor.location,
                        blood_request.location,
                    )
                )
            ).scalar_one_or_none()

            if distance_meters is not None:
                distance_km = float(distance_meters) / 1000

        # -------------------------------------------------
        # COMPATIBILITY
        # -------------------------------------------------

        compatibility_score = 100

        # -------------------------------------------------
        # AVAILABILITY
        # -------------------------------------------------

        availability_score = 100 if donor.is_available else 0

        # -------------------------------------------------
        # DISTANCE SCORE
        # -------------------------------------------------

        if distance_km is None:
            distance_score = 50
        else:
            distance_score = max(
                0,
                100 - (distance_km * 2),
            )

        # -------------------------------------------------
        # TOTAL SCORE
        # -------------------------------------------------

        total_score = (
            compatibility_score * 0.5
            + availability_score * 0.2
            + distance_score * 0.2
            + urgency_score * 0.1
        )

        match = DonorMatch(
            request_id=request_id,
            donor_id=donor.id,
            distance_km=distance_km,
            compatibility_score=compatibility_score,
            availability_score=availability_score,
            urgency_score=urgency_score,
            total_score=total_score,
            status=DonorMatchStatus.PENDING,
            created_at=datetime.now(timezone.utc),
        )

        db.add(match)
        matches.append(match)

    db.commit()

    for match in matches:
        db.refresh(match)

    matches.sort(
        key=lambda x: float(x.total_score),
        reverse=True,
    )

    return matches


# ---------------------------------------------------------
# GET MATCHES FOR REQUEST
# ---------------------------------------------------------

@router.get(
    "/{request_id}",
    response_model=list[DonorMatchResponse],
)
def get_matches(
    request_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    blood_request = (
        db.query(BloodRequest)
        .filter(BloodRequest.id == request_id)
        .first()
    )

    if not blood_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blood request not found",
        )

    matches = (
        db.query(DonorMatch)
        .filter(DonorMatch.request_id == request_id)
        .order_by(DonorMatch.total_score.desc())
        .all()
    )

    return matches


# ---------------------------------------------------------
# UPDATE MATCH STATUS
# ---------------------------------------------------------

@router.patch(
    "/{match_id}",
    response_model=DonorMatchResponse,
)
def update_match_status(
    match_id: int,
    data: DonorMatchStatusUpdate,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    match = (
        db.query(DonorMatch)
        .filter(DonorMatch.id == match_id)
        .first()
    )

    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Donor match not found",
        )

    donor = (
        db.query(Donor)
        .filter(Donor.id == match.donor_id)
        .first()
    )

    if not donor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Donor not found",
        )

    if donor.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the matched donor can update match status",
        )

    match.status = data.status

    # Get the associated blood request
    blood_request = (
        db.query(BloodRequest)
        .filter(BloodRequest.id == match.request_id)
        .first()
    )

    if not blood_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blood request not found",
        )

    # If donor accepts, update the blood request status
    if data.status == DonorMatchStatus.ACCEPTED:
        blood_request.status = RequestStatus.DONOR_RESPONDED

    blood_request.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(match)

    return match