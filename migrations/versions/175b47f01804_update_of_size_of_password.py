"""update of size of password

Revision ID: 175b47f01804
Revises: 033118dccd25
Create Date: 2020-11-09 12:52:48.895999

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '175b47f01804'
down_revision = '033118dccd25'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('administrator', 'password',
               existing_type=sa.VARCHAR(length=30),
               type_=sa.String(length=300),
               existing_nullable=False)
    op.alter_column('patient', 'password',
               existing_type=sa.VARCHAR(length=30),
               type_=sa.String(length=300),
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('patient', 'password',
               existing_type=sa.String(length=300),
               type_=sa.VARCHAR(length=30),
               existing_nullable=False)
    op.alter_column('administrator', 'password',
               existing_type=sa.String(length=300),
               type_=sa.VARCHAR(length=30),
               existing_nullable=False)
    # ### end Alembic commands ###