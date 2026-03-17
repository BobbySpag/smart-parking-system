"""OccupancyLog SQLAlchemy model."""
import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import timezone
from ..database import Base


class OccupancyLog(Base):
    """Records a detection event for a parking space."""

    __tablename__ = "occupancy_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    space_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("parking_spaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    is_occupied: Mapped[bool] = mapped_column(Boolean, nullable=False)
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), index=True
    )
    detection_method: Mapped[str | None] = mapped_column(String(100), nullable=True)

    space: Mapped["ParkingSpace"] = relationship(  # type: ignore[name-defined]
        "ParkingSpace", back_populates="occupancy_logs"
    )

    def __repr__(self) -> str:
        return (
            f"<OccupancyLog id={self.id} space_id={self.space_id} "
            f"occupied={self.is_occupied} ts={self.timestamp}>"
        )
