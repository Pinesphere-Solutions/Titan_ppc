
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.masters.models import BinMaster, MaterialMaster, ModelMaster, RackMaster, Vendor


class MastersError(Exception):
    """Raised when a requested master record doesn't exist, or a new one
    duplicates an existing code — the router converts this to a 400/404."""


async def list_vendors(db: AsyncSession) -> list[Vendor]:
    result = await db.execute(select(Vendor).order_by(Vendor.code))
    return list(result.scalars().all())


async def update_vendor_email(db: AsyncSession, vendor_code: str, email: str) -> Vendor:
    result = await db.execute(select(Vendor).where(Vendor.code == vendor_code))
    vendor = result.scalar_one_or_none()
    if vendor is None:
        raise MastersError(f"No vendor found with code {vendor_code}")

    vendor.email = email
    return vendor


# --- Material Master --------------------------------------------------

async def list_materials(db: AsyncSession) -> list[MaterialMaster]:
    result = await db.execute(select(MaterialMaster).order_by(MaterialMaster.code))
    return list(result.scalars().all())


async def create_material(db: AsyncSession, code: str, name: str) -> MaterialMaster:
    existing = await db.execute(select(MaterialMaster).where(MaterialMaster.code == code))
    if existing.scalar_one_or_none() is not None:
        raise MastersError(f"Material code '{code}' already exists.")

    material = MaterialMaster(code=code, name=name)
    db.add(material)
    try:
        await db.flush()
    except IntegrityError as e:
        raise MastersError(f"Material code '{code}' already exists.") from e

    return material


# --- Model Master -------------------------------------------------------

async def list_models(db: AsyncSession) -> list[ModelMaster]:
    result = await db.execute(select(ModelMaster).order_by(ModelMaster.code))
    return list(result.scalars().all())


async def create_model(db: AsyncSession, code: str, name: str) -> ModelMaster:
    existing = await db.execute(select(ModelMaster).where(ModelMaster.code == code))
    if existing.scalar_one_or_none() is not None:
        raise MastersError(f"Model code '{code}' already exists.")

    model = ModelMaster(code=code, name=name)
    db.add(model)
    try:
        await db.flush()
    except IntegrityError as e:
        raise MastersError(f"Model code '{code}' already exists.") from e

    return model


# --- Rack Master --------------------------------------------------------

async def list_racks(db: AsyncSession) -> list[RackMaster]:
    result = await db.execute(select(RackMaster).order_by(RackMaster.code))
    return list(result.scalars().all())


async def create_rack(db: AsyncSession, code: str, name: str) -> RackMaster:
    existing = await db.execute(select(RackMaster).where(RackMaster.code == code))
    if existing.scalar_one_or_none() is not None:
        raise MastersError(f"Rack code '{code}' already exists.")

    rack = RackMaster(code=code, name=name)
    db.add(rack)
    try:
        await db.flush()
    except IntegrityError as e:
        raise MastersError(f"Rack code '{code}' already exists.") from e

    return rack


# --- Bin Master ----------------------------------------------------------

async def list_bins(db: AsyncSession) -> list[BinMaster]:
    result = await db.execute(select(BinMaster).order_by(BinMaster.code))
    return list(result.scalars().all())


async def create_bin(db: AsyncSession, code: str, name: str) -> BinMaster:
    existing = await db.execute(select(BinMaster).where(BinMaster.code == code))
    if existing.scalar_one_or_none() is not None:
        raise MastersError(f"Bin code '{code}' already exists.")

    bin_ = BinMaster(code=code, name=name)
    db.add(bin_)
    try:
        await db.flush()
    except IntegrityError as e:
        raise MastersError(f"Bin code '{code}' already exists.") from e

    return bin_
