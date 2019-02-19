from typing import List

from lib.config import requires_admin_mode
from lib.db.table import Table


class ProcessLinks(Table):
    def insert(self, process_uuid: str, input_uuids: List[str], output_uuids: List[str], protocol_uuids: List[str]):
        result = 0
        try:
            self._cursor.execute(
                """
                INSERT INTO process_links (process_uuid, input_file_uuids, output_file_uuids, protocol_file_uuids)
                VALUES (%s, %s, %s, %s)

                """,
                (
                    process_uuid,
                    input_uuids,
                    output_uuids,
                    protocol_uuids,
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
            input_file_uuids=response[0][1],
            output_file_uuids=response[0][2],
            protocol_file_uuids=response[0][3],
        )

    @requires_admin_mode
    def initialize(self):
        self._cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS process_links (
                process_uuid text,
                input_file_uuids text[],
                output_file_uuids text[],
                protocol_file_uuids text[],
                PRIMARY KEY (process_uuid)
            );
            CREATE TABLE IF NOT EXISTS process_links_join_table (
              parent_process_uuid text,
              child_process_uuid text,
              UNIQUE (parent_process_uuid, child_process_uuid)
            );
            CREATE INDEX IF NOT EXISTS input_uuids_array ON process_links USING GIN (input_file_uuids);
            CREATE INDEX IF NOT EXISTS output_uuids_array ON process_links USING GIN (output_file_uuids);
            CREATE INDEX IF NOT EXISTS protocol_uuids_array ON process_links USING GIN (protocol_file_uuids);

        """
        )

    @requires_admin_mode
    def destroy(self):
        self._cursor.execute("DROP TABLE IF EXISTS process_links; DROP TABLE IF EXISTS process_links_join_table;")