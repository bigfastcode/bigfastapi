"""business email and phone number

Revision ID: 4f74855656cc
Revises: 
Create Date: 2022-03-08 09:56:38.457153

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4f74855656cc'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # op.add_column('businesses', sa.Column('email', sa.String(255)))
    # op.add_column('businesses', sa.Column('phone_number', sa.String(255)))
    pass


def downgrade():
    pass
