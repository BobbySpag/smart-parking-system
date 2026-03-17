"""pytest fixtures for backend tests."""
import asyncio
import uuid
from typing import AsyncGenerator
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from backend.app.main import app
from backend.app.database import Base, get_db
from backend.app.models.user import User, UserRole
from backend.app.services.auth_service import hash_password, create_access_token

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_db():
    """Create all tables before the test session and drop them after."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db() -> AsyncGenerator[AsyncSession, None]:
    async with TestSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def test_user(db: AsyncSession) -> User:
    """Create and persist a test driver user."""
    user = User(
        email="testdriver@example.com",
        hashed_password=hash_password("Password1"),
        full_name="Test Driver",
        role=UserRole.driver,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_admin(db: AsyncSession) -> User:
    """Create and persist a test admin user."""
    user = User(
        email="testadmin@example.com",
        hashed_password=hash_password("AdminPass1"),
        full_name="Test Admin",
        role=UserRole.admin,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest_asyncio.fixture
def driver_auth_headers(test_user: User) -> dict:
    token = create_access_token({"sub": str(test_user.id), "role": test_user.role.value})
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
def admin_auth_headers(test_admin: User) -> dict:
    token = create_access_token({"sub": str(test_admin.id), "role": test_admin.role.value})
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
