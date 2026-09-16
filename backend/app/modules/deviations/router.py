
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.deviations.schemas import DeviationItem
from app.modules.deviations.service import list_deviations

router = APIRouter(prefix="/deviations", tags=["deviations"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"module": "M7 Deviation Management", "status": "not_yet_implemented"}


@router.get("/list", response_model=list[DeviationItem])
async def get_deviations(db: Annotated[AsyncSession, Depends(get_db)]) -> list[DeviationItem]:
    deviations = await list_deviations(db)
    return [DeviationItem(**d) for d in deviations]

