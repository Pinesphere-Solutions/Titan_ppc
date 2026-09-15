
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.models_mixin import AuditMixin


class Vendor(Base, AuditMixin):
    __tablename__ = "vendor"

    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    # Nullable — SAP doesn't currently send vendor email (see Titan SAP Data
    # Mapping doc, Section 3). Populated manually via Masters (M15) for now,
    # until/unless it's confirmed as part of the SAP Vendor Master payload.
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)