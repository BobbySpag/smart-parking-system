"""Tests for authentication endpoints."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_new_user(client: AsyncClient):
    response = await client.post(
        "/api/auth/register",
        json={"email": "newuser@example.com", "password": "NewPass1", "full_name": "New User"},
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    payload = {"email": "duplicate@example.com", "password": "Pass1234", "full_name": "Dup User"}
    await client.post("/api/auth/register", json=payload)
    response = await client.post("/api/auth/register", json=payload)
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_login_valid_credentials(client: AsyncClient):
    # First register
    await client.post(
        "/api/auth/register",
        json={"email": "logintest@example.com", "password": "LoginPass1", "full_name": "Login Test"},
    )
    # Then login
    response = await client.post(
        "/api/auth/login",
        data={"username": "logintest@example.com", "password": "LoginPass1"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    response = await client.post(
        "/api/auth/login",
        data={"username": "nobody@example.com", "password": "wrong"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me_authenticated(client: AsyncClient, driver_auth_headers: dict):
    response = await client.get("/api/auth/me", headers=driver_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "testdriver@example.com"
    assert data["role"] == "driver"


@pytest.mark.asyncio
async def test_get_me_unauthenticated(client: AsyncClient):
    response = await client.get("/api/auth/me")
    assert response.status_code == 401
