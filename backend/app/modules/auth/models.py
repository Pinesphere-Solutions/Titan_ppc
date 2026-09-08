"""User and Role tables — see ERD in architecture doc Section 5.3."""

import uuid

from sqlalchemy import ForeignKey, String
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

    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("role.id"), nullable=False)

    role: Mapped["Role"] = relationship()
