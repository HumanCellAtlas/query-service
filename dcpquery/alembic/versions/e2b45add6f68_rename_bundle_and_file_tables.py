"""rename_bundle_and_file_tables

Revision ID: e2b45add6f68
Revises: 7597ca0971e5
Create Date: 2019-07-03 14:30:49.987853

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e2b45add6f68'
down_revision = '7597ca0971e5'
branch_labels = None
depends_on = None


def upgrade():
    op.rename_table('bundles', 'bundles_all_versions')
    op.rename_table('files', 'files_all_versions')


def downgrade():
    op.rename_table('bundles_all_versions', 'bundles')
    op.rename_table('marathon', 'files_all_versions')
