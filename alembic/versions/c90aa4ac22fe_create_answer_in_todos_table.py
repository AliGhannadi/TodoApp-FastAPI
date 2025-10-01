"""Create answer in todos table

Revision ID: c90aa4ac22fe
Revises: 
Create Date: 2025-09-28 11:27:37.844164

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c90aa4ac22fe'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('todos', sa.Column('scheduled_time', sa.String(), nullable=True))

def downgrade() -> None:
    op.drop_column('todos', 'scheduled_time')
