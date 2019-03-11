from dateutil.parser import parse as parse_datetime
from uuid import UUID

from query.lib.config import requires_admin_mode
from query.lib.db.table import Table
from query.lib.model import datetime_to_version, typing


class BundlesFiles(Table):

    def insert(self, bundle_uuid: UUID, bundle_version: str, file_uuid: UUID, file_version: str) -> int:
        self._cursor.execute(
            """
            INSERT INTO bundles_files (bundle_uuid, bundle_version, file_uuid, file_version)
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

    def select_bundle(self, uuid: UUID, version: str) -> typing.List[dict]:
        self._cursor.execute(
            """
            select
                bundle_uuid,
                bundle_version,
                file_uuid,
                file_version
            from bundles_files
            where bundle_uuid = %s and bundle_version = %s
            """,
            (str(uuid), parse_datetime(version))
        )
        return [
            dict(
                bundle_uuid=e[0],
                bundle_version=datetime_to_version(e[1]),
                file_uuid=e[2],
                file_version=datetime_to_version(e[3])
            ) for e in self._cursor.fetchall()
        ]

    @requires_admin_mode
    def initialize(self):
        self._cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS bundles_files (
                bundle_uuid UUID,
                bundle_version timestamp with time zone NOT NULL,
                file_uuid UUID NOT NULL,
                file_version timestamp with time zone NOT NULL,
                FOREIGN KEY (bundle_uuid, bundle_version) REFERENCES bundles(bundle_uuid, bundle_version),
                FOREIGN KEY (file_uuid, file_version) REFERENCES files(file_uuid, file_version),
                UNIQUE (bundle_uuid, bundle_version, file_uuid, file_version)
            );
            CREATE INDEX IF NOT EXISTS bundles_files_bundle_uuid ON bundles_files USING btree (bundle_uuid);
            CREATE INDEX IF NOT EXISTS bundles_files_file_uuid ON bundles_files USING btree (file_uuid);
        """
        )

    @requires_admin_mode
    def destroy(self):
        self._cursor.execute("DROP TABLE IF EXISTS bundles_files")
