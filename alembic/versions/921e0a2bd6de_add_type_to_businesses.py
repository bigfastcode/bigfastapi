"""add_type_to_businesses

Revision ID: 921e0a2bd6de
Revises: 4f74855656cc
Create Date: 2022-03-25 15:36:08.363455

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '921e0a2bd6de'
down_revision = '4f74855656cc'
branch_labels = None
depends_on = None


def upgrade():
    # op.add_column('businesses', sa.Column('business_type', sa.String(255)))
    pass


def downgrade():
    pass
