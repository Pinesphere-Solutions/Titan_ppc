"""Business logic for M6 Physical Verification.

Per the KT process, this is a distinct scan-based confirmation step
that happens after Document Verification (M5 DC Verification) and
before SAP GRN / QC Acknowledgement — confirming the physically scanned
material/model/quantity match what M5 already checked against SAP.

Implemented as additive and non-blocking: eligible once M5 verification
is done (matched or excess, not pending/reverted), but does NOT gate
QC Acknowledgement (M8), since that flow is already tested and working
independently. Tightening the sequence into a hard prerequisite is a
follow-up decision, not made here — see the DeliveryChallan model
docstring for the related White Box simplification note.
"""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.dc_verification.models import DeliveryChallan
from app.modules.masters.models import Vendor
from app.modules.sap_outward.models import Dispatch


class PhysicalVerificationError(Exception):
    """Raised when physical verification can't be processed — unknown
    DC, DC not yet verified against SAP, or already physically verified."""


async def confirm_physical_verification(db: AsyncSession, dc_no: str, verified_by: str) -> dict:
    stmt = (
        select(DeliveryChallan, Vendor.name)
        .join(Dispatch, DeliveryChallan.dispatch_id == Dispatch.id)
        .join(Vendor, Dispatch.vendor_id == Vendor.id)
        .where(DeliveryChallan.dc_no == dc_no)
    )
    result = await db.execute(stmt)
    row = result.first()
    if row is None:
        raise PhysicalVerificationError(f"No delivery challan found for {dc_no}")

    dc, vendor_name = row

    if dc.verification_status not in ("verified",):
        raise PhysicalVerificationError(
            f"DC {dc_no} has verification status '{dc.verification_status}' — "
            "only a verified (matched or excess) DC can be physically verified"
        )

    if dc.physical_verification_status == "done":
        raise PhysicalVerificationError(f"DC {dc_no} has already been physically verified")

    dc.physical_verification_status = "done"
    dc.physical_verified_by = verified_by
    dc.physical_verified_at = datetime.now(timezone.utc)

    return {
        "dc_no": dc.dc_no,
        "vendor_name": vendor_name,
        "physical_verification_status": dc.physical_verification_status,
        "verified_by": verified_by,
        "message": f"Physical verification confirmed for {vendor_name}",
    }


async def list_pending_physical_verification(db: AsyncSession) -> list[dict]:
    stmt = (
        select(DeliveryChallan, Vendor.name, Dispatch.material_code)
        .join(Dispatch, DeliveryChallan.dispatch_id == Dispatch.id)
        .join(Vendor, Dispatch.vendor_id == Vendor.id)
        .where(DeliveryChallan.verification_status == "verified", DeliveryChallan.physical_verification_status == "pending")
    )
    rows = (await db.execute(stmt)).all()
    return [
        {
            "dc_no": dc.dc_no,
            "vendor_name": vendor_name,
            "material_code": material_code,
            "verification_status": dc.verification_status,
            "physical_verification_status": dc.physical_verification_status,
        }
        for dc, vendor_name, material_code in rows
    ]