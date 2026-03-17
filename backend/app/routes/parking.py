"""Parking routes: lots, spaces, status updates."""
import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from ..models.user import User, UserRole
from ..schemas.parking import (
    ParkingLotResponse,
    ParkingSpaceResponse,
    SpaceStatusUpdate,
)
from ..services import parking_service
from ..services.auth_service import get_current_user, require_roles

router = APIRouter(prefix="/api/parking", tags=["parking"])


@router.get("/lots", response_model=list[ParkingLotResponse])
async def list_lots(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[ParkingLotResponse]:
    """List all active parking lots with occupancy counts."""
    return await parking_service.get_all_lots(db)


@router.get("/lots/{lot_id}", response_model=ParkingLotResponse)
async def get_lot(
    lot_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> ParkingLotResponse:
    """Get details for a specific parking lot including occupancy counts."""
    return await parking_service.get_lot_with_spaces(db, lot_id)


@router.get("/lots/{lot_id}/spaces", response_model=list[ParkingSpaceResponse])
async def list_spaces(
    lot_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[ParkingSpaceResponse]:
    """List all parking spaces within a specific lot."""
    spaces = await parking_service.get_lot_spaces(db, lot_id)
    return [ParkingSpaceResponse.model_validate(s) for s in spaces]


@router.put("/spaces/{space_id}/status", response_model=ParkingSpaceResponse)
async def update_space_status(
    space_id: uuid.UUID,
    update: SpaceStatusUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_roles(UserRole.staff, UserRole.admin)),
) -> ParkingSpaceResponse:
    """Update the occupancy status of a parking space (staff/admin only)."""
    space = await parking_service.update_space_status(db, space_id, update)
    return ParkingSpaceResponse.model_validate(space)
