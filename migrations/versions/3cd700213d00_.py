"""empty message

Revision ID: 3cd700213d00
Revises: 86a04a7f67e3
Create Date: 2024-02-16 03:41:11.119556

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import Inspector

# revision identifiers, used by Alembic.
revision: str = '3cd700213d00'
down_revision: Union[str, None] = '86a04a7f67e3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('comment', schema=None) as batch_op:
        # Inspector 객체를 사용하여 'Image' 테이블에 'post_id' 컬럼이 이미 존재하는지 확인
        inspector = Inspector.from_engine(op.get_bind())
        columns = [col['name'] for col in inspector.get_columns('comment')]
        if 'notice_id' not in columns:
            batch_op.add_column(sa.Column('notice_id', sa.Integer(), nullable=True))
            batch_op.create_foreign_key('fk_notice_id', 'notice', ['notice_id'], ['id'])


def downgrade() -> None:
    with op.batch_alter_table('comment', schema=None) as batch_op:
        batch_op.drop_constraint('fk_notice_id', type_='foreignkey')
        batch_op.drop_column('notice_id')
