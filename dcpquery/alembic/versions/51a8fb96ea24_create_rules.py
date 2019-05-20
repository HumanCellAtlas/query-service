"""create rules

Revision ID: 51a8fb96ea24
Revises: f86d2cea09a9
Create Date: 2019-05-08 22:04:01.648066

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.

revision = '51a8fb96ea24'
down_revision = 'f86d2cea09a9'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        CREATE OR REPLACE RULE process_table_ignore_duplicate_inserts AS
            ON INSERT TO processes
                WHERE EXISTS (
                  SELECT 1
                FROM processes
                WHERE process_uuid = NEW.process_uuid
            )
            DO INSTEAD NOTHING;
        """
    )
    op.execute(
        """
        CREATE OR REPLACE RULE bundle_file_join_table_ignore_duplicate_inserts AS
            ON INSERT TO bundle_file_links
                WHERE EXISTS (
                  SELECT 1
                FROM bundle_file_links
                WHERE bundle_fqid = NEW.bundle_fqid
                AND file_fqid = NEW.file_fqid
            )
            DO INSTEAD NOTHING;
        """
    )
    op.execute(
        """
        CREATE OR REPLACE RULE bundle_table_ignore_duplicate_inserts AS
            ON INSERT TO bundles
                WHERE EXISTS (
                  SELECT 1
                FROM bundles
                WHERE fqid = NEW.fqid
            )
            DO INSTEAD NOTHING;
        """
    )
    op.execute(
        """
        CREATE OR REPLACE RULE file_table_ignore_duplicate_inserts AS
            ON INSERT TO files
                WHERE EXISTS (
                  SELECT 1
                FROM files
                WHERE fqid = NEW.fqid
            )
            DO INSTEAD NOTHING;
        """
    )
    op.execute(
        """
        CREATE OR REPLACE RULE process_file_join_table_ignore_duplicate_inserts AS
            ON INSERT TO process_file_join_table
                WHERE EXISTS (
                  SELECT 1
                FROM process_file_join_table
                WHERE process_uuid = NEW.process_uuid
                AND process_file_connection_type=NEW.process_file_connection_type
                AND file_uuid=NEW.file_uuid
            )
            DO INSTEAD NOTHING;
        """
    )


def downgrade():
    op.execute("DROP RULE IF EXISTS process_table_ignore_duplicate_inserts ON processes;")
    op.execute("DROP RULE IF EXISTS file_table_ignore_duplicate_inserts ON files;")
    op.execute("DROP RULE IF EXISTS bundle_table_ignore_duplicate_inserts ON bundles;")
    op.execute("DROP RULE IF EXISTS bundle_file_join_table_ignore_duplicate_inserts ON bundle_file_links;")
    op.execute("DROP RULE IF EXISTS process_file_join_table_ignore_duplicate_inserts ON process_file_join_table;")
