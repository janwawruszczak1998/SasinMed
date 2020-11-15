"""time added

Revision ID: 033118dccd25
Revises: 28d8ca125ed6
Create Date: 2020-11-08 23:23:10.569649

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '033118dccd25'
down_revision = '28d8ca125ed6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('visit', sa.Column('time_of_visit', sa.Time(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('visit', 'time_of_visit')
    # ### end Alembic commands ###