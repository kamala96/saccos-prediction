"""empty message

Revision ID: ff47d3cf9e83
Revises: 
Create Date: 2022-05-23 08:13:05.430924

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ff47d3cf9e83'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('saccos',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=1000), nullable=True),
    sa.Column('date_created', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('prediction_models',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=1000), nullable=True),
    sa.Column('date_created', sa.DateTime(), nullable=False),
    sa.Column('saccoss_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['saccoss_id'], ['saccos.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('prediction_models')
    op.drop_table('saccos')
    # ### end Alembic commands ###
