"""ORM models for M10 PPC Collection and Verification. See ERD in architecture doc Section 5.3.

Per KT notes (Module-Wireframe-Draft steps 39-42, D1 sheet M10): after the
Sub-con team completes UD Post (SAP 313, tracked as
DeliveryChallan.ud_post_status), the material is placed in a Sub-con
Tray. The PPC team member collects the material from that tray and
re-verifies it in a single action ("Collect Material" + "Verify
Material" per D1's function list) — this is what officially ends the
Sub-con process.

Modeled as its own table (like SapMovement) rather than extra columns on
DeliveryChallan, since Tray No is genuinely new information tied to a
distinct physical event, not just another status flag.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.models_mixin import AuditMixin
from app.modules.dc_verification.models import DeliveryChallan


class PpcCollection(Base, AuditMixin):
    __tablename__ = "ppc_collection"

    dc_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("delivery_challan.id"), nullable=False, unique=True
    )
    tray_no: Mapped[str] = mapped_column(String(50), nullable=False)
    verification_status: Mapped[str] = mapped_column(String(20), default="verified", nullable=False)
    collected_by: Mapped[str] = mapped_column(String(100), nullable=False)
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    delivery_challan: Mapped["DeliveryChallan"] = relationship()
