"""empty message

Revision ID: 9688f8838685
Revises: 76e762613180
Create Date: 2023-01-14 22:38:17.881990

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9688f8838685'
down_revision = '76e762613180'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('sales_invoices', schema=None) as batch_op:
        batch_op.alter_column('invoice_date',
               existing_type=sa.DATETIME(),
               type_=sa.String(length=40),
               existing_nullable=True)
        batch_op.alter_column('date_posted',
               existing_type=sa.DATETIME(),
               type_=sa.String(length=40),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('sales_invoices', schema=None) as batch_op:
        batch_op.alter_column('date_posted',
               existing_type=sa.String(length=40),
               type_=sa.DATETIME(),
               existing_nullable=True)
        batch_op.alter_column('invoice_date',
               existing_type=sa.String(length=40),
               type_=sa.DATETIME(),
               existing_nullable=True)

    # ### end Alembic commands ###
