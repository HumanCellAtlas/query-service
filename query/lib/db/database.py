from contextlib import contextmanager
from typing import NamedTuple

from psycopg2 import DatabaseError
import psycopg2
import psycopg2.extras

from query.lib.common.exceptions import DatabaseException
from query.lib.db.job_status import JobStatus
from query.lib.db.bundles import Bundles
from query.lib.db.files import Files
from query.lib.db.bundles_files import BundlesFiles
from query.lib.logger import logger


class Tables(NamedTuple):
    bundles: Bundles
    files: Files
    bundles_files: BundlesFiles
    job_status: JobStatus


class PostgresDatabase:

    def __init__(self, connection_uri: str):
        self._connection_uri = connection_uri
        self._connection = self._connect()
        self._read_only_connection = self._connect()
        self._read_only_connection.set_session(readonly=True)

    def _connect(self):
        return psycopg2.connect(self._connection_uri)

    @contextmanager
    def transaction(self):
        if self._connection.closed != 0:
            logger.info(f"Reconnecting to database...")
            self._connection = self._connect()
        try:
            with self._connection.cursor() as cursor:
                yield cursor, Tables(
                    bundles=Bundles(cursor),
                    files=Files(cursor),
                    bundles_files=BundlesFiles(cursor),
                    job_status=JobStatus(cursor)
                )
            self._connection.commit()
        except DatabaseError as e:
            logger.exception(f"Database error: {e}")
            self._connection.rollback()

    @contextmanager
    def read_only_transaction(self):
        if self._read_only_connection.closed != 0:
            logger.info(f"Reconnecting to database...")
            self._read_only_connection = self._connect()
            self._read_only_connection.set_session(readonly=True)
        try:
            with self._read_only_connection.cursor() as cursor:
                yield cursor
            self._read_only_connection.commit()
        except DatabaseError as e:
            self._read_only_connection.commit()
            raise DatabaseException(title="Database error, ROT", detail=e, status=123)

    def run_read_only_query(self, query):
        with self.read_only_transaction() as cursor:
            cursor.execute(query)
            column_names = map(lambda x: x[0], cursor.description)
            return cursor.fetchall(), list(column_names)



