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


# Material, Model, Rack and Bin masters (KT notes D1 sheet, M15) — added
# as simple code/name lookup tables, same shape as Vendor above. These are
# net-new: material_code/model appear only as free-text fields on
# transactional tables elsewhere (e.g. sap_outward.Dispatch), and
# rack/row/bin only as free-text fields on storage.StorageAssignment.
# There was no existing lookup table for any of them before this.


class MaterialMaster(Base, AuditMixin):
    __tablename__ = "material_master"

    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)


class ModelMaster(Base, AuditMixin):
    __tablename__ = "model_master"

    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)


class RackMaster(Base, AuditMixin):
    __tablename__ = "rack_master"

    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)


class BinMaster(Base, AuditMixin):
    __tablename__ = "bin_master"

    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
