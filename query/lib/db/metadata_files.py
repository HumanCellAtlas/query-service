import re
import typing
from dateutil.parser import parse as parse_datetime
from uuid import UUID

from psycopg2 import DatabaseError, sql
from psycopg2.extras import Json

from lib.db.table import Table
from lib.model import datetime_to_version
from lib.config import requires_admin_mode


class MetadataFiles(Table):

    _valid_table_name = re.compile('^[a-zA-Z]+[a-zA-Z0-9_]*[a-zA-Z0-9]+$')

    def create_view(self, table_name: str, module: str):
        query = self._prepare_statement(
            """
            CREATE OR REPLACE VIEW {} AS
            SELECT * FROM metadata_files
            JOIN metadata_modules on metadata_files.module_id = metadata_modules.id
            WHERE metadata_modules.name = %s
            """,
            table_name
        )
        self._cursor.execute(query, (module,))

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

    def insert(self, module: str, uuid: UUID, version: str, json_as_dict: dict) -> int:
        self._cursor.execute(
            """
            INSERT INTO metadata_modules (name)
            VALUES (%s)
            ON CONFLICT (name) DO NOTHING;
            
            INSERT INTO metadata_files (uuid, version, module_id, json) (
                SELECT %s, %s, id, %s
                FROM metadata_modules
                WHERE name = %s
            )
            ON CONFLICT (uuid, version) DO NOTHING;
            """,
            (module, str(uuid), parse_datetime(version), Json(json_as_dict), module)
        )
        return self._cursor.rowcount

    def select(self, module: str, uuid: UUID, version: str) -> dict:
        self._cursor.execute(
            """
            SELECT uuid, version, json
            FROM metadata_files
            JOIN metadata_modules on metadata_files.module_id = metadata_modules.id
            WHERE
                metadata_files.uuid = %s AND
                metadata_files.version = %s AND
                metadata_modules.name = %s
            """,
            (str(uuid), parse_datetime(version), module)
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
            CREATE TABLE IF NOT EXISTS metadata_modules (
                id SERIAL,
                name varchar(128) UNIQUE NOT NULL,
                PRIMARY KEY (id)
            );
            CREATE TABLE IF NOT EXISTS metadata_files (
                uuid UUID NOT NULL,
                version timestamp NOT NULL,
                module_id SERIAL REFERENCES metadata_modules(id),
                json JSONB NOT NULL,
                PRIMARY KEY(uuid, version),
                UNIQUE (uuid, version, module_id)
            );
            CREATE INDEX metadata_files_jsonb_gin_index ON metadata_files USING GIN (json);
            """
        )

    @requires_admin_mode
    def destroy(self):
        self._cursor.execute(
            """
            DROP TABLE metadata_files CASCADE;
            DROP TABLE metadata_modules CASCADE;
            """
        )
