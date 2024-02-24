"""empty message

Revision ID: ff729b5ecbc1
Revises: 930e996dd483
Create Date: 2024-02-25 00:54:59.602091

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import Inspector

# revision identifiers, used by Alembic.
revision: str = 'ff729b5ecbc1'
down_revision: Union[str, None] = '930e996dd483'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # SQLite 데이터베이스를 위한 배치 모드 사용
    with op.batch_alter_table('like', schema=None) as batch_op:
        # Inspector 객체를 사용하여 'Like' 테이블에 'accompany_id' 컬럼이 이미 존재하는지 확인
        inspector = Inspector.from_engine(op.get_bind())
        columns = [col['name'] for col in inspector.get_columns('like')]
        if 'accompany_id' not in columns:
            batch_op.add_column(sa.Column('accompany_id', sa.Integer(), nullable=True))
            batch_op.create_foreign_key('fk_accompany_id', 'accompany', ['accompany_id'], ['id'])


def downgrade():
    with op.batch_alter_table('like', schema=None) as batch_op:
        # ForeignKeyConstraint 객체의 이름을 사용하여 외래 키 제약 조건을 제거
        batch_op.drop_constraint('fk_accompany_id', type_='foreignkey')
        batch_op.drop_column('accompany_id')