"""M13 Storage Management — see architecture doc Section 5.2."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import CurrentUser, get_current_user
from app.modules.storage.schemas import (
    StorageAssignRequest,
    StoragePendingItem,
    StorageResponse,
    StoredItem,
)
from app.modules.storage.service import StorageError, assign_storage, list_pending_storage, list_stored

router = APIRouter(prefix="/storage", tags=["storage"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"module": "M13 Storage Management", "status": "ok"}


@router.get("/pending", response_model=list[StoragePendingItem])
async def get_pending(db: Annotated[AsyncSession, Depends(get_db)]) -> list[StoragePendingItem]:
    items = await list_pending_storage(db)
    return [StoragePendingItem(**i) for i in items]


@router.post("/{dc_no}/assign", response_model=StorageResponse)
async def assign(
    dc_no: str,
    payload: StorageAssignRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> StorageResponse:
    try:
        result = await assign_storage(
            db,
            dc_no,
            rack=payload.rack,
            row=payload.row,
            bin=payload.bin,
            storage_location=payload.storage_location,
            stored_by=current_user.username,
        )
        await db.commit()
    except StorageError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e

    return StorageResponse(**result)


@router.get("/list", response_model=list[StoredItem])
async def get_list(
    db: Annotated[AsyncSession, Depends(get_db)],
    search: str | None = None,
) -> list[StoredItem]:
    items = await list_stored(db, search=search)
    return [StoredItem(**i) for i in items]
