

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.integrations.sap.dependency import get_sap_client
from app.modules.dc_verification.models import DeliveryChallan


class QcAcknowledgementError(Exception):
    """Raised for acknowledgement requests that can't be processed —
    unknown DC, not yet verified, reverted, or already acknowledged."""


async def acknowledge_dc(db: AsyncSession, dc_no: str, acknowledged_by: str) -> dict:
    result = await db.execute(select(DeliveryChallan).where(DeliveryChallan.dc_no == dc_no))
    dc = result.scalar_one_or_none()
    if dc is None:
        raise QcAcknowledgementError(f"No delivery challan found with DC number {dc_no}")

    if dc.verification_status != "verified":
        raise QcAcknowledgementError(
            f"DC {dc_no} has verification status '{dc.verification_status}' — "
            "only a verified (matched or excess) DC can be QC acknowledged"
        )

    if dc.qc_ack_status == "done":
        raise QcAcknowledgementError(f"DC {dc_no} has already been QC acknowledged")

    # Mark acknowledged
    dc.qc_ack_status = "done"
    dc.qc_acknowledged_by = acknowledged_by
    dc.qc_acknowledged_at = datetime.now(timezone.utc)

    # Trigger Level 2 -> Level 1 stock movement (confirmed process step)
    dc.stock_level = "level_1"

    # UD Post to SAP, now that material is at Level 1
    sap_client = get_sap_client()
    ud_result = await sap_client.post_ud(dc_no, {"stock_level": "level_1"})
    dc.ud_post_status = ud_result.get("status", "posted")

    return {
        "dc_no": dc.dc_no,
        "qc_ack_status": dc.qc_ack_status,
        "qc_acknowledged_by": dc.qc_acknowledged_by,
        "stock_level": dc.stock_level,
        "ud_post_status": dc.ud_post_status,
    }