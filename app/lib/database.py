import re
from contextlib import contextmanager
from datetime import datetime
from dateutil.parser import parse as parse_datetime

import psycopg2
import psycopg2.extras
from psycopg2 import OperationalError, sql
from psycopg2.extras import Json

from lib.logger import logger
from uuid import UUID

# http://initd.org/psycopg/docs/faq.html#faq-jsonb-adapt
psycopg2.extras.register_json(oid=3802, array_oid=3807, globally=True)


class DatabaseError(Exception):
    pass


class PostgresDatabase:

    def __init__(self, connection_uri: str):
        self._connection_uri = connection_uri
        self._connection = self._connect()

    def _connect(self):
        return psycopg2.connect(self._connection_uri)

    @contextmanager
    def transaction(self):
        try:
            with self._connection.cursor() as cursor:
                yield Transaction(cursor)
                self._connection.commit()
        except OperationalError as e:
            logger.error("Error connecting", e)
            self._connection = self._connect()
            with self._connection.cursor() as cursor:
                yield Transaction(cursor)
                self._connection.commit()


class Transaction:

    _valid_table_name = re.compile('^[a-zA-Z]+[a-zA-Z0-9_]*[a-zA-Z0-9]+$')

    def __init__(self, cursor):
        assert(cursor is not None)
        self._cursor = cursor

    def create_json_table(self, table_name: str):
        query = self._prepare_statement(
            """
            CREATE TABLE IF NOT EXISTS {} (
                uuid UUID NOT NULL,
                version timestamp NOT NULL,
                json JSONB NOT NULL,
                PRIMARY KEY(uuid, version)
            );
            """,
            table_name
        )
        self._cursor.execute(query)

    def create_join_table(self):
        query = self._prepare_statement(
            """
            CREATE TABLE IF NOT EXISTS bundles_metadata_files (
                bundle_uuid UUID,
                bundle_version timestamp NOT NULL,
                file_uuid UUID NOT NULL,
                file_version timestamp NOT NULL,
                FOREIGN KEY (bundle_uuid, bundle_version) REFERENCES bundles(uuid, version),
                UNIQUE (bundle_uuid, bundle_version, file_uuid, file_version)
            );
            """
        )
        self._cursor.execute(query)

    def list_tables(self):
        self._cursor.execute(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE
                table_type = 'BASE TABLE' AND
                table_schema NOT IN ('pg_catalog', 'information_schema') AND
                table_schema = 'public'
            """
        )
        result = [ele[0] for ele in self._cursor.fetchall()]
        return result

    def insert(self, table_name: str, uuid: UUID, version: str, json_as_dict: dict) -> int:
        query = self._prepare_statement(
            """
            INSERT INTO {} (uuid, version, json)
            VALUES (%s, %s, %s)
            ON CONFLICT (uuid, version) DO NOTHING
            """,
            table_name
        )
        self._cursor.execute(
            query,
            (str(uuid), parse_datetime(version), Json(json_as_dict))
        )

        result = self._cursor.rowcount
        return result

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

    def delete(self, table_name: str, uuid: UUID, version: str) -> int:
        query = self._prepare_statement(
            """
            DELETE FROM {}
            WHERE uuid = %s AND version = %s
            """,
            table_name
        )
        self._cursor.execute(query, (str(uuid), parse_datetime(version)))
        result = self._cursor.rowcount
        return result

    def select(self, table_name: str, uuid: UUID, version: str) -> dict:
        query = self._prepare_statement(
            """
            SELECT uuid, version, json
            FROM {}
            WHERE uuid = %s AND version = %s
            """,
            table_name
        )
        self._cursor.execute(query, (str(uuid), parse_datetime(version)))
        result = self._cursor.fetchall()
        if len(result) > 1:
            raise DatabaseError(
                f"Uniqueness constraint broken for uuid={uuid}, version={version}"
            )
        return dict(
            uuid=result[0][0],
            version=datetime_to_version(result[0][1]),
            json=result[0][2]
        ) if len(result) == 1 else None

    @classmethod
    def _prepare_statement(cls, statement: str, *table_names):
        for table_name in table_names:
            if not cls._valid_table_name.match(table_name):
                raise Exception(f"Not a valid table name: \"{table_name}\"")
        return sql.SQL(statement.format(*table_names))


def datetime_to_version(timestamp: datetime) -> str:
    return timestamp.strftime("%Y-%m-%dT%H%M%S.%fZ")
