"""add password reset token fields to app_user

Revision ID: a7b8c9d0e1f2
Revises: f1a2b3c4d5e6
Create Date: 2026-09-24 21:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a7b8c9d0e1f2'
down_revision: Union[str, Sequence[str], None] = 'f1a2b3c4d5e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('app_user', sa.Column('reset_token', sa.String(length=255), nullable=True))
    op.add_column('app_user', sa.Column('reset_token_expires_at', sa.DateTime(timezone=True), nullable=True))
    op.create_index(op.f('ix_app_user_reset_token'), 'app_user', ['reset_token'], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_app_user_reset_token'), table_name='app_user')
    op.drop_column('app_user', 'reset_token_expires_at')
    op.drop_column('app_user', 'reset_token')
