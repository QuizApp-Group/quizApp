"""empty message

Revision ID: 3c8b41553137
Revises: 3f0c6631c001
Create Date: 2016-09-09 12:57:39.867388

"""

# revision identifiers, used by Alembic.
revision = '3c8b41553137'
down_revision = '3f0c6631c001'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('activity', sa.Column('include_in_scorecards', sa.Boolean(), nullable=True))
    op.alter_column('choice', 'choice',
               existing_type=mysql.VARCHAR(length=200),
               nullable=True)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('choice', 'choice',
               existing_type=mysql.VARCHAR(length=200),
               nullable=False)
    op.drop_column('activity', 'include_in_scorecards')
    ### end Alembic commands ###
