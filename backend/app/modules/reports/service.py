
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.deviations.models import Deviation
from app.modules.dc_verification.models import DeliveryChallan
from app.modules.masters.models import Vendor
from app.modules.sap_outward.models import Dispatch
from app.modules.sap_processing.models import SapMovement
from app.modules.storage.models import StorageAssignment

MOVEMENT_TYPE_LABELS = {
    "101": "Goods Receipt",
    "313": "Stock Transfer",
    "321": "Quality to Unrestricted Stock",
}


async def get_material_movement_history(db: AsyncSession) -> list[dict]:
    events: list[dict] = []

    # Base: every DC with its dispatch + vendor context.
    dc_stmt = (
        select(DeliveryChallan, Dispatch.material_code, Vendor.name)
        .join(Dispatch, DeliveryChallan.dispatch_id == Dispatch.id)
        .join(Vendor, Dispatch.vendor_id == Vendor.id)
    )
    dc_rows = (await db.execute(dc_stmt)).all()

    for dc, material_code, vendor_name in dc_rows:
        base = {"dc_no": dc.dc_no, "vendor_name": vendor_name, "material_code": material_code}

        if dc.actual_front_case is not None and dc.actual_back_case is not None:
            events.append(
                {
                    **base,
                    "event_type": "received",
                    "description": f"Received and verified — {dc.verification_status}",
                    "quantity": dc.actual_front_case + dc.actual_back_case,
                    "event_date": dc.updated_at.isoformat() if dc.updated_at else dc.created_at.isoformat(),
                }
            )

        if dc.qc_ack_status == "done" and dc.qc_acknowledged_at is not None:
            events.append(
                {
                    **base,
                    "event_type": "qc_acknowledged",
                    "description": f"QC acknowledged by {dc.qc_acknowledged_by} — moved to {dc.stock_level}",
                    "quantity": None,
                    "event_date": dc.qc_acknowledged_at.isoformat(),
                }
            )

    # SAP movement postings, joined back the same way.
    movement_stmt = (
        select(SapMovement, DeliveryChallan.dc_no, Dispatch.material_code, Vendor.name)
        .join(DeliveryChallan, SapMovement.dc_id == DeliveryChallan.id)
        .join(Dispatch, DeliveryChallan.dispatch_id == Dispatch.id)
        .join(Vendor, Dispatch.vendor_id == Vendor.id)
    )
    movement_rows = (await db.execute(movement_stmt)).all()

    for movement, dc_no, material_code, vendor_name in movement_rows:
        label = MOVEMENT_TYPE_LABELS.get(movement.movement_type, movement.movement_type)
        events.append(
            {
                "dc_no": dc_no,
                "vendor_name": vendor_name,
                "material_code": material_code,
                "event_type": "sap_movement",
                "description": f"SAP {movement.movement_type} — {label} ({movement.material_document_no})",
                "quantity": None,
                "event_date": movement.posting_date or (movement.created_at.isoformat() if movement.created_at else ""),
            }
        )

    events.sort(key=lambda e: (e["dc_no"], e["event_date"]))
    return events


