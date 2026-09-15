"""Business logic for M5 DC Verification.

Implements the confirmed Excess/Less comparison from the KT process
notes: "During verification, the material quantity is identified as
Excess or Less. Excess Case: no issues, process continues. Less Case:
the received DC is reverted back to the Vendor." See also Titan SAP
Data Mapping design doc, Section 6.2 (deviation flow).

A DC can only be verified once. If it's already been verified (status
is not "pending"), this raises rather than silently re-processing —
conflict handling for re-verification of an already-progressed DC is
one of the open questions in the SAP mapping doc (Section 11), so this
layer deliberately refuses rather than guessing at a resolution.
"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.dc_verification.models import DeliveryChallan
from app.modules.deviations.models import Deviation
from app.modules.masters.models import Vendor
from app.modules.sap_outward.models import Dispatch


class DcVerificationError(Exception):
    """Raised for verification requests that can't be processed —
    unknown DC, or a DC that's already been verified."""


async def verify_delivery_challan(
    db: AsyncSession, dc_no: str, actual_front_case: int, actual_back_case: int
) -> dict:
    result = await db.execute(select(DeliveryChallan).where(DeliveryChallan.dc_no == dc_no))
    dc = result.scalar_one_or_none()
    if dc is None:
        raise DcVerificationError(f"No delivery challan found with DC number {dc_no}")

    if dc.verification_status != "pending":
        raise DcVerificationError(
            f"DC {dc_no} has already been verified (status: {dc.verification_status}); "
            "re-verification is not supported"
        )

    dispatch_result = await db.execute(select(Dispatch).where(Dispatch.id == dc.dispatch_id))
    dispatch = dispatch_result.scalar_one_or_none()
    if dispatch is None:
        # Shouldn't happen given the FK, but fail loudly rather than silently
        # comparing against None.
        raise DcVerificationError(f"Dispatch record missing for DC {dc_no} — data integrity issue")

    vendor_result = await db.execute(select(Vendor).where(Vendor.id == dispatch.vendor_id))
    vendor = vendor_result.scalar_one_or_none()
    vendor_email = vendor.email if vendor else None

    expected_qty = (dispatch.quantity_front_case or 0) + (dispatch.quantity_back_case or 0)
    actual_qty = actual_front_case + actual_back_case

    # Persisted regardless of outcome — this is what makes "received-to-date"
    # calculations (e.g. Open PO / Pending Quantity) possible. Previously
    # computed here but never saved, which blocked that downstream use.
    dc.actual_front_case = actual_front_case
    dc.actual_back_case = actual_back_case

    deviation_id: uuid.UUID | None = None

    if actual_qty < expected_qty:
        # Less Case — revert the DC, create a deviation record.
        dc.verification_status = "reverted"
        deviation = Deviation(
            dc_id=dc.id,
            deviation_type="less",
            expected_qty=expected_qty,
            actual_qty=actual_qty,
            difference_qty=expected_qty - actual_qty,
        )
        db.add(deviation)
        await db.flush()
        deviation_id = deviation.id
        outcome = "less"
    elif actual_qty > expected_qty:
        # Excess Case — no issue, process continues (per confirmed business rule).
        dc.verification_status = "verified"
        outcome = "excess"
    else:
        dc.verification_status = "verified"
        outcome = "matched"

    return {
        "dc_no": dc.dc_no,
        "expected_qty": expected_qty,
        "actual_qty": actual_qty,
        "result": outcome,
        "verification_status": dc.verification_status,
        "deviation_created": deviation_id is not None,
        "deviation_id": str(deviation_id) if deviation_id else None,
        "vendor_email": vendor_email,  # internal use only — not part of the API response schema
    }