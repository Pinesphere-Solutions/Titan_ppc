"""M11 QA Inspection — see architecture doc Section 5.2."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import CurrentUser, get_current_user
from app.modules.qa_inspection.schemas import QaInspectionQueueItem, QaInspectionResponse
from app.modules.qa_inspection.service import (
    QaInspectionError,
    complete_inspection,
    list_inspection_queue,
    start_inspection,
)

router = APIRouter(prefix="/qa-inspection", tags=["qa_inspection"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"module": "M11 QA Inspection", "status": "ok"}


@router.get("/queue", response_model=list[QaInspectionQueueItem])
async def get_queue(db: Annotated[AsyncSession, Depends(get_db)]) -> list[QaInspectionQueueItem]:
    items = await list_inspection_queue(db)
    return [QaInspectionQueueItem(**i) for i in items]


@router.post("/{dc_no}/start", response_model=QaInspectionResponse)
async def start(
    dc_no: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> QaInspectionResponse:
    try:
        result = await start_inspection(db, dc_no, qa_user=current_user.username)
        await db.commit()
    except QaInspectionError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e

    return QaInspectionResponse(**result)


@router.post("/{dc_no}/complete", response_model=QaInspectionResponse)
async def complete(
    dc_no: str,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> QaInspectionResponse:
    try:
        result = await complete_inspection(db, dc_no)
        await db.commit()
    except QaInspectionError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e

    return QaInspectionResponse(**result)
