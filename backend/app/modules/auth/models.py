"""User and Role tables — see ERD in architecture doc Section 5.3."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.models_mixin import AuditMixin


class Role(Base, AuditMixin):
    __tablename__ = "role"

    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    # e.g. gate_security, sub_con, qc_team, qa_team, ppc_team, admin


class User(Base, AuditMixin):
    __tablename__ = "app_user"

    # Login identifier — per decision with Athithya (M1 Forgot Password),
    # this is treated as the user's email going forward: new users
    # created via Settings (M16) must supply a valid email address here,
    # and that's also where the password-reset link is sent. Existing
    # rows created before this decision may still be non-email usernames.
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("role.id"), nullable=False)

    # M1 Forgot Password — single-use, time-limited reset token. Nullable:
    # only set between a forgot-password request and its use/expiry.
    reset_token: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True, index=True)
    reset_token_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    role: Mapped["Role"] = relationship()
