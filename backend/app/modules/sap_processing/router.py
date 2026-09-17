
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.integrations.sap.dependency import get_sap_client
from app.integrations.sap.mapping import SAPMappingError, map_movement
from app.modules.sap_processing.schemas import MovementItem
from app.modules.sap_processing.service import list_movements

router = APIRouter(prefix="/sap-processing", tags=["sap_processing"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"module": "M9 SAP Processing", "status": "not_yet_implemented"}


@router.get("/list", response_model=list[MovementItem])
async def get_movements(db: Annotated[AsyncSession, Depends(get_db)]) -> list[MovementItem]:
    movements = await list_movements(db)
    return [MovementItem(**m) for m in movements]


@router.post("/sync-movements")
async def sync_movements(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, object]:
    """Manually trigger a movement sync (101/313/321). See M3's /sync
    endpoint for the identical pattern — one bad record doesn't abort
    the batch."""
    sap_client = get_sap_client()
    records = await sap_client.fetch_movements()

    succeeded: list[str] = []
    failed: list[dict[str, str]] = []

    for record in records:
        try:
            movement = await map_movement(db, record)
            await db.commit()
            succeeded.append(movement.material_document_no)
        except SAPMappingError as e:
            await db.rollback()
            failed.append(
                {"material_document_no": record.get("material_document_no", "unknown"), "reason": str(e)}
            )

    return {
        "total_records": len(records),
        "succeeded": succeeded,
        "failed": failed,
    }