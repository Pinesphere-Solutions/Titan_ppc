
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import CurrentUser, get_current_user
from app.modules.qc_acknowledgement.schemas import QcAcknowledgeResponse
from app.modules.qc_acknowledgement.service import QcAcknowledgementError, acknowledge_dc

router = APIRouter(prefix="/qc-acknowledgement", tags=["qc_acknowledgement"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"module": "M8 QC Acknowledgement", "status": "not_yet_implemented"}


@router.post("/{dc_no}/acknowledge", response_model=QcAcknowledgeResponse)
async def acknowledge(
    dc_no: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> QcAcknowledgeResponse:
    try:
        result = await acknowledge_dc(db, dc_no, acknowledged_by=current_user.username)
        await db.commit()
    except QcAcknowledgementError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e

    return QcAcknowledgeResponse(**result)