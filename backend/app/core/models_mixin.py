"""Shared audit columns for every transactional table — see architecture
doc Section 5.3: every table carries created_by/created_at/updated_by/
updated_at given how sign-off and traceability-heavy the process is."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, func  # type: ignore[import-not-found]
from sqlalchemy.dialects.postgresql import UUID  # type: ignore[import-not-found]
from sqlalchemy.orm import Mapped, mapped_column  # type: ignore[import-not-found]


class AuditMixin:
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_by: Mapped[str | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_by: Mapped[str | None] = mapped_column(nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )
