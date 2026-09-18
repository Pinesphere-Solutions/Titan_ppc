"""M6 Physical Verification — see architecture doc Section 5.2."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import CurrentUser, get_current_user
from app.modules.physical_verification.schemas import (
    PhysicalVerificationListItem,
    PhysicalVerificationResponse,
)
from app.modules.physical_verification.service import (
    PhysicalVerificationError,
    confirm_physical_verification,
    list_pending_physical_verification,
)

router = APIRouter(prefix="/physical-verification", tags=["physical_verification"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"module": "M6 Physical Verification", "status": "not_yet_implemented"}


@router.get("/pending", response_model=list[PhysicalVerificationListItem])
async def get_pending(db: Annotated[AsyncSession, Depends(get_db)]) -> list[PhysicalVerificationListItem]:
    items = await list_pending_physical_verification(db)
    return [PhysicalVerificationListItem(**i) for i in items]


@router.post("/{dc_no}/confirm", response_model=PhysicalVerificationResponse)
async def confirm(
    dc_no: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PhysicalVerificationResponse:
    try:
        result = await confirm_physical_verification(db, dc_no, verified_by=current_user.username)
        await db.commit()
    except PhysicalVerificationError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e

    return PhysicalVerificationResponse(**result)