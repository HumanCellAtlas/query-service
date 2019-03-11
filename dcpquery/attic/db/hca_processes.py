from uuid import UUID

from query.lib.config import requires_admin_mode
from query.lib.db.table import Table


class HCAProcesses(Table):
    def insert(self, process_uuid: UUID, file_uuid: UUID, process_file_connection_type: str):
        self._cursor.execute(
            """
            INSERT INTO hca_processes (process_uuid, file_uuid, process_file_connection_type)
            VALUES (%s, %s, %s)
            ON CONFLICT (process_uuid, file_uuid, process_file_connection_type) DO NOTHING;
            """,
            (
                process_uuid,
                file_uuid,
                process_file_connection_type
            )
        )
        return self._cursor.rowcount

    def insert_parent_child_link(self, parent_process_uuid: UUID, child_process_uuid: UUID):
        self._cursor.execute(
            """
            INSERT into process_links_join_table (parent_process_uuid, child_process_uuid)
            VALUES (%s, %s)
            ON CONFLICT (parent_process_uuid, child_process_uuid) DO NOTHING;
            """,
            (
                parent_process_uuid,
                child_process_uuid
            )
        )
        return self._cursor.rowcount

    def select_by_process_uuid(self, process_uuid: UUID):
        self._cursor.execute(
            """
            SELECT * FROM hca_processes
            WHERE process_uuid=%s
            """,
            (
                process_uuid,
            )
        )
        response = self._cursor.fetchall()
        if len(response) == 0:
            return None

        return dict(
            uuid=response[0][0],
            file_uuid=response[0][1],
            process_file_connection_type=response[0][2]
        )

    def list_process_uuids_for_file_uuid(self, file_uuid: UUID, connection_type=None):
        if not connection_type:
            self._cursor.execute(
                """
                SELECT process_uuid FROM hca_processes
                WHERE file_uuid=%s
                """,
                (
                    file_uuid,
                )
            )
        else:
            self._cursor.execute(
                """
                SELECT process_uuid FROM hca_processes
                WHERE file_uuid=%s
                AND process_file_connection_type=%s
                """,
                (
                    file_uuid,
                    connection_type
                )
            )
        return [ele[0] for ele in self._cursor.fetchall()]

    def list_direct_children_process_uuids(self, parent_process_uuid: UUID):
        self._cursor.execute(
            """
            SELECT child_process_uuid FROM process_links_join_table
            WHERE parent_process_uuid = %s
            """,
            (
                parent_process_uuid,
            )
        )
        return [ele[0] for ele in self._cursor.fetchall()]

    def list_direct_parent_process_uuids(self, child_process_uuid: UUID):
        self._cursor.execute(
            """
            SELECT parent_process_uuid FROM process_links_join_table
            WHERE child_process_uuid = %s
            """,
            (
                child_process_uuid,
            )
        )
        return [ele[0] for ele in self._cursor.fetchall()]

    def list_all_parents(self, process_uuid: UUID):
        self._cursor.execute(
            """
            SELECT get_all_parents(%s);
            """,
            (
                process_uuid,
            )
        )
        return [ele[0] for ele in self._cursor.fetchall()]

    def list_all_children(self, process_uuid: UUID):
        self._cursor.execute(
            """
            SELECT get_all_children(%s);
            """,
            (
                process_uuid,
            )
        )

        return [ele[0] for ele in self._cursor.fetchall()]

    @requires_admin_mode
    def initialize(self):
        self._cursor.execute(
            """
            CREATE TYPE process_file_connection_type_enum AS ENUM ('INPUT_ENTITY', 'OUTPUT_ENTITY', 'PROTOCOL_ENTITY');
            CREATE TABLE IF NOT EXISTS hca_processes (
                process_uuid UUID,
                file_uuid UUID,
                process_file_connection_type process_file_connection_type_enum,
                UNIQUE (process_uuid, file_uuid, process_file_connection_type)
            );
            CREATE TABLE IF NOT EXISTS process_links_join_table (
              parent_process_uuid UUID,
              child_process_uuid UUID,
              UNIQUE (parent_process_uuid, child_process_uuid)
            );
            CREATE or REPLACE FUNCTION get_all_children(IN parent_process_uuid UUID)
            RETURNS TABLE(child_process_uuid UUID) as $$
              WITH RECURSIVE recursive_table AS (
                SELECT child_process_uuid FROM process_links_join_table
                WHERE parent_process_uuid=$1
                UNION
                SELECT process_links_join_table.child_process_uuid FROM process_links_join_table
                INNER JOIN recursive_table
                ON process_links_join_table.parent_process_uuid = recursive_table.child_process_uuid)
            SELECT * from recursive_table;
            $$ LANGUAGE SQL;
            CREATE or REPLACE FUNCTION get_all_parents(IN child_process_uuid UUID)
            RETURNS TABLE(parent_process_uuid UUID) as $$
              WITH RECURSIVE recursive_table AS (
                SELECT parent_process_uuid FROM process_links_join_table
                WHERE child_process_uuid=$1
                UNION
                SELECT process_links_join_table.parent_process_uuid FROM process_links_join_table
                INNER JOIN recursive_table
                ON process_links_join_table.child_process_uuid = recursive_table.parent_process_uuid)
            SELECT * from recursive_table;
            $$ LANGUAGE SQL;

        """
        )

    @requires_admin_mode
    def destroy(self):
        self._cursor.execute("DROP TABLE IF EXISTS hca_processes; DROP TABLE IF EXISTS process_links_join_table; ")
