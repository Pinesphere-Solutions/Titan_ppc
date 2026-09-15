
import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.models_mixin import AuditMixin
from app.modules.masters.models import Vendor


class Dispatch(Base, AuditMixin):
    __tablename__ = "dispatch"

    vendor_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("vendor.id"), nullable=False)
    sap_document_no: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    material_code: Mapped[str] = mapped_column(String(100), nullable=False)
    model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    quantity_front_case: Mapped[int | None] = mapped_column(nullable=True)
    quantity_back_case: Mapped[int | None] = mapped_column(nullable=True)
    dispatch_date: Mapped[str | None] = mapped_column(String(20), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="dispatched", nullable=False)

    # [OPEN] per SAP mapping doc Section 12 — added now since PO data is
    # part of the confirmed data request, even though exact field shape
    # from SAP isn't confirmed yet.
    po_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    po_line_item: Mapped[str | None] = mapped_column(String(20), nullable=True)
    # PO's total ordered quantity — needed to compute Open PO / Pending
    # Quantity (SAP mapping doc Section 5, item marked [OPEN]). Decision:
    # computed app-side (PO qty minus received-to-date), not stored
    # directly from SAP, so our pending count stays consistent with our
    # own verification records.
    po_quantity: Mapped[int | None] = mapped_column(nullable=True)

    vendor: Mapped["Vendor"] = relationship()