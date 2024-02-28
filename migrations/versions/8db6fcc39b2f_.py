"""empty message

Revision ID: 8db6fcc39b2f
Revises: c22d84583ae9
Create Date: 2024-02-28 18:11:42.435536

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '8db6fcc39b2f'
down_revision: Union[str, None] = 'c22d84583ae9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('accompany') as batch_op:
        batch_op.alter_column('id',
                              existing_type=sa.INTEGER(),
                              nullable=False,
                              autoincrement=True)
    with op.batch_alter_table('user') as batch_op:
        batch_op.add_column(sa.Column('uuid', sa.String(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('user') as batch_op:
        batch_op.drop_column('uuid')
    with op.batch_alter_table('accompany') as batch_op:
        batch_op.alter_column('id',
                              existing_type=sa.INTEGER(),
                              nullable=True,
                              autoincrement=True)
