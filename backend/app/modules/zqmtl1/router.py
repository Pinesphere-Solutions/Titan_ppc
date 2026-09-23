"""M12 ZQMTL1 Processing — see architecture doc Section 5.2."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import CurrentUser, get_current_user
from app.modules.zqmtl1.schemas import Zqmtl1PendingItem, Zqmtl1Response
from app.modules.zqmtl1.service import Zqmtl1Error, list_pending_zqmtl1, process_zqmtl1

router = APIRouter(prefix="/zqmtl1", tags=["zqmtl1"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"module": "M12 ZQMTL1 Processing", "status": "ok"}


@router.get("/pending", response_model=list[Zqmtl1PendingItem])
async def get_pending(db: Annotated[AsyncSession, Depends(get_db)]) -> list[Zqmtl1PendingItem]:
    items = await list_pending_zqmtl1(db)
    return [Zqmtl1PendingItem(**i) for i in items]


@router.post("/{dc_no}/process", response_model=Zqmtl1Response)
async def process(
    dc_no: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Zqmtl1Response:
    try:
        result = await process_zqmtl1(db, dc_no, processed_by=current_user.username)
        await db.commit()
    except Zqmtl1Error as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e

    return Zqmtl1Response(**result)
