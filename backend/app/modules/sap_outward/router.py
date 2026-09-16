

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.integrations.sap.dependency import get_sap_client
from app.integrations.sap.mapping import SAPMappingError, map_dispatched_material
from app.integrations.sap.open_po import get_open_po_summary
from app.modules.dc_verification.models import DeliveryChallan
from app.modules.masters.models import Vendor
from app.modules.sap_outward.models import Dispatch
from app.modules.sap_outward.schemas import DispatchListItem, OpenPoItem

router = APIRouter(prefix="/sap-outward", tags=["sap_outward"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"module": "M3 SAP Material Outward", "status": "not_yet_implemented"}


@router.get("/list", response_model=list[DispatchListItem])
async def list_dispatched_materials(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[DispatchListItem]:
    
    stmt = (
        select(
            Dispatch,
            Vendor.name,
            DeliveryChallan.dc_no,
            DeliveryChallan.verification_status,
            DeliveryChallan.qc_ack_status,
            DeliveryChallan.stock_level,
        )
        .join(Vendor, Dispatch.vendor_id == Vendor.id)
        .outerjoin(DeliveryChallan, DeliveryChallan.dispatch_id == Dispatch.id)
        .order_by(Dispatch.created_at.desc())
    )
    rows = (await db.execute(stmt)).all()

    return [
        DispatchListItem(
            sap_document_no=dispatch.sap_document_no,
            dc_no=dc_no,
            vendor_name=vendor_name,
            material_code=dispatch.material_code,
            model=dispatch.model,
            quantity_front_case=dispatch.quantity_front_case,
            quantity_back_case=dispatch.quantity_back_case,
            dispatch_date=dispatch.dispatch_date,
            verification_status=verification_status,
            qc_ack_status=qc_ack_status,
            stock_level=stock_level,
        )
        for dispatch, vendor_name, dc_no, verification_status, qc_ack_status, stock_level in rows
    ]


@router.post("/sync")
async def sync_dispatched_materials(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, object]:
    
    sap_client = get_sap_client()
    records = await sap_client.fetch_dispatched_materials()

    succeeded: list[str] = []
    failed: list[dict[str, str]] = []

    for record in records:
        try:
            dc = await map_dispatched_material(db, record)
            await db.commit()
            succeeded.append(dc.dc_no)
        except SAPMappingError as e:
            await db.rollback()
            failed.append({"sap_document_no": record.get("sap_document_no", "unknown"), "reason": str(e)})

    return {
        "total_records": len(records),
        "succeeded": succeeded,
        "failed": failed,
    }


@router.get("/open-po", response_model=list[OpenPoItem])
async def open_po_summary(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[OpenPoItem]:
    
    summary = await get_open_po_summary(db)
    return [OpenPoItem(**item) for item in summary]