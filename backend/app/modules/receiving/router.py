"""Gate Entry, Sub-con Receiving, and M4 Material Receiving categorization.
See architecture doc Section 5.1/5.2 and the useScannerInput hook this
serves. All mutating endpoints require auth (same as QC Acknowledgement)."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import CurrentUser, get_current_user
from app.modules.receiving.schemas import (
    CategorizeRequest,
    CategorizeResponse,
    ReceivingListItem,
    ScanRequest,
    ScanResponse,
)
from app.modules.receiving.service import (
    ReceivingError,
    list_pending_categorization,
    log_gate_entry,
    log_subcon_receipt,
    set_receiving_category,
)

router = APIRouter(prefix="/receiving", tags=["receiving"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"module": "Material Receiving", "status": "not_yet_implemented"}


@router.post("/gate-entry", response_model=ScanResponse)
async def gate_entry(
    payload: ScanRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ScanResponse:
    try:
        result = await log_gate_entry(db, payload.dc_no, scanned_by=current_user.username)
        await db.commit()
    except ReceivingError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e

    return ScanResponse(**result)


@router.post("/subcon-scan", response_model=ScanResponse)
async def subcon_scan(
    payload: ScanRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ScanResponse:
    try:
        result = await log_subcon_receipt(db, payload.dc_no, scanned_by=current_user.username)
        await db.commit()
    except ReceivingError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e

    return ScanResponse(**result)


@router.get("/pending-categorization", response_model=list[ReceivingListItem])
async def get_pending_categorization(db: Annotated[AsyncSession, Depends(get_db)]) -> list[ReceivingListItem]:
    items = await list_pending_categorization(db)
    return [ReceivingListItem(**i) for i in items]


@router.post("/{dc_no}/categorize", response_model=CategorizeResponse)
async def categorize(
    dc_no: str,
    payload: CategorizeRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> CategorizeResponse:
    try:
        result = await set_receiving_category(db, dc_no, payload.category, set_by=current_user.username)
        await db.commit()
    except ReceivingError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e

    return CategorizeResponse(**result)