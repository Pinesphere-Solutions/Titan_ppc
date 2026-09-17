

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.dc_verification.models import DeliveryChallan
from app.modules.sap_processing.models import SapMovement


async def list_movements(db: AsyncSession) -> list[dict]:
    stmt = (
        select(SapMovement, DeliveryChallan.dc_no)
        .join(DeliveryChallan, SapMovement.dc_id == DeliveryChallan.id)
        .order_by(SapMovement.created_at.desc())
    )
    rows = (await db.execute(stmt)).all()

    return [
        {
            "material_document_no": movement.material_document_no,
            "movement_type": movement.movement_type,
            "dc_no": dc_no,
            "posting_date": movement.posting_date,
            "sync_status": movement.sync_status,
        }
        for movement, dc_no in rows
    ]