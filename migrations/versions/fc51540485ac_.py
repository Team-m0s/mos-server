"""empty message

Revision ID: fc51540485ac
Revises: e601de43a283
Create Date: 2024-05-07 02:01:10.537822

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fc51540485ac'
down_revision: Union[str, None] = 'e601de43a283'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("report") as batch_op:
        batch_op.add_column(sa.Column('vocabulary_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_report_vocabulary', 'vocabulary', ['vocabulary_id'], ['id'])


def downgrade() -> None:
    with op.batch_alter_table("report") as batch_op:
        batch_op.drop_constraint('fk_report_vocabulary', type_='foreignkey')
        batch_op.drop_column('vocabulary_id')
