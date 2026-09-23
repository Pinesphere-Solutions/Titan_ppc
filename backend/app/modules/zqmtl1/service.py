"""Business logic for M12 ZQMTL1 Processing.

Per KT notes (Module-Wireframe-Draft steps 46-51): once QA Inspection
(M11) is complete, the material moves to "Level 1 (ZQMTL1)" for a
material check, a second UD Post, and a second SAP 313 transfer. The
manual Excel-reformatting and printout/signature steps described in
the KT notes are paperwork outside this application's scope; this
module covers the system-recorded parts — material check, UD Post,
and the move to SAP 313 — as one combined confirm action, consistent
with how PPC Collection (M10) combines its own two KT functions into
a single step.

Eligible once QA Inspection is completed; not repeatable once already
processed.
"""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.integrations.sap.dependency import get_sap_client
from app.modules.dc_verification.models import DeliveryChallan
from app.modules.masters.models import Vendor
from app.modules.qa_inspection.models import QaInspection
from app.modules.sap_outward.models import Dispatch
from app.modules.zqmtl1.models import Zqmtl1Processing


class Zqmtl1Error(Exception):
    """Raised when ZQMTL1 processing can't proceed — unknown DC, QA
    Inspection not yet completed, or already processed."""


async def list_pending_zqmtl1(db: AsyncSession) -> list[dict]:
    stmt = (
        select(
            DeliveryChallan,
            Vendor.name,
            Dispatch.material_code,
            Dispatch.model,
            (Dispatch.quantity_front_case + Dispatch.quantity_back_case).label("quantity"),
        )
        .join(Dispatch, DeliveryChallan.dispatch_id == Dispatch.id)
        .join(Vendor, Dispatch.vendor_id == Vendor.id)
        .join(QaInspection, QaInspection.dc_id == DeliveryChallan.id)
        .outerjoin(Zqmtl1Processing, Zqmtl1Processing.dc_id == DeliveryChallan.id)
        .where(QaInspection.inspection_status == "completed", Zqmtl1Processing.id.is_(None))
    )
    rows = (await db.execute(stmt)).all()
    return [
        {
            "dc_no": dc.dc_no,
            "vendor_name": vendor_name,
            "material_code": material_code,
            "model": model,
            "quantity": quantity,
        }
        for dc, vendor_name, material_code, model, quantity in rows
    ]


async def process_zqmtl1(db: AsyncSession, dc_no: str, processed_by: str) -> dict:
    stmt = (
        select(DeliveryChallan, Vendor.name)
        .join(Dispatch, DeliveryChallan.dispatch_id == Dispatch.id)
        .join(Vendor, Dispatch.vendor_id == Vendor.id)
        .where(DeliveryChallan.dc_no == dc_no)
    )
    row = (await db.execute(stmt)).first()
    if row is None:
        raise Zqmtl1Error(f"No delivery challan found for {dc_no}")
    dc, vendor_name = row

    inspection_result = await db.execute(select(QaInspection).where(QaInspection.dc_id == dc.id))
    inspection = inspection_result.scalar_one_or_none()
    if inspection is None or inspection.inspection_status != "completed":
        raise Zqmtl1Error(f"DC {dc_no} has not completed QA Inspection yet — cannot process at ZQMTL1")

    existing = await db.execute(select(Zqmtl1Processing).where(Zqmtl1Processing.dc_id == dc.id))
    if existing.scalar_one_or_none() is not None:
        raise Zqmtl1Error(f"DC {dc_no} has already been processed at ZQMTL1")

    sap_client = get_sap_client()
    await sap_client.post_ud(dc_no, {"stage": "zqmtl1"})
    posting_313 = await sap_client.post_313(dc_no, {"stage": "zqmtl1"})

    record = Zqmtl1Processing(
        dc_id=dc.id,
        zqmtl1_status="checked",
        sap_status=posting_313.get("status", "posted"),
        processed_by=processed_by,
        processed_at=datetime.now(timezone.utc),
    )
    db.add(record)

    return {
        "dc_no": dc.dc_no,
        "vendor_name": vendor_name,
        "zqmtl1_status": record.zqmtl1_status,
        "sap_status": record.sap_status,
        "processed_by": processed_by,
        "message": f"ZQMTL1 processing completed for {vendor_name}",
    }
