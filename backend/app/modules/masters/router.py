
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import CurrentUser, get_current_user
from app.modules.masters.schemas import VendorEmailUpdateRequest, VendorItem
from app.modules.masters.service import MastersError, list_vendors, update_vendor_email

router = APIRouter(prefix="/masters", tags=["masters"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"module": "M15 Masters", "status": "not_yet_implemented"}


@router.get("/vendors", response_model=list[VendorItem])
async def get_vendors(db: Annotated[AsyncSession, Depends(get_db)]) -> list[VendorItem]:
    vendors = await list_vendors(db)
    return [VendorItem(code=v.code, name=v.name, email=v.email) for v in vendors]


@router.patch("/vendors/{vendor_code}/email", response_model=VendorItem)
async def patch_vendor_email(
    vendor_code: str,
    payload: VendorEmailUpdateRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> VendorItem:
    try:
        vendor = await update_vendor_email(db, vendor_code, payload.email)
        await db.commit()
    except MastersError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e

    return VendorItem(code=vendor.code, name=vendor.name, email=vendor.email)