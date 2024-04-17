"""empty message

Revision ID: 9286ac3c57bb
Revises: d1647cc69f3e
Create Date: 2024-04-18 00:06:21.135960

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9286ac3c57bb'
down_revision: Union[str, None] = 'd1647cc69f3e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    with op.batch_alter_table("block") as batch_op:
        batch_op.add_column(sa.Column('blocked_firebase_uuid', sa.String(), nullable=True))
        batch_op.create_foreign_key('fk_blocked_firebase_uuid', 'user', ['blocked_firebase_uuid'], ['firebase_uuid'])

    with op.batch_alter_table("notification") as batch_op:
        batch_op.alter_column('body', existing_type=sa.VARCHAR(), type_=sa.Text(), existing_nullable=False)

    with op.batch_alter_table("report") as batch_op:
        batch_op.alter_column('report_reason_enum', existing_type=sa.VARCHAR(length=20), type_=sa.JSON(), existing_nullable=True)


def downgrade() -> None:
    with op.batch_alter_table("block") as batch_op:
        batch_op.drop_constraint('fk_blocked_firebase_uuid', type_='foreignkey')
        batch_op.drop_column('blocked_firebase_uuid')

    with op.batch_alter_table("notification") as batch_op:
        batch_op.alter_column('body', existing_type=sa.Text(), type_=sa.VARCHAR(), existing_nullable=False)

    with op.batch_alter_table("report") as batch_op:
        batch_op.alter_column('report_reason_enum', existing_type=sa.JSON(), type_=sa.VARCHAR(length=20), existing_nullable=True)
