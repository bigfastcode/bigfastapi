"""Add a column

Revision ID: 55bf9f113273
Revises: b9db22a7a297
Create Date: 2022-02-28 18:48:21.215288

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '55bf9f113273'
down_revision = 'b9db22a7a297'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('businesses', sa.Column('email', sa.String(), default='', index=True))
    op.add_column('businesses', sa.Column('phone_number', sa.String(), default=''))
    pass

def downgrade():
    op.drop_column('businesses', 'email')
    op.drop_column('businesses', 'phone_number')
    pass