async def get_vendor_report(db: AsyncSession) -> list[dict]:
    """Per-vendor rollup. Aggregated in Python rather than SQL, matching
    the rest of this module — dataset size here doesn't warrant it, and
    it keeps this readable alongside the other report functions."""
    dispatch_stmt = select(Dispatch.vendor_id, Vendor.code, Vendor.name).join(
        Vendor, Dispatch.vendor_id == Vendor.id
    )
    dispatch_rows = (await db.execute(dispatch_stmt)).all()

    dc_stmt = (
        select(DeliveryChallan, Dispatch.vendor_id)
        .join(Dispatch, DeliveryChallan.dispatch_id == Dispatch.id)
    )
    dc_rows = (await db.execute(dc_stmt)).all()

    deviation_stmt = (
        select(Deviation, Dispatch.vendor_id)
        .join(DeliveryChallan, Deviation.dc_id == DeliveryChallan.id)
        .join(Dispatch, DeliveryChallan.dispatch_id == Dispatch.id)
    )
    deviation_rows = (await db.execute(deviation_stmt)).all()

    vendors: dict[str, dict] = {}
    for vendor_id, code, name in dispatch_rows:
        key = str(vendor_id)
        vendor = vendors.setdefault(
            key,
            {
                "vendor_code": code,
                "vendor_name": name,
                "total_dispatches": 0,
                "total_dcs": 0,
                "pending_qc": 0,
                "total_deviations": 0,
            },
        )
        vendor["total_dispatches"] += 1

    for dc, vendor_id in dc_rows:
        key = str(vendor_id)
        if key not in vendors:
            continue
        vendors[key]["total_dcs"] += 1
        if dc.qc_ack_status != "done":
            vendors[key]["pending_qc"] += 1

    for _deviation, vendor_id in deviation_rows:
        key = str(vendor_id)
        if key in vendors:
            vendors[key]["total_deviations"] += 1

    return sorted(vendors.values(), key=lambda v: v["vendor_code"])


async def get_qc_report(db: AsyncSession) -> list[dict]:
    stmt = (
        select(DeliveryChallan, Dispatch.material_code, Vendor.name)
        .join(Dispatch, DeliveryChallan.dispatch_id == Dispatch.id)
        .join(Vendor, Dispatch.vendor_id == Vendor.id)
        .order_by(DeliveryChallan.dc_no)
    )
    rows = (await db.execute(stmt)).all()

    return [
        {
            "dc_no": dc.dc_no,
            "vendor_name": vendor_name,
            "material_code": material_code,
            "qc_ack_status": dc.qc_ack_status,
            "qc_acknowledged_by": dc.qc_acknowledged_by,
            "qc_acknowledged_at": dc.qc_acknowledged_at,
            "stock_level": dc.stock_level,
        }
        for dc, material_code, vendor_name in rows
    ]


async def get_sap_report(db: AsyncSession) -> list[dict]:
    stmt = (
        select(SapMovement, DeliveryChallan.dc_no, Dispatch.material_code, Vendor.name)
        .join(DeliveryChallan, SapMovement.dc_id == DeliveryChallan.id)
        .join(Dispatch, DeliveryChallan.dispatch_id == Dispatch.id)
        .join(Vendor, Dispatch.vendor_id == Vendor.id)
        .order_by(SapMovement.material_document_no)
    )
    rows = (await db.execute(stmt)).all()

    return [
        {
            "dc_no": dc_no,
            "vendor_name": vendor_name,
            "material_code": material_code,
            "material_document_no": movement.material_document_no,
            "movement_type": movement.movement_type,
            "movement_label": MOVEMENT_TYPE_LABELS.get(movement.movement_type, movement.movement_type),
            "posting_date": movement.posting_date,
            "sync_status": movement.sync_status,
        }
        for movement, dc_no, material_code, vendor_name in rows
    ]


async def get_deviation_report(db: AsyncSession) -> list[dict]:
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


async def get_storage_report(db: AsyncSession) -> list[dict]:
    stmt = (
        select(StorageAssignment, DeliveryChallan.dc_no, Dispatch.material_code, Vendor.name)
        .join(DeliveryChallan, StorageAssignment.dc_id == DeliveryChallan.id)
        .join(Dispatch, DeliveryChallan.dispatch_id == Dispatch.id)
        .join(Vendor, Dispatch.vendor_id == Vendor.id)
        .order_by(StorageAssignment.stored_at.desc())
    )
    rows = (await db.execute(stmt)).all()

    return [
        {
            "dc_no": dc_no,
            "vendor_name": vendor_name,
            "material_code": material_code,
            "rack": assignment.rack,
            "row": assignment.row,
            "bin": assignment.bin,
            "storage_location": assignment.storage_location,
            "stored_by": assignment.stored_by,
            "stored_at": assignment.stored_at,
        }
        for assignment, dc_no, material_code, vendor_name in rows
    ]
