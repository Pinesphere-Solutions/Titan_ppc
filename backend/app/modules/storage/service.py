"""Business logic for M13 Storage Management.

Per KT notes (D1 sheet M13; Module-Wireframe-Draft step 51): once
ZQMTL1 Processing (M12) has posted SAP 313, the material is ready to
be assigned a rack/row/bin and stored — the final step of the
tracked pipeline. "Assign Rack", "Assign Bin" and "Store Material"
are combined into one confirm action (same precedent as M10/M12).
"Location Search" is served by list_stored's optional search filter.

Eligible once ZQMTL1 processing is done (sap_status == "posted"); not
eligible before that, and not repeatable once already stored.
"""

from datetime import datetime, timezone

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.dc_verification.models import DeliveryChallan
from app.modules.masters.models import Vendor
from app.modules.sap_outward.models import Dispatch
from app.modules.storage.models import StorageAssignment
from app.modules.zqmtl1.models import Zqmtl1Processing


class StorageError(Exception):
    """Raised when storage assignment can't be processed — unknown DC,
    ZQMTL1/SAP 313 not yet posted, or already stored."""


async def list_pending_storage(db: AsyncSession) -> list[dict]:
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
        .join(Zqmtl1Processing, Zqmtl1Processing.dc_id == DeliveryChallan.id)
        .outerjoin(StorageAssignment, StorageAssignment.dc_id == DeliveryChallan.id)
        .where(Zqmtl1Processing.sap_status == "posted", StorageAssignment.id.is_(None))
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


async def assign_storage(
    db: AsyncSession,
    dc_no: str,
    rack: str,
    row: str,
    bin: str,
    storage_location: str,
    stored_by: str,
) -> dict:
    stmt = (
        select(DeliveryChallan, Vendor.name)
        .join(Dispatch, DeliveryChallan.dispatch_id == Dispatch.id)
        .join(Vendor, Dispatch.vendor_id == Vendor.id)
        .where(DeliveryChallan.dc_no == dc_no)
    )
    result = await db.execute(stmt)
    row_data = result.first()
    if row_data is None:
        raise StorageError(f"No delivery challan found for {dc_no}")
    dc, vendor_name = row_data

    zqmtl1_result = await db.execute(select(Zqmtl1Processing).where(Zqmtl1Processing.dc_id == dc.id))
    zqmtl1 = zqmtl1_result.scalar_one_or_none()
    if zqmtl1 is None or zqmtl1.sap_status != "posted":
        raise StorageError(f"DC {dc_no} has not completed ZQMTL1 / SAP 313 posting yet — cannot store")

    existing = await db.execute(select(StorageAssignment).where(StorageAssignment.dc_id == dc.id))
    if existing.scalar_one_or_none() is not None:
        raise StorageError(f"DC {dc_no} has already been stored")

    assignment = StorageAssignment(
        dc_id=dc.id,
        rack=rack,
        row=row,
        bin=bin,
        storage_location=storage_location,
        stored_by=stored_by,
        stored_at=datetime.now(timezone.utc),
    )
    db.add(assignment)

    return {
        "dc_no": dc.dc_no,
        "vendor_name": vendor_name,
        "rack": rack,
        "row": row,
        "bin": bin,
        "storage_location": storage_location,
        "stored_by": stored_by,
        "message": f"Material stored for {vendor_name} at {storage_location} (Rack {rack}, Row {row}, Bin {bin})",
    }


async def list_stored(db: AsyncSession, search: str | None = None) -> list[dict]:
    stmt = (
        select(StorageAssignment, DeliveryChallan.dc_no, Vendor.name, Dispatch.material_code, Dispatch.model)
        .join(DeliveryChallan, StorageAssignment.dc_id == DeliveryChallan.id)
        .join(Dispatch, DeliveryChallan.dispatch_id == Dispatch.id)
        .join(Vendor, Dispatch.vendor_id == Vendor.id)
        .order_by(StorageAssignment.stored_at.desc())
    )
    if search:
        pattern = f"%{search}%"
        stmt = stmt.where(
            or_(
                DeliveryChallan.dc_no.ilike(pattern),
                StorageAssignment.rack.ilike(pattern),
                StorageAssignment.row.ilike(pattern),
                StorageAssignment.bin.ilike(pattern),
                StorageAssignment.storage_location.ilike(pattern),
            )
        )
    rows = (await db.execute(stmt)).all()
    return [
        {
            "dc_no": dc_no,
            "vendor_name": vendor_name,
            "material_code": material_code,
            "model": model,
            "rack": assignment.rack,
            "row": assignment.row,
            "bin": assignment.bin,
            "storage_location": assignment.storage_location,
            "stored_by": assignment.stored_by,
            "stored_at": assignment.stored_at,
        }
        for assignment, dc_no, vendor_name, material_code, model in rows
    ]
