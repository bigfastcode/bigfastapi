"""add country code to table

Revision ID: 0367b739bb81
Revises: 1e09924c1938
Create Date: 2022-01-27 16:10:57.297020

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0367b739bb81'
down_revision = '1e09924c1938'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', 
    sa.Column('image', sa.String(), index= True), 
    sa.Column('is_deleted', sa.Boolean(), index=True),
    sa.Column('device_id', sa.String(), index=True),
    sa.Column('country', sa.String(225), index=True),
    sa.Column('state', sa.String(225), index=True),
    sa.Column('google_id', sa.String()),
    sa.Column('google_picture', sa.String()),
    sa.Column('date_created', sa.DateTime()),
    sa.Column('last_updated', sa.DateTime())
    )
    pass


def downgrade():
    op.drop_column('users', 
    'image', 
    'is_deleted',
    'device_id', 
    'country', 
    'state', 
    'google_id', 
    'google_picture', 
    'date_created',
    'last_updated'
    )
    pass
