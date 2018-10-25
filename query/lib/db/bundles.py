import typing
from dateutil.parser import parse as parse_datetime
from uuid import UUID

from lib.model import datetime_to_version
from lib.config import requires_admin_mode
from lib.db.table import Table


class Bundles(Table):

    def insert(self, uuid: UUID, version: str, file_uuid: UUID, file_version: str) -> int:
        self._cursor.execute(
            """
            INSERT INTO bundles (uuid, version, file_uuid, file_version)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (uuid, version, file_uuid, file_version) DO NOTHING
            """,
            (
                str(uuid),
                parse_datetime(version),
                str(file_uuid),
                parse_datetime(file_version)
            )
        )
        result = self._cursor.rowcount
        return result

    def select(self, uuid: UUID, version: str) -> typing.List[dict]:
        self._cursor.execute(
            """
            SELECT uuid, version, file_uuid, file_version
            FROM bundles
            WHERE uuid = %s AND version = %s
            """,
            (
                str(uuid),
                parse_datetime(version),
            )
        )
        response = self._cursor.fetchall()
        return [
            dict(
                uuid=ele[0],
                version=datetime_to_version(ele[1]),
                file_uuid=ele[2],
                file_version=datetime_to_version(ele[3])
            ) for ele in response
        ]

    @requires_admin_mode
    def initialize(self):
        self._cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS bundles (
                uuid UUID,
                version timestamp NOT NULL,
                file_uuid UUID NOT NULL,
                file_version timestamp NOT NULL,
                FOREIGN KEY (file_uuid, file_version) REFERENCES files(uuid, version),
                PRIMARY KEY (uuid, version, file_uuid, file_version)
            );
            CREATE INDEX IF NOT EXISTS bundles_bundle_uuid ON bundles USING btree (uuid);
            CREATE INDEX IF NOT EXISTS bundles_bundle_uuid_version ON bundles USING btree (uuid, version);
            CREATE INDEX IF NOT EXISTS bundles_files_file_uuid ON bundles USING btree (file_uuid);
        """
        )

    @requires_admin_mode
    def destroy(self):
        self._cursor.execute("DROP TABLE bundles")
