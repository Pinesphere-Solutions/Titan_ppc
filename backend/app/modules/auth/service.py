from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, create_refresh_token, verify_password
from app.modules.auth.models import Role, User


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
    refresh_token = create_refresh_token(subject=user.username)
    return access_token, refresh_token
