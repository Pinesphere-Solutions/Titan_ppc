
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.masters.models import Vendor


class MastersError(Exception):
    """Raised when a requested vendor doesn't exist."""


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