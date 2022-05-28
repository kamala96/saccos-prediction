"""empty message

Revision ID: 8e81a638b1a4
Revises: a151d46aa59f
Create Date: 2022-05-24 18:13:26.521214

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8e81a638b1a4'
down_revision = 'a151d46aa59f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('prediction_models', sa.Column('performance_criteria', sa.String(length=1000), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('prediction_models', 'performance_criteria')
    # ### end Alembic commands ###