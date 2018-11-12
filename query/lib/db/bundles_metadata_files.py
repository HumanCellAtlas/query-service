from dateutil.parser import parse as parse_datetime
from uuid import UUID

from lib.config import requires_admin_mode
from lib.db.table import Table


class BundlesMetadataFiles(Table):

    def insert(self, bundle_uuid: UUID, bundle_version: str, file_uuid: UUID, file_version: str) -> int:
        self._cursor.execute(
            """
            INSERT INTO bundles_metadata_files (bundle_uuid, bundle_version, file_uuid, file_version)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (bundle_uuid, bundle_version, file_uuid, file_version) DO NOTHING
            """,
            (
                str(bundle_uuid),
                parse_datetime(bundle_version),
                str(file_uuid),
                parse_datetime(file_version)
            )
        )
        result = self._cursor.rowcount
        return result

    @requires_admin_mode
    def initialize(self):
        self._cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS bundles_metadata_files (
                bundle_uuid UUID,
                bundle_version timestamp NOT NULL,
                file_uuid UUID NOT NULL,
                file_version timestamp NOT NULL,
                FOREIGN KEY (bundle_uuid, bundle_version) REFERENCES bundles(uuid, version),
                FOREIGN KEY (file_uuid, file_version) REFERENCES metadata_files(uuid, version),
                UNIQUE (bundle_uuid, bundle_version, file_uuid, file_version)
            );

            CREATE INDEX IF NOT EXISTS bundles_metadata_files_bundle_uuid ON bundles_metadata_files USING btree (bundle_uuid);

            CREATE INDEX IF NOT EXISTS bundles_metadata_files_file_uuid ON bundles_metadata_files USING btree (file_uuid);
        """
        )

    @requires_admin_mode
    def destroy(self):
        self._cursor.execute("DROP TABLE bundles_metadata_files")
