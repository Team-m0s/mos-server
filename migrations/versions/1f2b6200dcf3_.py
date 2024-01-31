"""empty message

Revision ID: 1f2b6200dcf3
Revises: 543c7c5194b4
Create Date: 2024-01-31 22:33:09.070416

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1f2b6200dcf3'
down_revision: Union[str, None] = '543c7c5194b4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('comment', sa.Column('like_count', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('comment', 'like_count')
    # ### end Alembic commands ###
