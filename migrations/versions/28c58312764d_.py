"""empty message

Revision ID: 28c58312764d
Revises: 59aed4abda9f
Create Date: 2024-02-10 01:32:48.814449

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '28c58312764d'
down_revision: Union[str, None] = '59aed4abda9f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('comment', sa.Column('modify_date', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('comment', 'modify_date')
    # ### end Alembic commands ###
