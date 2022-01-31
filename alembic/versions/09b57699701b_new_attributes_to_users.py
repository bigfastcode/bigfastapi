"""new attributes to users

Revision ID: 09b57699701b
Revises: 0367b739bb81
Create Date: 2022-01-28 06:51:15.581769

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '09b57699701b'
down_revision = '0367b739bb81'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('country', sa.String(225), index=True))
    op.add_column('users', sa.Column('state', sa.String(225), index=True))
    op.add_column('users', sa.Column('is_deleted', sa.Boolean(), index=True))
    op.add_column('users', sa.Column('image', sa.String(), index= True)) 
    op.add_column('users', sa.Column('device_id', sa.String(), index=True))
    op.add_column('users', sa.Column('google_id', sa.String()))
    op.add_column('users', sa.Column('date_created', sa.DateTime()))
    op.add_column('users', sa.Column('last_updated', sa.DateTime()))
    
    pass


# def downgrade():
#     op.drop_column('users', 'image') 
#     op.drop_column('users', 'is_deleted') 
#     op.drop_column('users', 'device_id') 
#     op.drop_column('users','device_id') 
#     op.drop_column('users', 'country') 
#     op.drop_column('users', 'state') 
#     op.drop_column('users', 'google_id')
#     op.drop_column('users', 'date_created')
#     op.drop_column('users', 'last_updated')
#     pass

