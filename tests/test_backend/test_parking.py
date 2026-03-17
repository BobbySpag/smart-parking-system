"""Tests for parking endpoints."""
import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models.parking_lot import ParkingLot, ParkingSpace
from backend.app.models.user import User, UserRole
from backend.app.services.auth_service import create_access_token, hash_password


async def _create_lot(db: AsyncSession) -> ParkingLot:
    lot = ParkingLot(
        name="Test Lot",
        address="123 Test St",
        latitude=51.5,
        longitude=-0.1,
        total_spaces=10,
    )
    db.add(lot)
    await db.commit()
    await db.refresh(lot)
    return lot


async def _create_space(db: AsyncSession, lot_id: uuid.UUID) -> ParkingSpace:
    space = ParkingSpace(lot_id=lot_id, space_number="A1", is_occupied=False)
    db.add(space)
    await db.commit()
    await db.refresh(space)
    return space


async def _create_staff(db: AsyncSession) -> User:
    user = User(
        email="staff_parking@example.com",
        hashed_password=hash_password("StaffPass1"),
        full_name="Staff User",
        role=UserRole.staff,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest.mark.asyncio
async def test_list_lots_authenticated(client: AsyncClient, driver_auth_headers: dict, db: AsyncSession):
    await _create_lot(db)
    response = await client.get("/api/parking/lots", headers=driver_auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_list_lots_unauthenticated(client: AsyncClient):
    response = await client.get("/api/parking/lots")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_lot_details(client: AsyncClient, driver_auth_headers: dict, db: AsyncSession):
    lot = await _create_lot(db)
    response = await client.get(f"/api/parking/lots/{lot.id}", headers=driver_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Lot"
    assert "available_spaces" in data


@pytest.mark.asyncio
async def test_get_lot_not_found(client: AsyncClient, driver_auth_headers: dict):
    fake_id = uuid.uuid4()
    response = await client.get(f"/api/parking/lots/{fake_id}", headers=driver_auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_lot_spaces(client: AsyncClient, driver_auth_headers: dict, db: AsyncSession):
    lot = await _create_lot(db)
    await _create_space(db, lot.id)
    response = await client.get(f"/api/parking/lots/{lot.id}/spaces", headers=driver_auth_headers)
    assert response.status_code == 200
    spaces = response.json()
    assert len(spaces) >= 1
    assert spaces[0]["space_number"] == "A1"


@pytest.mark.asyncio
async def test_update_space_status_staff(client: AsyncClient, db: AsyncSession):
    staff = await _create_staff(db)
    token = create_access_token({"sub": str(staff.id), "role": staff.role.value})
    headers = {"Authorization": f"Bearer {token}"}
    lot = await _create_lot(db)
    space = await _create_space(db, lot.id)
    response = await client.put(
        f"/api/parking/spaces/{space.id}/status",
        json={"is_occupied": True, "confidence_score": 0.95, "detection_method": "cnn"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["is_occupied"] is True


@pytest.mark.asyncio
async def test_update_space_status_driver_forbidden(
    client: AsyncClient, driver_auth_headers: dict, db: AsyncSession
):
    lot = await _create_lot(db)
    space = await _create_space(db, lot.id)
    response = await client.put(
        f"/api/parking/spaces/{space.id}/status",
        json={"is_occupied": True},
        headers=driver_auth_headers,
    )
    assert response.status_code == 403
