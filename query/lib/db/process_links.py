from lib.config import requires_admin_mode
from lib.db.table import Table


class ProcessLinks(Table):
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