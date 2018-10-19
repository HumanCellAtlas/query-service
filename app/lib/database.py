import json
import re
from contextlib import contextmanager

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
                uuid UUID PRIMARY KEY NOT NULL,
                json JSONB NOT NULL
            );
            """,
            table_name
        )
        self._cursor.execute(query)

    def create_join_table(self):
        query = self._prepare_statement(
            """
            CREATE TABLE IF NOT EXISTS bundles_metadata_files (
                bundle_uuid UUID REFERENCES bundles(uuid),
                file_uuid UUID NOT NULL
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

    def insert(self, table_name: str, uuid: UUID, json_as_dict: dict) -> int:
        query = self._prepare_statement(
            """
            INSERT INTO {} (uuid, json)
            VALUES (%s, %s)
            ON CONFLICT (uuid) DO NOTHING
            """,
            table_name
        )
        self._cursor.execute(query, (str(uuid), Json(json_as_dict)))

        result = self._cursor.rowcount
        return result

    def insert_join(self, table_name: str, bundle_uuid: UUID, file_uuid: UUID) -> int:
        self._cursor.execute(
            """
            INSERT INTO bundles_metadata_files
            VALUES (%s, %s)
            """,
            (str(bundle_uuid), str(file_uuid))
        )
        result = self._cursor.rowcount
        return result

    def delete(self, table_name: str, uuid: UUID) -> int:
        query = self._prepare_statement(
            """
            DELETE FROM {}
            WHERE uuid = %s
            """,
            table_name
        )
        self._cursor.execute(query, (str(uuid),))
        result = self._cursor.rowcount
        return result

    def select(self, table_name: str, uuid: UUID) -> dict:
        query = self._prepare_statement(
            """
            SELECT uuid, json
            FROM {}
            WHERE uuid = %s
            """,
            table_name
        )
        self._cursor.execute(query, (str(uuid),))
        result = self._cursor.fetchall()
        if len(result) > 1:
            raise DatabaseError(
                f"Uniqueness constraint broken for uuid={uuid}"
            )
        return dict(
            uuid=result[0][0],
            json=result[0][1]
        ) if len(result) == 1 else None

    @classmethod
    def _prepare_statement(cls, statement: str, *table_names):
        for table_name in table_names:
            if not cls._valid_table_name.match(table_name):
                raise Exception(f"Not a valid table name: \"{table_name}\"")
        return sql.SQL(statement.format(*table_names))


