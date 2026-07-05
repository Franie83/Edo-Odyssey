"""Add user_id to attractions, hotels, restaurants

Revision ID: bf0da3de6505
Revises: 99188a7347bc
Create Date: 2026-07-05 09:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bf0da3de6505'
down_revision = '99188a7347bc'
branch_labels = None
depends_on = None


def upgrade():
    # Add user_id column to attractions
    with op.batch_alter_table('attractions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_attractions_user_id', 'users', ['user_id'], ['id'])

    # Add user_id column to hotels
    with op.batch_alter_table('hotels', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_hotels_user_id', 'users', ['user_id'], ['id'])

    # Add user_id column to restaurants
    with op.batch_alter_table('restaurants', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_restaurants_user_id', 'users', ['user_id'], ['id'])


def downgrade():
    # Remove foreign keys and columns
    with op.batch_alter_table('restaurants', schema=None) as batch_op:
        batch_op.drop_constraint('fk_restaurants_user_id', type_='foreignkey')
        batch_op.drop_column('user_id')

    with op.batch_alter_table('hotels', schema=None) as batch_op:
        batch_op.drop_constraint('fk_hotels_user_id', type_='foreignkey')
        batch_op.drop_column('user_id')

    with op.batch_alter_table('attractions', schema=None) as batch_op:
        batch_op.drop_constraint('fk_attractions_user_id', type_='foreignkey')
        batch_op.drop_column('user_id')