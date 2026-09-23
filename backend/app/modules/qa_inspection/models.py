"""ORM models for M11 QA Inspection. See ERD in architecture doc Section 5.3.

Per KT notes (Module-Wireframe-Draft steps 43-46, D1 sheet M11): after
PPC Collection (M10) ends the Sub-con process, the material is pending
with a separate Quality Team under "Waiting for Inspection" status.
That team starts and completes the inspection before the material can
move on to ZQMTL1 (M12).

A DC with a PpcCollection record but no QaInspection row is implicitly
"waiting for inspection" — the row here is only created once inspection
actually starts (see service.py), at which point status moves to
"in_progress" and finally "completed".
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.models_mixin import AuditMixin
from app.modules.dc_verification.models import DeliveryChallan


class QaInspection(Base, AuditMixin):
    __tablename__ = "qa_inspection"

    dc_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("delivery_challan.id"), nullable=False, unique=True
    )
    inspection_status: Mapped[str] = mapped_column(String(20), default="in_progress", nullable=False)
    qa_user: Mapped[str] = mapped_column(String(100), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    delivery_challan: Mapped["DeliveryChallan"] = relationship()
