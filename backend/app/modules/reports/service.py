

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.dc_verification.models import DeliveryChallan
from app.modules.masters.models import Vendor
from app.modules.sap_outward.models import Dispatch
from app.modules.sap_processing.models import SapMovement

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