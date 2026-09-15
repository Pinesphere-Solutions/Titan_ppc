
import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.models_mixin import AuditMixin
from app.modules.dc_verification.models import DeliveryChallan


class Deviation(Base, AuditMixin):
    __tablename__ = "deviation"

    dc_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("delivery_challan.id"), nullable=False)
    deviation_type: Mapped[str] = mapped_column(String(20), nullable=False)  # "less" (only type created today)
    expected_qty: Mapped[int] = mapped_column(nullable=False)
    actual_qty: Mapped[int] = mapped_column(nullable=False)
    difference_qty: Mapped[int] = mapped_column(nullable=False)
    mail_status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    vendor_status: Mapped[str] = mapped_column(String(20), default="awaiting_response", nullable=False)

    delivery_challan: Mapped["DeliveryChallan"] = relationship()