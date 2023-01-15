"""empty message

Revision ID: 071917b032d1
Revises: 9688f8838685
Create Date: 2023-01-15 12:34:22.062567

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '071917b032d1'
down_revision = '9688f8838685'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('purchase_invoices', schema=None) as batch_op:
        batch_op.add_column(sa.Column('supplier_code', sa.String(length=40), nullable=True))
        batch_op.drop_column('customer_code')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('purchase_invoices', schema=None) as batch_op:
        batch_op.add_column(sa.Column('customer_code', sa.VARCHAR(length=40), nullable=True))
        batch_op.drop_column('supplier_code')

    # ### end Alembic commands ###
