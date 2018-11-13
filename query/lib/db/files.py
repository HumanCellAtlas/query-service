import re
import typing
from dateutil.parser import parse as parse_datetime
from uuid import UUID

from psycopg2 import DatabaseError, sql
from psycopg2.extras import Json

from lib.db.table import Table
from lib.model import datetime_to_version, File
from lib.config import requires_admin_mode


class Files(Table):

    _valid_table_name = re.compile('^[a-zA-Z]+[a-zA-Z0-9_]*[a-zA-Z0-9]+$')

    def create_view(self, table_name: str, schema_type: str):
        query = self._prepare_statement(
            """
            CREATE OR REPLACE VIEW {} AS
            SELECT f.* FROM files as f
            JOIN schema_types as m on f.schema_type_id = m.id
            WHERE m.name = %s
            """,
            table_name
        )
        self._cursor.execute(query, (schema_type,))

    def select_views(self) -> typing.List[str]:
        self._cursor.execute(
            """
            SELECT table_name
            FROM INFORMATION_SCHEMA.views
            WHERE table_schema = ANY (current_schemas(false))
            """
        )
        result = [ele[0] for ele in self._cursor.fetchall()]
        return result

    def insert(self, file: File) -> int:
        if file.schema_type:
            self._cursor.execute(
                """
                INSERT INTO schema_types (name)
                VALUES (%s)
                ON CONFLICT (name) DO NOTHING;

                INSERT INTO files (uuid, version, fqid, name, schema_type_id, json) (
                    SELECT %s, %s, %s, %s, id, %s
                    FROM schema_types
                    WHERE schema_types.name = %s
                )
                ON CONFLICT (uuid, version) DO NOTHING;
                """,
                (
                    file.schema_type,
                    str(file.uuid),
                    parse_datetime(file.version),
                    f"{file.uuid}.{file.version}",
                    file.metadata.name,
                    Json(file if file.metadata.indexable else None),
                    file.schema_type
                )
            )
        else:
            self._cursor.execute(
                """
                INSERT INTO files (uuid, version, fqid, name, schema_type_id, json) (
                    SELECT %s, %s, %s, %s, id, %s
                    FROM schema_types
                    WHERE schema_types.name is NULL
                )
                ON CONFLICT (uuid, version) DO NOTHING;
                """,
                (
                    str(file.uuid),
                    parse_datetime(file.version),
                    f"{file.uuid}.{file.version}",
                    file.metadata.name,
                    Json(file if file.metadata.indexable else None)
                )
            )
        return self._cursor.rowcount

    def select(self, uuid: UUID, version: str) -> dict:
        self._cursor.execute(
            """
            SELECT uuid, version, fqid, files.name, json
            FROM files
            WHERE
                files.uuid = %s AND
                files.version = %s
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
            fqid=response[0][2],
            name=response[0][3],
            json=response[0][4]
        ) if len(response) == 1 else None

    @classmethod
    def _prepare_statement(cls, statement: str, *table_names):
        for table_name in table_names:
            if not cls._valid_table_name.match(table_name):
                raise Exception(f"Not a valid table name: \"{table_name}\"")
        return sql.SQL(statement.format(*table_names))

    @requires_admin_mode
    def initialize(self):
        self._cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_types (
                id SERIAL,
                name varchar(128) UNIQUE,
                PRIMARY KEY (id)
            );

            INSERT INTO schema_types (name)
            VALUES (NULL)
            ON CONFLICT (name) DO NOTHING;

            CREATE TABLE IF NOT EXISTS files (
                uuid UUID NOT NULL,
                version timestamp with time zone NOT NULL,
                fqid varchar(62) NOT NULL,
                name varchar(128) NOT NULL,
                schema_type_id SERIAL REFERENCES schema_types(id),
                json JSONB,
                PRIMARY KEY(uuid, version),
                UNIQUE (uuid, version, fqid, schema_type_id)
            );
            CREATE INDEX IF NOT EXISTS files_uuid ON files USING btree (uuid);
            CREATE INDEX IF NOT EXISTS files_fqid ON files USING btree (fqid);
            CREATE INDEX IF NOT EXISTS files_jsonb_gin_index ON files USING GIN (json);
            """
        )

    @requires_admin_mode
    def destroy(self):
        self._cursor.execute(
            """
            DROP TABLE IF EXISTS files CASCADE;
            DROP TABLE IF EXISTS schema_types CASCADE;
            """
        )
