
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.reports.schemas import MovementHistoryEvent
from app.modules.reports.service import get_material_movement_history

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"module": "M14 Reports", "status": "not_yet_implemented"}


@router.get("/material-movement-history", response_model=list[MovementHistoryEvent])
async def material_movement_history(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[MovementHistoryEvent]:
    events = await get_material_movement_history(db)
    return [MovementHistoryEvent(**e) for e in events]