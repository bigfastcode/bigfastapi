"""add a single column

Revision ID: f29d62a715ad
Revises: 09b57699701b
Create Date: 2022-01-28 07:31:11.176779

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f29d62a715ad'
down_revision = '09b57699701b'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('google_image', sa.String()))
    pass


def downgrade():
    op.drop_column('users', 'google_image')
    pass

