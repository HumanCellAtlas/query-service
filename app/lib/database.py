import re
import typing
from contextlib import contextmanager
from dateutil.parser import parse as parse_datetime
from uuid import UUID

from psycopg2 import DatabaseError, sql
from psycopg2.extras import Json
import psycopg2
import psycopg2.extras

from lib.config import requires_admin_mode
from lib.logger import logger
from lib.model import datetime_to_version

# http://initd.org/psycopg/docs/faq.html#faq-jsonb-adapt
psycopg2.extras.register_json(oid=3802, array_oid=3807, globally=True)


class PostgresDatabase:

    def __init__(self, connection_uri: str):
        self._connection_uri = connection_uri
        self._connection = self._connect()

    def _connect(self):
        return psycopg2.connect(self._connection_uri)

    @contextmanager
    def transaction(self):
        if self._connection.closed != 0:
            logger.info(f"Reconnecting to database...")
            self._connection = self._connect()
        try:
            with self._connection.cursor() as cursor:
                yield Transaction(cursor)
            self._connection.commit()
        except DatabaseError as e:
            logger.exception("Database error")
            self._connection.rollback()


class Transaction:

    _valid_table_name = re.compile('^[a-zA-Z]+[a-zA-Z0-9_]*[a-zA-Z0-9]+$')

    def __init__(self, cursor):
        assert(cursor is not None)
        self._cursor = cursor

    def create_metadata_file_view(self, table_name: str, module: str):
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

    def insert_bundle(self, uuid: UUID, version: str, json_as_dict: dict) -> int:
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

    def insert_metadata_file(self, module: str, uuid: UUID, version: str, json_as_dict: dict) -> int:
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

    def insert_join(self, bundle_uuid: UUID, bundle_version: str, file_uuid: UUID, file_version: str) -> int:
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

    def delete_bundle(self, uuid: UUID, version: str) -> int:
        self._cursor.execute(
            """
            DELETE FROM bundles
            WHERE uuid = %s AND version = %s
            """,
            (str(uuid), parse_datetime(version))
        )
        result = self._cursor.rowcount
        return result

    def delete_metadata_file(self, module: str, uuid: UUID, version: str) -> int:
        self._cursor.execute(
            """
            DELETE FROM metadata_files
            USING metadata_modules
            WHERE
                metadata_modules.name = %s AND
                metadata_files.module_id = metadata_modules.id AND
                metadata_files.uuid = %s AND
                metadata_files.version = %s
            """,
            (module, str(uuid), parse_datetime(version))
        )
        result = self._cursor.rowcount
        return result

    def select_bundle(self, uuid: UUID, version: str) -> dict:
        self._cursor.execute(
            """
            SELECT uuid, version, json
            FROM bundles
            WHERE uuid = %s AND version = %s
            """,
            (str(uuid), parse_datetime(version))
        )
        return self._response_to_dict(self._cursor.fetchall(), uuid, version)

    def select_metadata_file(self, module: str, uuid: UUID, version: str) -> dict:
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
        return self._response_to_dict(self._cursor.fetchall(), uuid, version)

    @staticmethod
    def _response_to_dict(response, uuid, version):
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
    def initialize_database(self):
        self._cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS bundles (
                uuid UUID NOT NULL,
                version timestamp NOT NULL,
                json JSONB NOT NULL,
                PRIMARY KEY(uuid, version)
            );
            
            CREATE INDEX IF NOT EXISTS bundles_uuid ON bundles USING btree (uuid);
            
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
    def clear_database(self):
        self._cursor.execute(
            """
            CREATE OR REPLACE FUNCTION drop_tables(username IN VARCHAR) RETURNS void AS $$
            DECLARE
                statements CURSOR FOR
                    SELECT tablename FROM pg_tables
                    WHERE tableowner = username AND schemaname = 'public';
            BEGIN
                FOR stmt IN statements LOOP
                    EXECUTE 'DROP TABLE ' || quote_ident(stmt.tablename) || ' CASCADE;';
                END LOOP;
            END;
            $$ LANGUAGE plpgsql;
            
            SELECT drop_tables('master');
            """
        )
