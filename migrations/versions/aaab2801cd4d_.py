"""empty message

Revision ID: aaab2801cd4d
Revises: 5090b3a878de
Create Date: 2024-05-10 14:56:41.901108

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'aaab2801cd4d'
down_revision: Union[str, None] = '5090b3a878de'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_activity',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('activity_type', sa.String(), nullable=False),
    sa.Column('activity_date', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_activity_id'), 'user_activity', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_user_activity_id'), table_name='user_activity')
    op.drop_table('user_activity')
    # ### end Alembic commands ###
