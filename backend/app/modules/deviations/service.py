"""Business logic for M7 Deviation Management."""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.dc_verification.models import DeliveryChallan
from app.modules.deviations.models import Deviation
from app.modules.masters.models import Vendor
from app.modules.sap_outward.models import Dispatch


class DeviationError(Exception):
    """Raised when a deviation can't be resolved — unknown DC, or
    already resolved."""


async def list_deviations(db: AsyncSession) -> list[dict]:
    stmt = (
        select(Deviation, DeliveryChallan.dc_no, Dispatch.material_code, Vendor.name)
        .join(DeliveryChallan, Deviation.dc_id == DeliveryChallan.id)
        .join(Dispatch, DeliveryChallan.dispatch_id == Dispatch.id)
        .join(Vendor, Dispatch.vendor_id == Vendor.id)
        .order_by(Deviation.created_at.desc())
    )
    rows = (await db.execute(stmt)).all()

    return [
        {
            "dc_no": dc_no,
            "vendor_name": vendor_name,
            "material_code": material_code,
            "deviation_type": deviation.deviation_type,
            "expected_qty": deviation.expected_qty,
            "actual_qty": deviation.actual_qty,
            "difference_qty": deviation.difference_qty,
            "mail_status": deviation.mail_status,
            "vendor_status": deviation.vendor_status,
            "resolved_by": deviation.resolved_by,
            "resolved_at": deviation.resolved_at,
            "created_at": deviation.created_at,
        }
        for deviation, dc_no, material_code, vendor_name in rows
    ]


async def resolve_deviation(db: AsyncSession, dc_no: str, resolved_by: str) -> dict:
    """Lightweight resolution — marks the deviation closed once the
    vendor has sent a corrected DC. Does NOT reopen the DeliveryChallan
    for re-verification; that stays "reverted" permanently as a
    historical record (see Deviation model docstring)."""
    stmt = (
        select(Deviation, DeliveryChallan.dc_no)
        .join(DeliveryChallan, Deviation.dc_id == DeliveryChallan.id)
        .where(DeliveryChallan.dc_no == dc_no)
    )
    result = await db.execute(stmt)
    row = result.first()
    if row is None:
        raise DeviationError(f"No deviation found for DC {dc_no}")

    deviation, _ = row

    if deviation.vendor_status == "resolved":
        raise DeviationError(f"Deviation for DC {dc_no} has already been resolved")

    deviation.vendor_status = "resolved"
    deviation.resolved_by = resolved_by
    deviation.resolved_at = datetime.now(timezone.utc)

    return {
        "dc_no": dc_no,
        "vendor_status": deviation.vendor_status,
        "resolved_by": deviation.resolved_by,
        "resolved_at": deviation.resolved_at,
    }


