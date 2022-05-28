"""empty message

Revision ID: a151d46aa59f
Revises: ff47d3cf9e83
Create Date: 2022-05-24 18:10:23.093400

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a151d46aa59f'
down_revision = 'ff47d3cf9e83'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('prediction_models', sa.Column('model_used', sa.String(length=1000), nullable=True))
    op.add_column('prediction_models', sa.Column('model_accuracy', sa.Float(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('prediction_models', 'model_accuracy')
    op.drop_column('prediction_models', 'model_used')
    # ### end Alembic commands ###
