"""empty message

Revision ID: 53abbe298c1b
Revises: 78280ccd6797
Create Date: 2024-05-01 16:17:50.390353

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '53abbe298c1b'
down_revision: Union[str, None] = '78280ccd6797'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('post', sa.Column('is_hot', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('post', 'is_hot')
    # ### end Alembic commands ###
