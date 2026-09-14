from datetime import datetime, timezone
from app.models.enums import BloodGroup, UserRole
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.models.blood_bank import BloodBank
from app.models.blood_inventory import BloodInventory
from app.models.user import User
from app.schemas.blood_inventory import (
    BloodInventoryCreate,
    BloodInventoryResponse,
    BloodInventoryUpdate,
)


router = APIRouter(
    prefix="/blood-banks/inventory",
    tags=["Blood Inventory"],
)


def get_current_blood_bank(
    current_user_id: int,
    db: Session,
) -> BloodBank:

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
            detail="Only blood bank users can manage inventory",
        )

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

    return blood_bank


@router.post(
    "",
    response_model=BloodInventoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_inventory(
    data: BloodInventoryCreate,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    blood_bank = get_current_blood_bank(
        current_user_id,
        db,
    )

    existing_inventory = (
        db.query(BloodInventory)
        .filter(
            BloodInventory.blood_bank_id == blood_bank.id,
            BloodInventory.blood_group == data.blood_group,
        )
        .first()
    )

    if existing_inventory:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inventory for this blood group already exists",
        )

    if data.reserved_units > data.available_units:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reserved units cannot exceed available units",
        )

    inventory = BloodInventory(
        blood_bank_id=blood_bank.id,
        blood_group=data.blood_group,
        available_units=data.available_units,
        reserved_units=data.reserved_units,
        updated_at=datetime.now(timezone.utc),
    )

    db.add(inventory)
    db.commit()
    db.refresh(inventory)

    return inventory


@router.get(
    "",
    response_model=list[BloodInventoryResponse],
)
def get_inventory(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    blood_bank = get_current_blood_bank(
        current_user_id,
        db,
    )

    inventory = (
        db.query(BloodInventory)
        .filter(
            BloodInventory.blood_bank_id == blood_bank.id
        )
        .order_by(BloodInventory.blood_group)
        .all()
    )

    return inventory


@router.patch(
    "/{blood_group}",
    response_model=BloodInventoryResponse,
)
def update_inventory(
    blood_group: BloodGroup,
    data: BloodInventoryUpdate,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    blood_bank = get_current_blood_bank(
        current_user_id,
        db,
    )

    inventory = (
        db.query(BloodInventory)
        .filter(
            BloodInventory.blood_bank_id == blood_bank.id,
            BloodInventory.blood_group == blood_group,
        )
        .first()
    )

    if not inventory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blood inventory entry not found",
        )

    update_data = data.model_dump(
        exclude_unset=True
    )

    new_available_units = update_data.get(
        "available_units",
        inventory.available_units,
    )

    new_reserved_units = update_data.get(
        "reserved_units",
        inventory.reserved_units,
    )

    if new_reserved_units > new_available_units:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reserved units cannot exceed available units",
        )

    if "available_units" in update_data:
        inventory.available_units = (
            update_data["available_units"]
        )

    if "reserved_units" in update_data:
        inventory.reserved_units = (
            update_data["reserved_units"]
        )

    inventory.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(inventory)

    return inventory