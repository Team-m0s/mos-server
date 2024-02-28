"""empty message

Revision ID: f4225d965f20
Revises: 8db6fcc39b2f
Create Date: 2024-02-29 02:54:01.143233

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f4225d965f20'
down_revision: Union[str, None] = '8db6fcc39b2f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('user') as batch_op:
        batch_op.add_column(sa.Column('provider', sa.String(), nullable=False))
        batch_op.alter_column('uuid', existing_type=sa.VARCHAR(), nullable=False)


def downgrade() -> None:
    with op.batch_alter_table('user') as batch_op:
        batch_op.alter_column('uuid', existing_type=sa.VARCHAR(), nullable=True)
        batch_op.drop_column('provider')



