from typing import List

from query.lib.config import requires_admin_mode
from query.lib.db.table import Table


class ProcessLinks(Table):
    def insert(self, process_uuid: str, file_uuid: str, process_file_connection_type: str, file_type: str):
        result = 0
        try:
            self._cursor.execute(
                """
                INSERT INTO process_links (process_uuid, file_uuid, process_file_connection_type, file_type)
                VALUES (%s, %s, %s, %s)

                """,
                (
                    process_uuid,
                    file_uuid,
                    process_file_connection_type,
                    file_type,
                )
            )
            result = self._cursor.rowcount
        except Exception as e:
            print(f"EVERYTHING IS BROKEN!!!!: {e}")
        return result

    def select_by_process_uuid(self, process_uuid):
        self._cursor.execute(
            """
            SELECT * FROM process_links
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
            process_file_connection_type=response[0][2],
            file_type=response[0][3],
        )

    #TODO once table settled, make process_file_connection_type an enum/create enum (input_entity, output_entity, protocol_entity)
    @requires_admin_mode
    def initialize(self):
        self._cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS processes (
                process_uuid text,
                file_uuid text,
                process_file_connection_type text,
                file_type,
                PRIMARY KEY (process_uuid)
            );
            CREATE TABLE IF NOT EXISTS process_links_join_table (
              parent_process_uuid text,
              child_process_uuid text,
              UNIQUE (parent_process_uuid, child_process_uuid)
            );

        """
        )

    @requires_admin_mode
    def destroy(self):
        self._cursor.execute("DROP TABLE IF EXISTS process_links; DROP TABLE IF EXISTS process_links_join_table;")