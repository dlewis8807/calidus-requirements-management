"""add_coverage_snapshots_table

Revision ID: eb6aa8f9d3ec
Revises: 23a663f00df1
Create Date: 2025-10-21 18:04:27.422065

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'eb6aa8f9d3ec'
down_revision: Union[str, None] = '23a663f00df1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
