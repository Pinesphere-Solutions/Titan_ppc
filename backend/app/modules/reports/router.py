
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.reports.schemas import (
    DeviationReportItem,
    MovementHistoryEvent,
    QcReportItem,
    SapReportItem,
    StorageReportItem,
    VendorReportItem,
)
from app.modules.reports.service import (
    get_deviation_report,
    get_material_movement_history,
    get_qc_report,
    get_sap_report,
    get_storage_report,
    get_vendor_report,
)

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"module": "M14 Reports", "status": "not_yet_implemented"}


@router.get("/material-movement-history", response_model=list[MovementHistoryEvent])
async def material_movement_history(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[MovementHistoryEvent]:
    events = await get_material_movement_history(db)
    return [MovementHistoryEvent(**e) for e in events]


@router.get("/vendor-report", response_model=list[VendorReportItem])
async def vendor_report(db: Annotated[AsyncSession, Depends(get_db)]) -> list[VendorReportItem]:
    rows = await get_vendor_report(db)
    return [VendorReportItem(**r) for r in rows]


@router.get("/qc-report", response_model=list[QcReportItem])
async def qc_report(db: Annotated[AsyncSession, Depends(get_db)]) -> list[QcReportItem]:
    rows = await get_qc_report(db)
    return [QcReportItem(**r) for r in rows]


@router.get("/sap-report", response_model=list[SapReportItem])
async def sap_report(db: Annotated[AsyncSession, Depends(get_db)]) -> list[SapReportItem]:
    rows = await get_sap_report(db)
    return [SapReportItem(**r) for r in rows]


@router.get("/deviation-report", response_model=list[DeviationReportItem])
async def deviation_report(db: Annotated[AsyncSession, Depends(get_db)]) -> list[DeviationReportItem]:
    rows = await get_deviation_report(db)
    return [DeviationReportItem(**r) for r in rows]


@router.get("/storage-report", response_model=list[StorageReportItem])
async def storage_report(db: Annotated[AsyncSession, Depends(get_db)]) -> list[StorageReportItem]:
    rows = await get_storage_report(db)
    return [StorageReportItem(**r) for r in rows]
