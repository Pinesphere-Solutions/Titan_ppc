"""Business logic for the Gate Entry and Sub-con Receiving floor
stations. Both scan the same code — the DC number, printed as a
barcode on the White Box per the physical process — and log a
timestamped checkpoint against the matching DeliveryChallan.

Sub-con receipt can only be logged after gate entry, matching the
physical sequence (material must pass the gate before it reaches
sub-con). Each checkpoint can only be scanned once, same idempotency
pattern as DC Verification and QC Acknowledgement.
"""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.dc_verification.models import DeliveryChallan
from app.modules.masters.models import Vendor
from app.modules.sap_outward.models import Dispatch


class ReceivingError(Exception):
    """Raised when a scan can't be processed — unknown DC, already
    scanned at this checkpoint, or scanned out of sequence."""


async def _get_dc_with_vendor(db: AsyncSession, dc_no: str) -> tuple[DeliveryChallan, str]:
    stmt = (
        select(DeliveryChallan, Vendor.name)
        .join(Dispatch, DeliveryChallan.dispatch_id == Dispatch.id)
        .join(Vendor, Dispatch.vendor_id == Vendor.id)
        .where(DeliveryChallan.dc_no == dc_no)
    )
    result = await db.execute(stmt)
    row = result.first()
    if row is None:
        raise ReceivingError(f"No delivery challan found for scanned code {dc_no}")
    return row[0], row[1]


async def log_gate_entry(db: AsyncSession, dc_no: str, scanned_by: str) -> dict:
    dc, vendor_name = await _get_dc_with_vendor(db, dc_no)

    if dc.gate_entry_at is not None:
        raise ReceivingError(f"DC {dc_no} has already been scanned at the gate")

    dc.gate_entry_at = datetime.now(timezone.utc)
    dc.gate_entry_by = scanned_by

    return {
        "dc_no": dc.dc_no,
        "vendor_name": vendor_name,
        "message": f"Gate entry logged for {vendor_name}",
    }


async def log_subcon_receipt(db: AsyncSession, dc_no: str, scanned_by: str) -> dict:
    dc, vendor_name = await _get_dc_with_vendor(db, dc_no)

    if dc.gate_entry_at is None:
        raise ReceivingError(f"DC {dc_no} has not been scanned at the gate yet")

    if dc.subcon_received_at is not None:
        raise ReceivingError(f"DC {dc_no} has already been received at sub-con")

    dc.subcon_received_at = datetime.now(timezone.utc)
    dc.subcon_received_by = scanned_by

    return {
        "dc_no": dc.dc_no,
        "vendor_name": vendor_name,
        "message": f"Sub-con receiving logged for {vendor_name}",
    }


async def list_pending_categorization(db: AsyncSession) -> list[dict]:
    """DCs received at sub-con but not yet categorized — for the M4
    Material Receiving screen's dropdown."""
    stmt = (
        select(DeliveryChallan, Vendor.name, Dispatch.material_code)
        .join(Dispatch, DeliveryChallan.dispatch_id == Dispatch.id)
        .join(Vendor, Dispatch.vendor_id == Vendor.id)
        .where(DeliveryChallan.subcon_received_at.is_not(None), DeliveryChallan.receiving_category.is_(None))
    )
    rows = (await db.execute(stmt)).all()
    return [
        {
            "dc_no": dc.dc_no,
            "vendor_name": vendor_name,
            "material_code": material_code,
            "receiving_category": dc.receiving_category,
        }
        for dc, vendor_name, material_code in rows
    ]


VALID_RECEIVING_CATEGORIES = {"regular", "rework"}


async def set_receiving_category(db: AsyncSession, dc_no: str, category: str, set_by: str) -> dict:
    """M4 Material Receiving — categorize a DC as Regular or Rework once
    it has been received at sub-con. Additive/informational: does not
    gate DC Verification, since that flow is already tested and working
    without this step — see model docstring for the White Box
    simplification note this inherits."""
    if category not in VALID_RECEIVING_CATEGORIES:
        raise ReceivingError(
            f"Invalid receiving category '{category}' (expected one of {sorted(VALID_RECEIVING_CATEGORIES)})"
        )

    dc, vendor_name = await _get_dc_with_vendor(db, dc_no)

    if dc.subcon_received_at is None:
        raise ReceivingError(f"DC {dc_no} has not been received at sub-con yet")

    if dc.receiving_category is not None:
        raise ReceivingError(f"DC {dc_no} has already been categorized as {dc.receiving_category}")

    dc.receiving_category = category
    dc.receiving_category_set_by = set_by
    dc.receiving_category_set_at = datetime.now(timezone.utc)

    return {
        "dc_no": dc.dc_no,
        "vendor_name": vendor_name,
        "receiving_category": dc.receiving_category,
        "message": f"DC {dc_no} categorized as {category}",
    }