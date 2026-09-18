
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

    # Floor kiosk scan checkpoints — Gate Security scanning material in
    # at the gate, then Sub-con scanning it in on receipt. Same audit
    # pattern as qc_acknowledged_at/by. Both nullable until scanned.
    gate_entry_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    gate_entry_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    subcon_received_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    subcon_received_by: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # M4 Material Receiving — categorization done at/after Sub-con receipt.
    # Simplification note: the KT process describes this keyed on a
    # physical "White Box" UID scanned separately from the DC. This
    # build tracks everything at the DC level instead (one DC assumed
    # to correspond to one physical box) — flagged to Kauverysree,
    # pending confirmation of whether that assumption always holds.
    receiving_category: Mapped[str | None] = mapped_column(String(20), nullable=True)  # "regular" | "rework"
    receiving_category_set_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    receiving_category_set_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # M6 Physical Verification — per the KT process this is a distinct
    # scan-based confirmation step after Document Verification (M5) and
    # before SAP GRN/QC Acknowledgement. Implemented here as additive
    # and non-blocking (does NOT gate QC Acknowledgement) so it doesn't
    # retroactively break the already-tested M8 flow — tightening this
    # into a hard prerequisite is a follow-up decision, not made here.
    physical_verification_status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    physical_verified_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    physical_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    dispatch: Mapped["Dispatch"] = relationship()