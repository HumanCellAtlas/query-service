"""create db functions

Revision ID: 7597ca0971e5
Revises: 51a8fb96ea24
Create Date: 2019-05-08 22:25:25.224195

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7597ca0971e5'
down_revision = '51a8fb96ea24'
branch_labels = None
depends_on = None


def upgrade():
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
                ON process_join_table.child_process_uuid = recursive_table.parent_process_uuid)
            SELECT * from recursive_table;
            $$ LANGUAGE SQL;
        """
    )


def downgrade():
    op.execute("DROP FUNCTION get_all_children;")
    op.execute("DROP FUNCTION get_all_parents;")
