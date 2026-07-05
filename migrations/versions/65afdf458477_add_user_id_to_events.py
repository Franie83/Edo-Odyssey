"""Add user_id to events

Revision ID: 65afdf458477
Revises: bf0da3de6505
Create Date: 2026-07-05 09:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '65afdf458477'
down_revision = 'bf0da3de6505'
branch_labels = None
depends_on = None


def upgrade():
    # Add user_id column to events with named foreign key
    with op.batch_alter_table('events', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_events_user_id', 'users', ['user_id'], ['id'])


def downgrade():
    # Remove foreign key and column
    with op.batch_alter_table('events', schema=None) as batch_op:
        batch_op.drop_constraint('fk_events_user_id', type_='foreignkey')
        batch_op.drop_column('user_id')