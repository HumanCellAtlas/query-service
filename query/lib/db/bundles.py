import typing
from dateutil.parser import parse as parse_datetime
from uuid import UUID

from lib.model import datetime_to_version
from lib.config import requires_admin_mode
from lib.db.table import Table


class Bundles(Table):

    def insert(self, uuid: UUID, version: str) -> int:
        self._cursor.execute(
            """
            INSERT INTO bundles (uuid, version)
            VALUES (%s, %s)
            ON CONFLICT (uuid, version) DO NOTHING
            """,
            (
                str(uuid),
                parse_datetime(version)
            )
        )
        result = self._cursor.rowcount
        return result

    def select(self, uuid: UUID, version: str) -> typing.Optional[dict]:
        self._cursor.execute(
            """
            SELECT uuid, version
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
            version=datetime_to_version(response[0][1])
        )

    @requires_admin_mode
    def initialize(self):
        self._cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS bundles (
                uuid UUID,
                version timestamp with time zone NOT NULL,
                PRIMARY KEY (uuid, version)
            );
            CREATE INDEX IF NOT EXISTS bundles_uuid ON bundles USING btree (uuid);
        """
        )

    @requires_admin_mode
    def destroy(self):
        self._cursor.execute("DROP TABLE IF EXISTS bundles")
