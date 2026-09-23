"""ORM models for M12 ZQMTL1 Processing. See ERD in architecture doc Section 5.3.

Per KT notes (Module-Wireframe-Draft steps 46-51, D1 sheet M12): once QA
Inspection (M11) is complete, the material moves to "Level 1 (ZQMTL1)"
for a material check, a second UD Post, and a second SAP 313 transfer —
distinct from the UD Post/SAP 313 already done earlier at M8/M9.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.models_mixin import AuditMixin
from app.modules.dc_verification.models import DeliveryChallan


class Zqmtl1Processing(Base, AuditMixin):
    __tablename__ = "zqmtl1_processing"

    dc_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("delivery_challan.id"), nullable=False, unique=True
    )
    zqmtl1_status: Mapped[str] = mapped_column(String(20), default="checked", nullable=False)
    sap_status: Mapped[str] = mapped_column(String(20), default="not_posted", nullable=False)
    processed_by: Mapped[str] = mapped_column(String(100), nullable=False)
    processed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    delivery_challan: Mapped["DeliveryChallan"] = relationship()
