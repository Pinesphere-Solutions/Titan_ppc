"""Business logic for M10 PPC Collection and Verification.

Per the KT process (Module-Wireframe-Draft steps 39-42): after Sub-con
completes UD Post (SAP 313) at M9, the Sub-con team places the material
in a Sub-con Tray. The PPC team member collects the material from that
tray, re-verifies it once more, and confirms collection — this is what
officially ends the Sub-con process. D1's function list combines
"Collect Material" and "Verify Material" into one action, so this
module implements a single confirm step rather than two separate
stages.

Eligible once UD Post is done (ud_post_status == "posted"); not
eligible before that, and not repeatable once already collected.
"""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.dc_verification.models import DeliveryChallan
from app.modules.masters.models import Vendor
from app.modules.ppc_collection.models import PpcCollection
from app.modules.sap_outward.models import Dispatch


class PpcCollectionError(Exception):
    """Raised when collection can't be processed — unknown DC, UD Post
    not yet done, or already collected."""


async def collect_material(db: AsyncSession, dc_no: str, tray_no: str, collected_by: str) -> dict:
    stmt = (
        select(DeliveryChallan, Vendor.name)
        .join(Dispatch, DeliveryChallan.dispatch_id == Dispatch.id)
        .join(Vendor, Dispatch.vendor_id == Vendor.id)
        .where(DeliveryChallan.dc_no == dc_no)
    )
    row = (await db.execute(stmt)).first()
    if row is None:
        raise PpcCollectionError(f"No delivery challan found for {dc_no}")

    dc, vendor_name = row

    if dc.ud_post_status != "posted":
        raise PpcCollectionError(
            f"DC {dc_no} has UD Post status '{dc.ud_post_status}' — "
            "material must be UD Posted (SAP 313) before PPC collection"
        )

    existing = await db.execute(select(PpcCollection).where(PpcCollection.dc_id == dc.id))
    if existing.scalar_one_or_none() is not None:
        raise PpcCollectionError(f"DC {dc_no} has already been collected by PPC")

    collection = PpcCollection(
        dc_id=dc.id,
        tray_no=tray_no,
        verification_status="verified",
        collected_by=collected_by,
        collected_at=datetime.now(timezone.utc),
    )
    db.add(collection)

    return {
        "dc_no": dc.dc_no,
        "tray_no": tray_no,
        "vendor_name": vendor_name,
        "verification_status": collection.verification_status,
        "collected_by": collected_by,
        "message": f"Material collected from tray {tray_no} for {vendor_name}",
    }


async def list_pending_collection(db: AsyncSession) -> list[dict]:
    stmt = (
        select(DeliveryChallan, Vendor.name, Dispatch.material_code, Dispatch.model, Dispatch.quantity)
        .join(Dispatch, DeliveryChallan.dispatch_id == Dispatch.id)
        .join(Vendor, Dispatch.vendor_id == Vendor.id)
        .outerjoin(PpcCollection, PpcCollection.dc_id == DeliveryChallan.id)
        .where(DeliveryChallan.ud_post_status == "posted", PpcCollection.id.is_(None))
    )
    rows = (await db.execute(stmt)).all()
    return [
        {
            "dc_no": dc.dc_no,
            "vendor_name": vendor_name,
            "material_code": material_code,
            "model": model,
            "quantity": quantity,
            "ud_post_status": dc.ud_post_status,
        }
        for dc, vendor_name, material_code, model, quantity in rows
    ]
