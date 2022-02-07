"""customer_another

Revision ID: 647f600ed6a8
Revises: 442d9b84ce92
Create Date: 2022-02-01 08:36:00.650606

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '647f600ed6a8'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('customer', sa.Column('country_code', sa.String(225), index= True))
    pass


def downgrade():
    op.drop_column('customer', 'country_code')
    pass
