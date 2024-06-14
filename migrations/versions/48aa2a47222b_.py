"""empty message

Revision ID: 48aa2a47222b
Revises: 194a9c0f7069
Create Date: 2024-06-14 15:59:14.878694

"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy.dialects.postgresql import ENUM
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '48aa2a47222b'
down_revision: Union[str, None] = '194a9c0f7069'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Define the Enum type
language_enum = ENUM('korean', 'english', name='languagecategory', create_type=False)

def upgrade():
    # Create the Enum type
    language_enum.create(op.get_bind())

    # Add the column with the Enum type
    op.add_column('banner', sa.Column('language', language_enum, nullable=False))


def downgrade():
    # Drop the column with the Enum type
    op.drop_column('banner', 'language')

    # Drop the Enum type
    language_enum.drop(op.get_bind())
