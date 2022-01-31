"""create tables

Revision ID: 1e09924c1938
Revises: 
Create Date: 2022-01-27 14:10:38.187671

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1e09924c1938'
down_revision = None
branch_labels = None
depends_on = None
from uuid import UUID, uuid4


def upgrade():
    op.add_column('users', sa.Column('country_code', sa.String(225), index= True))
    pass


def downgrade():
    op.drop_column('users', 'country_code')
    pass
