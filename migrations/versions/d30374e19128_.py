"""empty message

Revision ID: d30374e19128
Revises: 50636f488d12
Create Date: 2024-03-31 16:47:08.401621

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'd30374e19128'
down_revision: Union[str, None] = '50636f488d12'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('report') as batch_op:
        batch_op.add_column(sa.Column('reported_user_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('reported_user_id_fk', 'user', ['reported_user_id'], ['id'])


def downgrade() -> None:
    with op.batch_alter_table('report') as batch_op:
        batch_op.drop_constraint('reported_user_id_fk', type_='foreignkey')
        batch_op.drop_column('reported_user_id')
