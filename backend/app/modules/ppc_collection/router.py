"""M10 PPC Collection and Verification — see architecture doc Section 5.2."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import CurrentUser, get_current_user
from app.modules.ppc_collection.schemas import (
    PpcCollectionListItem,
    PpcCollectionRequest,
    PpcCollectionResponse,
)
from app.modules.ppc_collection.service import (
    PpcCollectionError,
    collect_material,
    list_pending_collection,
)

router = APIRouter(prefix="/ppc-collection", tags=["ppc_collection"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"module": "M10 PPC Collection and Verification", "status": "ok"}


@router.get("/pending", response_model=list[PpcCollectionListItem])
async def get_pending(db: Annotated[AsyncSession, Depends(get_db)]) -> list[PpcCollectionListItem]:
    items = await list_pending_collection(db)
    return [PpcCollectionListItem(**i) for i in items]


@router.post("/{dc_no}/collect", response_model=PpcCollectionResponse)
async def collect(
    dc_no: str,
    payload: PpcCollectionRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PpcCollectionResponse:
    try:
        result = await collect_material(db, dc_no, payload.tray_no, collected_by=current_user.username)
        await db.commit()
    except PpcCollectionError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e

    return PpcCollectionResponse(**result)
