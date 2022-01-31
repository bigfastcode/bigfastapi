"""add g image

Revision ID: 709ea24ea2ce
Revises: f29d62a715ad
Create Date: 2022-01-28 13:16:51.599322

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '709ea24ea2ce'
down_revision = 'f29d62a715ad'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('google_image', sa.String(225), index= True))
    pass


def downgrade():
    op.drop_column('users', 'google_image')
    pass
