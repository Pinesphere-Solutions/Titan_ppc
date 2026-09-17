"""M7 Deviation Management — see architecture doc Section 5.2."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import CurrentUser, get_current_user
from app.modules.deviations.schemas import DeviationItem, DeviationResolveResponse
from app.modules.deviations.service import DeviationError, list_deviations, resolve_deviation

router = APIRouter(prefix="/deviations", tags=["deviations"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"module": "M7 Deviation Management", "status": "not_yet_implemented"}


@router.get("/list", response_model=list[DeviationItem])
async def get_deviations(db: Annotated[AsyncSession, Depends(get_db)]) -> list[DeviationItem]:
    deviations = await list_deviations(db)
    return [DeviationItem(**d) for d in deviations]


@router.post("/{dc_no}/resolve", response_model=DeviationResolveResponse)
async def resolve(
    dc_no: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> DeviationResolveResponse:
    try:
        result = await resolve_deviation(db, dc_no, resolved_by=current_user.username)
        await db.commit()
    except DeviationError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e

    return DeviationResolveResponse(**result)

