
import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.models_mixin import AuditMixin
from app.modules.dc_verification.models import DeliveryChallan


class SapMovement(Base, AuditMixin):
    __tablename__ = "sap_movement"

    dc_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("delivery_challan.id"), nullable=False)
    material_document_no: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    movement_type: Mapped[str] = mapped_column(String(10), nullable=False)  # "101" | "313" | "321"
    posting_date: Mapped[str | None] = mapped_column(String(20), nullable=True)  # [OPEN] format per mapping doc Sec 3
    sync_status: Mapped[str] = mapped_column(String(20), default="synced", nullable=False)

    delivery_challan: Mapped["DeliveryChallan"] = relationship()