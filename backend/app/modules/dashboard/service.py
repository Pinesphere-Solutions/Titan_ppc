
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.integrations.sap.open_po import get_open_po_summary
from app.modules.dc_verification.models import DeliveryChallan
from app.modules.deviations.models import Deviation
from app.modules.sap_outward.models import Dispatch
from app.modules.sap_processing.models import SapMovement


async def get_dashboard_summary(db: AsyncSession) -> dict:
    total_dispatches = (await db.execute(select(func.count()).select_from(Dispatch))).scalar_one()

    pending_verification = (
        await db.execute(
            select(func.count()).select_from(DeliveryChallan).where(DeliveryChallan.verification_status == "pending")
        )
    ).scalar_one()

    pending_qc_acknowledgement = (
        await db.execute(
            select(func.count())
            .select_from(DeliveryChallan)
            .where(DeliveryChallan.verification_status == "verified", DeliveryChallan.qc_ack_status == "pending")
        )
    ).scalar_one()

    open_deviations = (
        await db.execute(
            select(func.count()).select_from(Deviation).where(Deviation.vendor_status == "awaiting_response")
        )
    ).scalar_one()

    total_movements_synced = (await db.execute(select(func.count()).select_from(SapMovement))).scalar_one()

    open_po_summary = await get_open_po_summary(db)
    open_po_count = sum(1 for po in open_po_summary if po["pending_qty"] > 0)
    total_pending_qty = sum(po["pending_qty"] for po in open_po_summary)

    return {
        "total_dispatches": total_dispatches,
        "pending_verification": pending_verification,
        "pending_qc_acknowledgement": pending_qc_acknowledgement,
        "open_deviations": open_deviations,
        "total_movements_synced": total_movements_synced,
        "open_po_count": open_po_count,
        "total_pending_qty": total_pending_qty,
    }