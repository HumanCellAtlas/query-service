import typing
from dateutil.parser import parse as parse_datetime
from uuid import UUID
from psycopg2.extras import Json

from query.lib.model import datetime_to_version, Bundle
from query.lib.config import requires_admin_mode
from query.lib.db.table import Table


class Bundles(Table):

    def insert(self, bundle: Bundle, transformed_bundle: dict) -> int:
        fqids = [f.fqid for f in bundle.files]
        self._cursor.execute(
            """
            INSERT INTO bundles (bundle_uuid, bundle_version, file_fqids, json)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (bundle_uuid, bundle_version) DO NOTHING
            """,
            (
                str(bundle.uuid),
                parse_datetime(bundle.version),
                fqids,
                Json(transformed_bundle)
            )
        )
        result = self._cursor.rowcount
        return result

    def select(self, uuid: UUID, version: str) -> typing.Optional[dict]:
        self._cursor.execute(
            """
            SELECT bundle_uuid, bundle_version, file_fqids, json
            FROM bundles
            WHERE bundle_uuid = %s AND bundle_version = %s
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
            file_fqids=response[0][2],
            json=response[0][3]
        )

    @requires_admin_mode
    def initialize(self):
        self._cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS bundles (
                bundle_uuid UUID,
                bundle_version timestamp with time zone NOT NULL,
                file_fqids text[],
                json jsonb NOT NULL,
                PRIMARY KEY (bundle_uuid),
                UNIQUE (bundle_uuid, bundle_version)
            );
            CREATE INDEX IF NOT EXISTS bundles_json ON bundles USING GIN (json);
            CREATE INDEX IF NOT EXISTS bundles_file_fqids_array ON bundles USING GIN (file_fqids);
        """
        )

    @requires_admin_mode
    def destroy(self):
        self._cursor.execute("DROP TABLE IF EXISTS bundles")
