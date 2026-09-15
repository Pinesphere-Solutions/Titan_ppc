
from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.dc_verification.models import DeliveryChallan
from app.modules.sap_outward.models import Dispatch


async def get_open_po_summary(db: AsyncSession) -> list[dict]:
    stmt = (
        select(Dispatch, DeliveryChallan)
        .outerjoin(DeliveryChallan, DeliveryChallan.dispatch_id == Dispatch.id)
        .where(Dispatch.po_number.is_not(None))
    )
    rows = (await db.execute(stmt)).all()

    groups: dict[tuple[str, str | None], dict] = defaultdict(
        lambda: {"po_quantity": 0, "received_qty": 0}
    )

    for dispatch, dc in rows:
        key = (dispatch.po_number, dispatch.po_line_item)
        group = groups[key]

        # po_quantity should be the same value on every dispatch sharing
        # this PO line — take it once rather than summing duplicates.
        if dispatch.po_quantity is not None:
            group["po_quantity"] = dispatch.po_quantity

        if dc is not None and dc.actual_front_case is not None and dc.actual_back_case is not None:
            group["received_qty"] += dc.actual_front_case + dc.actual_back_case

    return [
        {
            "po_number": po_number,
            "po_line_item": po_line_item,
            "po_quantity": g["po_quantity"],
            "received_qty": g["received_qty"],
            "pending_qty": max(g["po_quantity"] - g["received_qty"], 0),
        }
        for (po_number, po_line_item), g in sorted(groups.items())
    ]