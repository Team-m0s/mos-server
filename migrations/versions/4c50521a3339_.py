"""empty message

Revision ID: 4c50521a3339
Revises: fc42d1cce05e
Create Date: 2024-03-08 17:50:03.595939

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '4c50521a3339'
down_revision: Union[str, None] = 'fc42d1cce05e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("image") as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_image_user', 'user', ['user_id'], ['id'])


def downgrade() -> None:
    with op.batch_alter_table("image") as batch_op:
        batch_op.drop_constraint('fk_image_user', type_='foreignkey')
        batch_op.drop_column('user_id')
