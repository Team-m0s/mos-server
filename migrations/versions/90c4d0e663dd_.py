"""empty message

Revision ID: 90c4d0e663dd
Revises: 2ff28d8f5eae
Create Date: 2024-04-07 19:12:31.543897

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '90c4d0e663dd'
down_revision: Union[str, None] = '2ff28d8f5eae'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('accompany', sa.Column('blind_date', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('accompany', 'blind_date')
    # ### end Alembic commands ###
