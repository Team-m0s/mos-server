"""empty message

Revision ID: 2e1a23280fa9
Revises: 0fb989f09fbf
Create Date: 2024-02-12 21:49:50.901788

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2e1a23280fa9'
down_revision: Union[str, None] = '0fb989f09fbf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('accompany',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('city', sa.String(), nullable=False),
    sa.Column('total_member', sa.Integer(), nullable=False),
    sa.Column('leader_id', sa.Integer(), nullable=True),
    sa.Column('introduce', sa.String(), nullable=False),
    sa.Column('activity_scope', sa.Enum('online', 'offline', 'hybrid', name='activityscope'), nullable=False),
    sa.Column('create_date', sa.String(), nullable=False),
    sa.Column('update_date', sa.String(), nullable=False),
    sa.Column('category', sa.String(), nullable=False),
    sa.Column('chat_count', sa.String(), nullable=False),
    sa.Column('like_count', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['leader_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('accompany_member',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('accompany_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['accompany_id'], ['accompany.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'accompany_id')
    )
    op.create_table('image',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('image_url', sa.String(), nullable=False),
    sa.Column('accompany_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['accompany_id'], ['accompany.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('notice',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('content', sa.String(), nullable=False),
    sa.Column('accompany_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['accompany_id'], ['accompany.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tag',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('accompany_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['accompany_id'], ['accompany.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tag')
    op.drop_table('notice')
    op.drop_table('image')
    op.drop_table('accompany_member')
    op.drop_table('accompany')
    # ### end Alembic commands ###
