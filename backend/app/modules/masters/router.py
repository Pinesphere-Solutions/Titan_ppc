
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import CurrentUser, get_current_user
from app.modules.masters.schemas import (
    BinCreateRequest,
    BinItem,
    MaterialCreateRequest,
    MaterialItem,
    ModelCreateRequest,
    ModelItem,
    RackCreateRequest,
    RackItem,
    VendorEmailUpdateRequest,
    VendorItem,
)
from app.modules.masters.service import (
    MastersError,
    create_bin,
    create_material,
    create_model,
    create_rack,
    list_bins,
    list_materials,
    list_models,
    list_racks,
    list_vendors,
    update_vendor_email,
)

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


# --- Material Master --------------------------------------------------

@router.get("/materials", response_model=list[MaterialItem])
async def get_materials(db: Annotated[AsyncSession, Depends(get_db)]) -> list[MaterialItem]:
    materials = await list_materials(db)
    return [MaterialItem(code=m.code, name=m.name) for m in materials]


@router.post("/materials", response_model=MaterialItem)
async def add_material(
    payload: MaterialCreateRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> MaterialItem:
    try:
        material = await create_material(db, payload.code, payload.name)
        await db.commit()
    except MastersError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e

    return MaterialItem(code=material.code, name=material.name)


# --- Model Master -------------------------------------------------------

@router.get("/models", response_model=list[ModelItem])
async def get_models(db: Annotated[AsyncSession, Depends(get_db)]) -> list[ModelItem]:
    models = await list_models(db)
    return [ModelItem(code=m.code, name=m.name) for m in models]


@router.post("/models", response_model=ModelItem)
async def add_model(
    payload: ModelCreateRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ModelItem:
    try:
        model = await create_model(db, payload.code, payload.name)
        await db.commit()
    except MastersError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e

    return ModelItem(code=model.code, name=model.name)


# --- Rack Master --------------------------------------------------------

@router.get("/racks", response_model=list[RackItem])
async def get_racks(db: Annotated[AsyncSession, Depends(get_db)]) -> list[RackItem]:
    racks = await list_racks(db)
    return [RackItem(code=r.code, name=r.name) for r in racks]


@router.post("/racks", response_model=RackItem)
async def add_rack(
    payload: RackCreateRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> RackItem:
    try:
        rack = await create_rack(db, payload.code, payload.name)
        await db.commit()
    except MastersError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e

    return RackItem(code=rack.code, name=rack.name)


# --- Bin Master ----------------------------------------------------------

@router.get("/bins", response_model=list[BinItem])
async def get_bins(db: Annotated[AsyncSession, Depends(get_db)]) -> list[BinItem]:
    bins_ = await list_bins(db)
    return [BinItem(code=b.code, name=b.name) for b in bins_]


@router.post("/bins", response_model=BinItem)
async def add_bin(
    payload: BinCreateRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> BinItem:
    try:
        bin_ = await create_bin(db, payload.code, payload.name)
        await db.commit()
    except MastersError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e

    return BinItem(code=bin_.code, name=bin_.name)
