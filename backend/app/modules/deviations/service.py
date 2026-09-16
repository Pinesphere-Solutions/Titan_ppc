
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.dc_verification.models import DeliveryChallan
from app.modules.deviations.models import Deviation
from app.modules.masters.models import Vendor
from app.modules.sap_outward.models import Dispatch


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
            "created_at": deviation.created_at,
        }
        for deviation, dc_no, material_code, vendor_name in rows
    ]