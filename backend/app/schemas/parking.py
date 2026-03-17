"""Pydantic schemas for Parking resources."""
import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class ParkingLotCreate(BaseModel):
    """Schema for creating a parking lot."""
    name: str = Field(..., min_length=1, max_length=255)
    address: str = Field(..., min_length=1, max_length=500)
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    total_spaces: int = Field(..., ge=1)


class ParkingLotUpdate(BaseModel):
    """Schema for updating an existing parking lot."""
    name: str | None = Field(None, min_length=1, max_length=255)
    address: str | None = Field(None, min_length=1, max_length=500)
    latitude: float | None = Field(None, ge=-90.0, le=90.0)
    longitude: float | None = Field(None, ge=-180.0, le=180.0)
    total_spaces: int | None = Field(None, ge=1)
    is_active: bool | None = None


class ParkingLotResponse(BaseModel):
    """Schema returned for a parking lot."""
    id: uuid.UUID
    name: str
    address: str
    latitude: float
    longitude: float
    total_spaces: int
    is_active: bool
    created_at: datetime
    occupied_spaces: int = 0
    available_spaces: int = 0

    model_config = {"from_attributes": True}


class ParkingSpaceResponse(BaseModel):
    """Schema returned for a parking space."""
    id: uuid.UUID
    lot_id: uuid.UUID
    space_number: str
    is_occupied: bool
    coordinates_json: str | None
    updated_at: datetime

    model_config = {"from_attributes": True}


class SpaceStatusUpdate(BaseModel):
    """Schema for updating a space occupancy status."""
    is_occupied: bool
    confidence_score: float | None = Field(None, ge=0.0, le=1.0)
    detection_method: str | None = Field(None, max_length=100)


class OccupancyLogResponse(BaseModel):
    """Schema returned for an occupancy log entry."""
    id: uuid.UUID
    space_id: uuid.UUID
    is_occupied: bool
    confidence_score: float | None
    timestamp: datetime
    detection_method: str | None

    model_config = {"from_attributes": True}
