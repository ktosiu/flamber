"""empty message

Revision ID: 66d146220f69
Revises: None
Create Date: 2016-03-21 20:33:54.301159

"""

# revision identifiers, used by Alembic.
revision = '66d146220f69'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('password_hash', sa.String(length=128), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'password_hash')
    ### end Alembic commands ###
