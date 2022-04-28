"""inactive customers

Revision ID: 0b2533b9b534
Revises: 921e0a2bd6de
Create Date: 2022-04-19 22:33:01.145447

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0b2533b9b534'
down_revision = '921e0a2bd6de'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('customer', sa.Column('is_inactive', sa.Boolean, default=False))
    op.add_column('customer', sa.Column('default_currency', sa.String(255)))
    pass


def downgrade():
    op.drop_column('customer', 'is_inactive')
    op.drop_column('customer', 'default_currency')
    pass
