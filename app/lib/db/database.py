from contextlib import contextmanager
from typing import NamedTuple

from psycopg2 import DatabaseError
import psycopg2
import psycopg2.extras

from lib.db.bundles import Bundles
from lib.db.bundles_metadata_files import BundlesMetadataFiles
from lib.db.metadata_files import MetadataFiles
from lib.logger import logger


class Transaction(NamedTuple):
    bundles: Bundles
    bundles_metadata_files: BundlesMetadataFiles
    metadata_files: MetadataFiles


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
                yield Transaction(
                    bundles=Bundles(cursor),
                    bundles_metadata_files=BundlesMetadataFiles(cursor),
                    metadata_files=MetadataFiles(cursor),
                )
            self._connection.commit()
        except DatabaseError as e:
            logger.exception("Database error")
            self._connection.rollback()


