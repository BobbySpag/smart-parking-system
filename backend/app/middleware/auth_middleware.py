"""JWT authentication middleware and reusable dependencies."""
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from ..models.user import User, UserRole
from ..services.auth_service import get_current_user, require_roles

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


async def get_optional_current_user(
    request: Request,
    token: str | None = Depends(oauth2_scheme),
) -> User | None:
    """Return the current user if a valid token is present, otherwise None."""
    if token is None:
        return None
    try:
        from ..database import get_db
        from sqlalchemy.ext.asyncio import AsyncSession
        # Re-use the standard get_current_user but swallow auth errors
        from ..services.auth_service import decode_token
        import uuid
        from sqlalchemy import select

        token_data = decode_token(token)
        async for db in get_db():
            result = await db.execute(
                select(User).where(User.id == uuid.UUID(token_data.sub))
            )
            user = result.scalar_one_or_none()
            return user if (user and user.is_active) else None
    except Exception:
        return None


def require_admin() -> User:
    """Shortcut dependency that requires the admin role."""
    return Depends(require_roles(UserRole.admin))


def require_staff_or_admin():
    """Shortcut dependency that requires staff or admin role."""
    return Depends(require_roles(UserRole.staff, UserRole.admin))
