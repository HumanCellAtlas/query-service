"""add metadata schema version

Revision ID: 132698d15453
Revises: d11b97864836
Create Date: 2019-10-15 00:26:44.089228

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '132698d15453'
down_revision = 'd11b97864836'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('files_all_versions', sa.Column('schema_major_version', sa.Integer(), nullable=True))
    op.add_column('files_all_versions', sa.Column('schema_minor_version', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('files_all_versions', 'schema_minor_version')
    op.drop_column('files_all_versions', 'schema_major_version')
    # ### end Alembic commands ###
