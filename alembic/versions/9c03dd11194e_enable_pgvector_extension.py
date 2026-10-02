"""enable pgvector extension

Revision ID: 9c03dd11194e
Revises: be59ba4506d0
Create Date: 2026-10-01 19:09:18.109913

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '9c03dd11194e'
down_revision: Union[str, Sequence[str], None] = 'be59ba4506d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        "CREATE EXTENSION IF NOT EXISTS vector"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        "DROP EXTENSION IF EXISTS vector"
    )
