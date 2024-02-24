"""empty message

Revision ID: c22d84583ae9
Revises: ff729b5ecbc1
Create Date: 2024-02-25 01:09:00.531948

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c22d84583ae9'
down_revision: Union[str, None] = 'ff729b5ecbc1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Step 1: Create a new table with the desired column types and structure
    op.execute(
        '''
        CREATE TABLE IF NOT EXISTS accompany_new (
            id INTEGER PRIMARY KEY,
            title VARCHAR NOT NULL,
            city VARCHAR NOT NULL,
            total_member INTEGER NOT NULL,
            leader_id INTEGER,
            introduce VARCHAR NOT NULL,
            activity_scope VARCHAR(7) NOT NULL, -- Assuming Enum is stored as TEXT
            create_date VARCHAR NOT NULL,
            update_date VARCHAR NOT NULL,
            category VARCHAR NOT NULL, -- Assuming Enum is stored as TEXT
            chat_count INTEGER NOT NULL DEFAULT 0,
            like_count INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY(leader_id) REFERENCES user(id)
        )
        '''
    )
    # Since we're dealing with relationships, ensure you handle any related data correctly.

    # Step 2: Copy data from the old table to the new table
    op.execute(
        '''
        INSERT INTO accompany_new (id, title, city, total_member, leader_id, introduce, activity_scope, create_date, update_date, category, chat_count, like_count)
        SELECT id, title, city, total_member, leader_id, introduce, activity_scope, create_date, update_date, category, chat_count, like_count
        FROM accompany
        '''
    )
    # Step 3: Drop the old table and rename the new table
    op.execute('DROP TABLE accompany')
    op.execute('ALTER TABLE accompany_new RENAME TO accompany')


def downgrade():
    # For downgrade, recreate the original table structure and copy data back.
    # This would involve reversing any type changes and ensuring all data fits the original schema.
    # This example assumes you were changing types and need to reverse it.
    op.execute(
        '''
        CREATE TABLE IF NOT EXISTS accompany_old (
            id INTEGER PRIMARY KEY,
            title VARCHAR NOT NULL,
            city VARCHAR NOT NULL,
            total_member INTEGER NOT NULL,
            leader_id INTEGER,
            introduce VARCHAR NOT NULL,
            activity_scope VARCHAR(7) NOT NULL, -- Enum stored as TEXT
            create_date VARCHAR NOT NULL,
            update_date VARCHAR NOT NULL,
            category VARCHAR NOT NULL, -- Enum stored as TEXT
            chat_count TEXT NOT NULL DEFAULT '0', -- Assuming you're changing back to TEXT
            like_count TEXT NOT NULL DEFAULT '0',
            FOREIGN KEY(leader_id) REFERENCES user(id)
        )
        '''
    )
    op.execute(
        '''
        INSERT INTO accompany_old (id, title, city, total_member, leader_id, introduce, activity_scope, create_date, update_date, category, chat_count, like_count)
        SELECT id, title, city, total_member, leader_id, introduce, activity_scope, create_date, update_date, category, CAST(chat_count AS TEXT), CAST(like_count AS TEXT)
        FROM accompany
        '''
    )
    op.execute('DROP TABLE accompany')
    op.execute('ALTER TABLE accompany_old RENAME TO accompany')


