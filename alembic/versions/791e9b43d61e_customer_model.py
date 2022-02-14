"""customer_model

Revision ID: 791e9b43d61e
Revises: f4e906862bfa
Create Date: 2022-02-13 22:58:26.252209

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '791e9b43d61e'
down_revision = 'f4e906862bfa'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('customer', sa.Column('is_deleted', sa.Boolean(), index=True))
    op.add_column('customer', sa.Column('other_information', sa.JSON(), index=True))
    pass


def downgrade():
    pass
