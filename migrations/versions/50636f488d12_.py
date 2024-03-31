"""empty message

Revision ID: 50636f488d12
Revises: a5ec19870a1d
Create Date: 2024-03-31 16:38:14.638951

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '50636f488d12'
down_revision: Union[str, None] = 'a5ec19870a1d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 컬럼 추가
    op.add_column('report', sa.Column('reported_user_id', sa.Integer(), nullable=True))
    # 외래 키 제약 조건 생성
    op.create_foreign_key('reported_user_id_fk', 'report', 'user', ['reported_user_id'], ['id'])


def downgrade() -> None:
    # 외래 키 제약 조건 삭제
    op.drop_constraint('reported_user_id_fk', 'report', type_='foreignkey')
    # 컬럼 삭제
    op.drop_column('report', 'reported_user_id')
