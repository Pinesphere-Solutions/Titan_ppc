"""ORM models for M13 Storage Management. See ERD in architecture doc Section 5.3.

Per KT notes (D1 sheet M13; Module-Wireframe-Draft step 51 — "A printout
is taken, signatures are obtained, and the material is moved to Storage
after completion of the SAP 313 process"): once ZQMTL1 Processing (M12)
has posted SAP 313, the material is ready to be assigned a rack/row/bin
and stored. D1's function list ("Assign Rack, Assign Bin, QR Scan,
Location Search, Store Material") combines the assign+store actions
into one confirm step, consistent with the M10/M12 precedent — and per
the same DC-level simplification used throughout this build (one DC
assumed to correspond to one physical White Box), "QR Scan" is DC
selection rather than a separate physical scan.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.models_mixin import AuditMixin
from app.modules.dc_verification.models import DeliveryChallan


class StorageAssignment(Base, AuditMixin):
    __tablename__ = "storage_assignment"

    dc_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("delivery_challan.id"), nullable=False, unique=True
    )
    rack: Mapped[str] = mapped_column(String(50), nullable=False)
    row: Mapped[str] = mapped_column(String(50), nullable=False)
    bin: Mapped[str] = mapped_column(String(50), nullable=False)
    storage_location: Mapped[str] = mapped_column(String(100), nullable=False)
    stored_by: Mapped[str] = mapped_column(String(100), nullable=False)
    stored_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    delivery_challan: Mapped["DeliveryChallan"] = relationship()
