import typing
from dateutil.parser import parse as parse_datetime
from uuid import UUID

from lib.model import datetime_to_version, Bundle
from lib.config import requires_admin_mode
from lib.db.table import Table


class Bundles(Table):

    def insert(self, bundle: Bundle) -> int:
        self._cursor.execute(
            """
            INSERT INTO bundles (uuid, version, file_fqids)
            VALUES (%s, %s, %s)
            ON CONFLICT (uuid, version) DO NOTHING
            """,
            (
                str(bundle.uuid),
                parse_datetime(bundle.version),
                [f.fqid for f in bundle.files]
            )
        )
        result = self._cursor.rowcount
        return result

    def select(self, uuid: UUID, version: str) -> typing.Optional[dict]:
        self._cursor.execute(
            """
            SELECT uuid, version, file_fqids
            FROM bundles
            WHERE uuid = %s AND version = %s
            """,
            (
                str(uuid),
                parse_datetime(version),
            )
        )
        response = self._cursor.fetchall()
        assert(len(response) <= 1)
        if len(response) == 0:
            return None
        return dict(
            uuid=response[0][0],
            version=datetime_to_version(response[0][1]),
            file_fqids=response[0][2]
        )

    @requires_admin_mode
    def initialize(self):
        self._cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS bundles (
                uuid UUID,
                version timestamp with time zone NOT NULL,
                file_fqids varchar(62)[],
                PRIMARY KEY (uuid),
                UNIQUE (uuid, version)
            );
            CREATE INDEX IF NOT EXISTS bundles_file_fqids ON bundles USING GIN (file_fqids);
        """
        )

    @requires_admin_mode
    def destroy(self):
        self._cursor.execute("DROP TABLE IF EXISTS bundles")
