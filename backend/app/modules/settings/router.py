"""M16 Settings — see architecture doc Section 5.2.

Scoped to User Management and Role Management for now — see schemas.py
for why. Every endpoint here is admin-only: user and role management is
exactly the kind of action that shouldn't be reachable by every role."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import CurrentUser, require_role
from app.modules.settings.schemas import (
    RoleCreateRequest,
    RoleItem,
    UserCreateRequest,
    UserItem,
    UserUpdateRoleRequest,
)
from app.modules.settings.service import (
    SettingsError,
    create_role,
    create_user,
    list_roles,
    list_users,
    update_user_role,
)

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"module": "M16 Settings", "status": "ok"}


@router.get("/roles", response_model=list[RoleItem])
async def get_roles(
    current_user: Annotated[CurrentUser, Depends(require_role("admin"))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[RoleItem]:
    roles = await list_roles(db)
    return [RoleItem(**r) for r in roles]


@router.post("/roles", response_model=RoleItem)
async def add_role(
    payload: RoleCreateRequest,
    current_user: Annotated[CurrentUser, Depends(require_role("admin"))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> RoleItem:
    try:
        role = await create_role(db, payload.name)
        await db.commit()
    except SettingsError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e

    return RoleItem(**role)


@router.get("/users", response_model=list[UserItem])
async def get_users(
    current_user: Annotated[CurrentUser, Depends(require_role("admin"))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[UserItem]:
    users = await list_users(db)
    return [UserItem(**u) for u in users]


@router.post("/users", response_model=UserItem)
async def add_user(
    payload: UserCreateRequest,
    current_user: Annotated[CurrentUser, Depends(require_role("admin"))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserItem:
    try:
        user = await create_user(db, payload.username, payload.password, payload.role_id)
        await db.commit()
    except SettingsError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e

    return UserItem(**user)


@router.patch("/users/{user_id}/role", response_model=UserItem)
async def change_user_role(
    user_id: str,
    payload: UserUpdateRoleRequest,
    current_user: Annotated[CurrentUser, Depends(require_role("admin"))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserItem:
    try:
        user = await update_user_role(db, user_id, payload.role_id)
        await db.commit()
    except SettingsError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e

    return UserItem(**user)
