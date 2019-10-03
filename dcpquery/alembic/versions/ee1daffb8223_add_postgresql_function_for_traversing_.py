"""Add postgresql function for traversing node graph

Revision ID: ee1daffb8223
Revises: e5a3141a178d
Create Date: 2019-10-01 17:15:25.992900

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ee1daffb8223'
down_revision = 'e5a3141a178d'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("DROP FUNCTION get_all_children;")
    op.execute("DROP FUNCTION get_all_parents;")
    op.execute(
        """
         CREATE or REPLACE FUNCTION process_subtree(IN parent_process_uuid UUID)
            RETURNS TABLE(child_process UUID) as $$
              WITH RECURSIVE recursive_table AS (
                SELECT child_process_uuid FROM process_join_table
                WHERE parent_process_uuid=$1
                UNION
                SELECT process_join_table.child_process_uuid FROM process_join_table
                INNER JOIN recursive_table
                ON process_join_table.parent_process_uuid = recursive_table.child_process_uuid)
            SELECT * from recursive_table;
            $$ LANGUAGE SQL;
        """
    )
    op.execute(
        """
        CREATE or REPLACE FUNCTION process_ancestors(IN child_process_uuid UUID)
            RETURNS TABLE(parent_process UUID) as $$
              WITH RECURSIVE recursive_table AS (
                SELECT parent_process_uuid FROM process_join_table
                WHERE child_process_uuid=$1
                UNION
                SELECT process_join_table.parent_process_uuid FROM process_join_table
                INNER JOIN recursive_table
                ON process_join_table.child_process_uuid = recursive_table.parent_process_uuid)
            SELECT * from recursive_table;
            $$ LANGUAGE SQL;
        """
    )
    op.execute(
        """
        CREATE or REPLACE FUNCTION file_subtree(IN uuid UUID)
        RETURNS TABLE(uuid UUID) AS $$
        SELECT file_uuid
          FROM process_file_join_table
          WHERE process_uuid IN (SELECT process_subtree(process_uuid)
                                 FROM process_file_join_table
                                 WHERE file_uuid = $1)
            AND file_uuid != $1;
        $$ LANGUAGE SQL;
        """
    )
    op.execute(
        """
        CREATE or REPLACE FUNCTION file_ancestors(IN uuid UUID)
        RETURNS TABLE(uuid UUID) AS $$
        SELECT file_uuid
          FROM process_file_join_table
          WHERE process_uuid IN (SELECT process_ancestors(process_uuid)
                                 FROM process_file_join_table
                                 WHERE file_uuid = $1)
            AND file_uuid != $1;
        $$ LANGUAGE SQL;
        """
    )


def downgrade():
    op.execute("DROP FUNCTION process_subtree;")
    op.execute("DROP FUNCTION process_ancestors;")
    op.execute("DROP FUNCTION file_subtree;")
    op.execute("DROP FUNCTION file_ancestors;")
    op.execute(
        """
         CREATE or REPLACE FUNCTION get_all_children(IN parent_process_uuid UUID)
            RETURNS TABLE(child_process UUID) as $$
              WITH RECURSIVE recursive_table AS (
                SELECT child_process_uuid FROM process_join_table
                WHERE parent_process_uuid=$1
                UNION
                SELECT process_join_table.child_process_uuid FROM process_join_table
                INNER JOIN recursive_table
                ON process_join_table.parent_process_uuid = recursive_table.child_process_uuid)
            SELECT * from recursive_table;
            $$ LANGUAGE SQL;
        """
    )
    op.execute(
        """
        CREATE or REPLACE FUNCTION get_all_parents(IN child_process_uuid UUID)
            RETURNS TABLE(parent_process UUID) as $$
              WITH RECURSIVE recursive_table AS (
                SELECT parent_process_uuid FROM process_join_table
                WHERE child_process_uuid=$1
                UNION
                SELECT process_join_table.parent_process_uuid FROM process_join_table
                INNER JOIN recursive_table
            $$ LANGUAGE SQL;
        """
    )
