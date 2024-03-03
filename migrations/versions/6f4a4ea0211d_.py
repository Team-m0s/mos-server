"""empty message

Revision ID: 6f4a4ea0211d
Revises: be2f9da12ed8
Create Date: 2024-03-04 00:24:29.137757

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '6f4a4ea0211d'
down_revision: Union[str, None] = 'be2f9da12ed8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("application") as batch_op:
        batch_op.alter_column('answer', existing_type=sa.VARCHAR(), nullable=True)


def downgrade() -> None:
    with op.batch_alter_table("application") as batch_op:
        batch_op.alter_column('answer', existing_type=sa.VARCHAR(), nullable=False)
