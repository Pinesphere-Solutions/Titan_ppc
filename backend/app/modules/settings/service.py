"""Business logic for M16 Settings. See architecture doc Section 5.2.

Scoped to User Management and Role Management for now — see schemas.py
for why. Reuses the existing auth.models.User / auth.models.Role tables
rather than introducing new ones."""

import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.modules.auth.models import Role, User


class SettingsError(Exception):
    """Raised for any user-facing failure in M16 Settings — the router
    converts this to a 400, same pattern as every other module's *Error."""


async def list_roles(db: AsyncSession) -> list[dict]:
    result = await db.execute(select(Role).order_by(Role.name))
    return [{"id": str(role.id), "name": role.name} for role in result.scalars().all()]


async def create_role(db: AsyncSession, name: str) -> dict:
    existing = await db.execute(select(Role).where(Role.name == name))
    if existing.scalar_one_or_none() is not None:
        raise SettingsError(f"Role '{name}' already exists.")

    role = Role(name=name)
    db.add(role)
    try:
        await db.flush()
    except IntegrityError as e:
        raise SettingsError(f"Role '{name}' already exists.") from e

    return {"id": str(role.id), "name": role.name}


async def list_users(db: AsyncSession) -> list[dict]:
    result = await db.execute(
        select(User, Role.name).join(Role, User.role_id == Role.id).order_by(User.username)
    )
    return [
        {"id": str(user.id), "username": user.username, "role_id": str(user.role_id), "role_name": role_name}
        for user, role_name in result.all()
    ]


async def create_user(db: AsyncSession, username: str, password: str, role_id: str) -> dict:
    existing = await db.execute(select(User).where(User.username == username))
    if existing.scalar_one_or_none() is not None:
        raise SettingsError(f"Username '{username}' is already taken.")

    try:
        role_uuid = uuid.UUID(role_id)
    except ValueError as e:
        raise SettingsError("Invalid role.") from e

    role = await db.get(Role, role_uuid)
    if role is None:
        raise SettingsError("Selected role does not exist.")

    user = User(username=username, hashed_password=hash_password(password), role_id=role_uuid)
    db.add(user)
    try:
        await db.flush()
    except IntegrityError as e:
        raise SettingsError(f"Username '{username}' is already taken.") from e

    return {"id": str(user.id), "username": user.username, "role_id": str(role.id), "role_name": role.name}


async def update_user_role(db: AsyncSession, user_id: str, role_id: str) -> dict:
    try:
        user_uuid = uuid.UUID(user_id)
        role_uuid = uuid.UUID(role_id)
    except ValueError as e:
        raise SettingsError("Invalid user or role.") from e

    user = await db.get(User, user_uuid)
    if user is None:
        raise SettingsError("User not found.")

    role = await db.get(Role, role_uuid)
    if role is None:
        raise SettingsError("Selected role does not exist.")

    user.role_id = role_uuid
    await db.flush()

    return {"id": str(user.id), "username": user.username, "role_id": str(role.id), "role_name": role.name}
