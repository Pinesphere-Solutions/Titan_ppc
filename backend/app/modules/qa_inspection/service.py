"""Business logic for M11 QA Inspection.

Per KT notes (Module-Wireframe-Draft steps 43-46): after PPC Collection
(M10) ends the Sub-con process, the material is pending with a separate
Quality Team under "Waiting for Inspection" status, then moves through
"in_progress" (Start Inspection) to "completed" (Complete Inspection)
before it can move on to ZQMTL1 (M12).

Eligible once the DC has a PpcCollection record; not eligible before
that, and not repeatable once already started/completed.
"""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.dc_verification.models import DeliveryChallan
from app.modules.masters.models import Vendor
from app.modules.ppc_collection.models import PpcCollection
from app.modules.qa_inspection.models import QaInspection
from app.modules.sap_outward.models import Dispatch


class QaInspectionError(Exception):
    """Raised when inspection can't be processed — unknown DC, not yet
    collected by PPC, already started/completed, or not yet started."""


async def list_inspection_queue(db: AsyncSession) -> list[dict]:
    stmt = (
        select(DeliveryChallan, Vendor.name, Dispatch.material_code, Dispatch.model, QaInspection)
        .join(Dispatch, DeliveryChallan.dispatch_id == Dispatch.id)
        .join(Vendor, Dispatch.vendor_id == Vendor.id)
        .join(PpcCollection, PpcCollection.dc_id == DeliveryChallan.id)
        .outerjoin(QaInspection, QaInspection.dc_id == DeliveryChallan.id)
    )
    rows = (await db.execute(stmt)).all()

    result = []
    for dc, vendor_name, material_code, model, inspection in rows:
        if inspection is not None and inspection.inspection_status == "completed":
            continue  # already done, not part of the active queue
        result.append(
            {
                "dc_no": dc.dc_no,
                "vendor_name": vendor_name,
                "material_code": material_code,
                "model": model,
                "inspection_status": inspection.inspection_status if inspection else "waiting_for_inspection",
                "qa_user": inspection.qa_user if inspection else None,
            }
        )
    return result


async def start_inspection(db: AsyncSession, dc_no: str, qa_user: str) -> dict:
    stmt = (
        select(DeliveryChallan, Vendor.name)
        .join(Dispatch, DeliveryChallan.dispatch_id == Dispatch.id)
        .join(Vendor, Dispatch.vendor_id == Vendor.id)
        .where(DeliveryChallan.dc_no == dc_no)
    )
    row = (await db.execute(stmt)).first()
    if row is None:
        raise QaInspectionError(f"No delivery challan found for {dc_no}")
    dc, vendor_name = row

    collected = await db.execute(select(PpcCollection).where(PpcCollection.dc_id == dc.id))
    if collected.scalar_one_or_none() is None:
        raise QaInspectionError(f"DC {dc_no} has not been collected by PPC yet — cannot start inspection")

    existing = await db.execute(select(QaInspection).where(QaInspection.dc_id == dc.id))
    if existing.scalar_one_or_none() is not None:
        raise QaInspectionError(f"DC {dc_no} inspection has already been started or completed")

    inspection = QaInspection(
        dc_id=dc.id,
        inspection_status="in_progress",
        qa_user=qa_user,
        started_at=datetime.now(timezone.utc),
    )
    db.add(inspection)

    return {
        "dc_no": dc.dc_no,
        "vendor_name": vendor_name,
        "inspection_status": inspection.inspection_status,
        "qa_user": qa_user,
        "message": f"Inspection started for {vendor_name}",
    }


async def complete_inspection(db: AsyncSession, dc_no: str) -> dict:
    stmt = (
        select(DeliveryChallan, Vendor.name, QaInspection)
        .join(Dispatch, DeliveryChallan.dispatch_id == Dispatch.id)
        .join(Vendor, Dispatch.vendor_id == Vendor.id)
        .join(QaInspection, QaInspection.dc_id == DeliveryChallan.id)
        .where(DeliveryChallan.dc_no == dc_no)
    )
    row = (await db.execute(stmt)).first()
    if row is None:
        raise QaInspectionError(f"No in-progress inspection found for {dc_no}")
    dc, vendor_name, inspection = row

    if inspection.inspection_status == "completed":
        raise QaInspectionError(f"DC {dc_no} inspection has already been completed")

    inspection.inspection_status = "completed"
    inspection.completed_at = datetime.now(timezone.utc)

    return {
        "dc_no": dc.dc_no,
        "vendor_name": vendor_name,
        "inspection_status": inspection.inspection_status,
        "qa_user": inspection.qa_user,
        "message": f"Inspection completed for {vendor_name}",
    }
