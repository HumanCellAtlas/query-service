from dateutil.parser import parse as parse_datetime
from uuid import UUID

from psycopg2 import DatabaseError
from psycopg2.extras import Json

from lib.config import requires_admin_mode
from lib.model import datetime_to_version
from lib.db.table import Table


class Bundles(Table):

    def insert(self, uuid: UUID, version: str, json_as_dict: dict) -> int:
        self._cursor.execute(
            """
            INSERT INTO bundles (uuid, version, json)
            VALUES (%s, %s, %s)
            ON CONFLICT (uuid, version) DO NOTHING
            """,
            (str(uuid), parse_datetime(version), Json(json_as_dict))
        )
        result = self._cursor.rowcount
        return result

    def select(self, uuid: UUID, version: str) -> dict:
        self._cursor.execute(
            """
            SELECT uuid, version, json
            FROM bundles
            WHERE uuid = %s AND version = %s
            """,
            (str(uuid), parse_datetime(version))
        )
        response = self._cursor.fetchall()
        if len(response) > 1:
            raise DatabaseError(
                f"Uniqueness constraint broken for uuid={uuid}, version={version}"
            )
        return dict(
            uuid=response[0][0],
            version=datetime_to_version(response[0][1]),
            json=response[0][2]
        ) if len(response) == 1 else None

    @requires_admin_mode
    def initialize(self):
        self._cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS bundles (
                uuid UUID NOT NULL,
                version timestamp NOT NULL,
                json JSONB NOT NULL,
                PRIMARY KEY(uuid, version)
            );
            
            CREATE INDEX IF NOT EXISTS bundles_uuid ON bundles USING btree (uuid);
            """
        )

    @requires_admin_mode
    def destroy(self):
        self._cursor.execute("DROP TABLE bundles CASCADE;")

