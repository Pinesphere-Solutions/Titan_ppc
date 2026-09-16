
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.models_mixin import AuditMixin
from app.modules.sap_outward.models import Dispatch


class DeliveryChallan(Base, AuditMixin):
    __tablename__ = "delivery_challan"

    dispatch_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("dispatch.id"), nullable=False)
    dc_no: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    line_item_count: Mapped[int] = mapped_column(nullable=False)
    verification_status: Mapped[str] = mapped_column(String(30), default="pending", nullable=False)

    # Persisted at verification time — previously computed but not saved,
    # which blocked any "received-to-date" calculation (e.g. Open PO /
    # Pending Quantity). Null until the DC is actually verified.
    actual_front_case: Mapped[int | None] = mapped_column(nullable=True)
    actual_back_case: Mapped[int | None] = mapped_column(nullable=True)

    # M8 QC Acknowledgement
    qc_ack_status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    qc_acknowledged_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    qc_acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Level 2 -> Level 1 stock movement, triggered by QC acknowledgement
    stock_level: Mapped[str] = mapped_column(String(20), default="level_2", nullable=False)

    # M9 SAP Processing — UD Post triggered once at Level 1
    ud_post_status: Mapped[str] = mapped_column(String(20), default="not_posted", nullable=False)

    dispatch: Mapped["Dispatch"] = relationship()