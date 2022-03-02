"""create table test

Revision ID: acd4cbff5545
Revises: 
Create Date: 2022-03-02 14:04:16.770971

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'acd4cbff5545'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('wallet_transactions', sa.Column('transaction_ref', sa.String()))
    pass


def downgrade():
    op.drop_column('wallet_transactions', 'transaction_ref')
    pass
