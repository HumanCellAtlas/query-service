"""replace view tables with materialized views

Revision ID: e5a3141a178d
Revises: 88bab7754636
Create Date: 2019-08-29 15:32:12.076186

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e5a3141a178d'
down_revision = '88bab7754636'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("DROP VIEW IF EXISTS files CASCADE;")
    op.execute("DROP VIEW IF EXISTS bundles CASCADE ;")
    op.execute(
        """
          CREATE MATERIALIZED VIEW files AS
          SELECT * FROM files_all_versions
          WHERE (uuid, version) IN (SELECT uuid, max(version) FROM files_all_versions GROUP BY uuid)
        """
    )
    op.execute("CREATE UNIQUE INDEX IF NOT EXISTS files_idx ON files (fqid);")
    op.execute(
        """
          CREATE MATERIALIZED VIEW bundles AS
          SELECT * FROM bundles_all_versions
          WHERE (uuid, version) IN (SELECT uuid, max(version) FROM bundles_all_versions GROUP BY uuid)
        """
    )
    op.execute("CREATE UNIQUE INDEX IF NOT EXISTS bundles_idx ON bundles (fqid);")


def downgrade():
    op.execute(
        """
        DROP MATERIALIZED VIEW bundles CASCADE;
        """
    )
    op.execute(
        """
        DROP MATERIALIZED VIEW files CASCADE;
        """
    )
    op.execute(
        """
          CREATE OR REPLACE VIEW files AS
          SELECT * FROM files_all_versions
          WHERE (uuid, version) IN (SELECT uuid, max(version) FROM files_all_versions GROUP BY uuid)
        """
    )
    op.execute(
        """
          CREATE OR REPLACE VIEW bundles AS
          SELECT * FROM bundles_all_versions
          WHERE (uuid, version) IN (SELECT uuid, max(version) FROM bundles_all_versions GROUP BY uuid)
        """
    )
