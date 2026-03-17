"""Parking business logic."""
import uuid
from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from ..models.parking_lot import ParkingLot, ParkingSpace
from ..models.occupancy import OccupancyLog
from ..schemas.parking import (
    ParkingLotCreate,
    ParkingLotUpdate,
    ParkingLotResponse,
    SpaceStatusUpdate,
)


async def get_all_lots(db: AsyncSession) -> list[ParkingLotResponse]:
    """Return all active parking lots with computed occupancy counts."""
    result = await db.execute(
        select(ParkingLot)
        .where(ParkingLot.is_active == True)
        .order_by(ParkingLot.name)
    )
    lots = result.scalars().all()
    responses: list[ParkingLotResponse] = []
    for lot in lots:
        occupied = await _count_occupied(db, lot.id)
        resp = ParkingLotResponse.model_validate(lot)
        resp.occupied_spaces = occupied
        resp.available_spaces = max(0, lot.total_spaces - occupied)
        responses.append(resp)
    return responses


async def get_lot_with_spaces(db: AsyncSession, lot_id: uuid.UUID) -> ParkingLotResponse:
    """Return a single parking lot with occupancy counts, or raise 404."""
    result = await db.execute(select(ParkingLot).where(ParkingLot.id == lot_id))
    lot = result.scalar_one_or_none()
    if lot is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parking lot not found")
    occupied = await _count_occupied(db, lot.id)
    resp = ParkingLotResponse.model_validate(lot)
    resp.occupied_spaces = occupied
    resp.available_spaces = max(0, lot.total_spaces - occupied)
    return resp


async def get_lot_spaces(db: AsyncSession, lot_id: uuid.UUID) -> list[ParkingSpace]:
    """Return all spaces belonging to a lot, or raise 404 if lot not found."""
    lot_result = await db.execute(select(ParkingLot).where(ParkingLot.id == lot_id))
    if lot_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parking lot not found")
    result = await db.execute(
        select(ParkingSpace)
        .where(ParkingSpace.lot_id == lot_id)
        .order_by(ParkingSpace.space_number)
    )
    return list(result.scalars().all())


async def update_space_status(
    db: AsyncSession, space_id: uuid.UUID, update: SpaceStatusUpdate
) -> ParkingSpace:
    """Update the occupancy status of a parking space and log the event."""
    result = await db.execute(select(ParkingSpace).where(ParkingSpace.id == space_id))
    space = result.scalar_one_or_none()
    if space is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parking space not found")
    space.is_occupied = update.is_occupied
    space.updated_at = datetime.now(timezone.utc)
    log = OccupancyLog(
        space_id=space_id,
        is_occupied=update.is_occupied,
        confidence_score=update.confidence_score,
        detection_method=update.detection_method,
    )
    db.add(log)
    await db.flush()
    await db.refresh(space)
    return space


async def create_lot(db: AsyncSession, data: ParkingLotCreate) -> ParkingLot:
    """Create a new parking lot and return it."""
    lot = ParkingLot(**data.model_dump())
    db.add(lot)
    await db.flush()
    await db.refresh(lot)
    return lot


async def update_lot(
    db: AsyncSession, lot_id: uuid.UUID, data: ParkingLotUpdate
) -> ParkingLot:
    """Apply a partial update to a parking lot and return it."""
    result = await db.execute(select(ParkingLot).where(ParkingLot.id == lot_id))
    lot = result.scalar_one_or_none()
    if lot is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parking lot not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(lot, field, value)
    await db.flush()
    await db.refresh(lot)
    return lot


async def _count_occupied(db: AsyncSession, lot_id: uuid.UUID) -> int:
    """Count occupied spaces in a lot."""
    result = await db.execute(
        select(func.count(ParkingSpace.id)).where(
            ParkingSpace.lot_id == lot_id,
            ParkingSpace.is_occupied == True,
        )
    )
    return result.scalar() or 0
