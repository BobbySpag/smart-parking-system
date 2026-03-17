"""Admin routes: user management and parking lot administration."""
import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..database import get_db
from ..models.user import User, UserRole
from ..schemas.user import UserResponse
from ..schemas.parking import ParkingLotCreate, ParkingLotResponse, ParkingLotUpdate
from ..services import parking_service
from ..services.auth_service import require_roles

router = APIRouter(prefix="/api/admin", tags=["admin"])

_admin_only = Depends(require_roles(UserRole.admin))


@router.get("/users", response_model=list[UserResponse])
async def list_users(
    db: AsyncSession = Depends(get_db),
    _: User = _admin_only,
) -> list[UserResponse]:
    """Return all registered users (admin only)."""
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    users = result.scalars().all()
    return [UserResponse.model_validate(u) for u in users]


@router.post("/lots", response_model=ParkingLotResponse, status_code=201)
async def create_lot(
    data: ParkingLotCreate,
    db: AsyncSession = Depends(get_db),
    _: User = _admin_only,
) -> ParkingLotResponse:
    """Create a new parking lot (admin only)."""
    lot = await parking_service.create_lot(db, data)
    resp = ParkingLotResponse.model_validate(lot)
    resp.occupied_spaces = 0
    resp.available_spaces = lot.total_spaces
    return resp


@router.put("/lots/{lot_id}", response_model=ParkingLotResponse)
async def update_lot(
    lot_id: uuid.UUID,
    data: ParkingLotUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = _admin_only,
) -> ParkingLotResponse:
    """Update an existing parking lot (admin only)."""
    lot = await parking_service.update_lot(db, lot_id, data)
    resp = ParkingLotResponse.model_validate(lot)
    occupied = await parking_service._count_occupied(db, lot.id)
    resp.occupied_spaces = occupied
    resp.available_spaces = max(0, lot.total_spaces - occupied)
    return resp
