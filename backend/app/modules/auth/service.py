import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, create_refresh_token, hash_password, verify_password
from app.modules.auth.models import Role, User

RESET_TOKEN_VALID_MINUTES = 60


class AuthError(Exception):
    """Raised for password-reset failures — invalid or expired token."""


async def authenticate_user(db: AsyncSession, username: str, password: str) -> tuple[str, str] | None:
    result = await db.execute(
        select(User, Role.name).join(Role, User.role_id == Role.id).where(User.username == username)
    )
    row = result.first()
    if row is None:
        return None

    user, role_name = row
    if not verify_password(password, user.hashed_password):
        return None

    access_token = create_access_token(subject=user.username, role=role_name)
    refresh_token = create_refresh_token(subject=user.username, role=role_name)
    return access_token, refresh_token


async def request_password_reset(db: AsyncSession, username: str) -> tuple[User, str] | None:
    """Generates and stores a reset token for the given username (email).
    Returns None if no such user exists — the router deliberately shows
    the same generic message either way, so this isn't used to leak
    which emails have accounts."""
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if user is None:
        return None

    raw_token = secrets.token_urlsafe(32)
    user.reset_token = raw_token
    user.reset_token_expires_at = datetime.now(timezone.utc) + timedelta(minutes=RESET_TOKEN_VALID_MINUTES)
    await db.flush()

    return user, raw_token


async def reset_password(db: AsyncSession, token: str, new_password: str) -> None:
    result = await db.execute(select(User).where(User.reset_token == token))
    user = result.scalar_one_or_none()
    if user is None:
        raise AuthError("This reset link is invalid. Please request a new one.")

    expires_at = user.reset_token_expires_at
    if expires_at is None or expires_at < datetime.now(timezone.utc):
        raise AuthError("This reset link has expired. Please request a new one.")

    user.hashed_password = hash_password(new_password)
    user.reset_token = None
    user.reset_token_expires_at = None
    await db.flush()
