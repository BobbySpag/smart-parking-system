"""Detection integration service for processing CV detection results."""
import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from ..models.parking_lot import ParkingLot, ParkingSpace
from ..models.occupancy import OccupancyLog
from ..schemas.parking import SpaceStatusUpdate


async def process_detection_result(
    db: AsyncSession,
    space_id: uuid.UUID,
    is_occupied: bool,
    confidence_score: float | None = None,
    detection_method: str = "cnn",
) -> OccupancyLog:
    """Persist a single detection result and update the parking space status.

    Args:
        db: Async database session.
        space_id: UUID of the space being updated.
        is_occupied: Detection result.
        confidence_score: Model confidence (0-1).
        detection_method: Label describing the detection source.

    Returns:
        The newly created OccupancyLog entry.
    """
    result = await db.execute(select(ParkingSpace).where(ParkingSpace.id == space_id))
    space = result.scalar_one_or_none()
    if space is None:
        raise ValueError(f"ParkingSpace {space_id} not found")

    space.is_occupied = is_occupied
    space.updated_at = datetime.now(timezone.utc)

    log = OccupancyLog(
        space_id=space_id,
        is_occupied=is_occupied,
        confidence_score=confidence_score,
        detection_method=detection_method,
        timestamp=datetime.now(timezone.utc),
    )
    db.add(log)
    await db.flush()
    await db.refresh(log)
    return log


async def get_lot_occupancy_summary(db: AsyncSession, lot_id: uuid.UUID) -> dict:
    """Return an occupancy summary dictionary for a parking lot.

    Returns:
        Dict with keys: lot_id, total, occupied, available, occupancy_rate.
    """
    lot_result = await db.execute(select(ParkingLot).where(ParkingLot.id == lot_id))
    lot = lot_result.scalar_one_or_none()
    if lot is None:
        raise ValueError(f"ParkingLot {lot_id} not found")

    total_result = await db.execute(
        select(func.count(ParkingSpace.id)).where(ParkingSpace.lot_id == lot_id)
    )
    total = total_result.scalar() or 0

    occupied_result = await db.execute(
        select(func.count(ParkingSpace.id)).where(
            ParkingSpace.lot_id == lot_id, ParkingSpace.is_occupied
        )
    )
    occupied = occupied_result.scalar() or 0
    available = max(0, total - occupied)
    rate = round(occupied / total, 4) if total > 0 else 0.0

    return {
        "lot_id": str(lot_id),
        "lot_name": lot.name,
        "total": total,
        "occupied": occupied,
        "available": available,
        "occupancy_rate": rate,
    }


async def batch_update_spaces(
    db: AsyncSession,
    updates: list[dict],
    detection_method: str = "batch_cnn",
) -> list[OccupancyLog]:
    """Apply a batch of detection results at once.

    Each entry in *updates* must be a dict with keys:
    ``space_id`` (str/UUID), ``is_occupied`` (bool), and optionally
    ``confidence_score`` (float).

    Returns:
        List of created OccupancyLog objects.
    """
    logs: list[OccupancyLog] = []
    for entry in updates:
        space_id = uuid.UUID(str(entry["space_id"]))
        log = await process_detection_result(
            db=db,
            space_id=space_id,
            is_occupied=bool(entry["is_occupied"]),
            confidence_score=entry.get("confidence_score"),
            detection_method=detection_method,
        )
        logs.append(log)
    return logs
