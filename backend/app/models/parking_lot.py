"""ParkingLot and ParkingSpace SQLAlchemy models."""
import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Float, Integer, ForeignKey, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import timezone
from ..database import Base


class ParkingLot(Base):
    """Represents a physical parking lot."""

    __tablename__ = "parking_lots"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str] = mapped_column(String(500), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    total_spaces: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    spaces: Mapped[list["ParkingSpace"]] = relationship(
        "ParkingSpace", back_populates="lot", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<ParkingLot id={self.id} name={self.name}>"


class ParkingSpace(Base):
    """Represents an individual parking space within a lot."""

    __tablename__ = "parking_spaces"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    lot_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("parking_lots.id", ondelete="CASCADE"), nullable=False, index=True
    )
    space_number: Mapped[str] = mapped_column(String(50), nullable=False)
    is_occupied: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    coordinates_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    lot: Mapped["ParkingLot"] = relationship("ParkingLot", back_populates="spaces")
    occupancy_logs: Mapped[list["OccupancyLog"]] = relationship(  # type: ignore[name-defined]
        "OccupancyLog", back_populates="space", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<ParkingSpace id={self.id} number={self.space_number} occupied={self.is_occupied}>"
