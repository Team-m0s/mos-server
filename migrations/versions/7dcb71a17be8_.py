"""empty message

Revision ID: 7dcb71a17be8
Revises: aaab2801cd4d
Create Date: 2024-05-11 17:55:06.911174

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7dcb71a17be8'
down_revision: Union[str, None] = 'aaab2801cd4d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("notification") as batch_op:
        batch_op.add_column(sa.Column('vocabulary_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_notification_vocabulary', 'vocabulary', ['vocabulary_id'], ['id'])


def downgrade() -> None:
    with op.batch_alter_table("notification") as batch_op:
        batch_op.drop_constraint('fk_notification_vocabulary', type_='foreignkey')
        batch_op.drop_column('vocabulary_id')
