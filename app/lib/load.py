from datetime import datetime
from uuid import UUID
from psycopg2 import IntegrityError
from lib.model import Bundle
from lib.database import PostgresDatabase
from lib.transform import BundleDocumentTransform

from lib.logger import logger


class Loader:

    def load(self, bundle: Bundle):
        raise NotImplementedError()


class DatabaseError(Exception):
    pass


class PostgresLoader(Loader):

    def __init__(self, db: PostgresDatabase):
        self._db = db
        self._existing_table_names = set([])

    def load(self, bundle: Bundle):
        with self._db.transaction() as transaction:
            self._prepare_database(transaction, bundle)
            self._insert_into_database(transaction, bundle)

    def _prepare_database(self, transaction, bundle: Bundle):
        # get table names for tables implied by the bundle manifest
        implied_table_names = set([f.schema_module_plural for f in bundle.normalizable_files])
        implied_table_names.add('bundles')
        join_table_name = 'bundles_metadata_files'

        # if there are tables implied in the manifest not recorded in PostgresLoader, refresh
        if len(implied_table_names - self._existing_table_names) > 0 or \
                join_table_name not in self._existing_table_names:
            self._existing_table_names = set(transaction.list_tables())

        # create json tables still outstanding
        for table_name in implied_table_names - self._existing_table_names:
            transaction.create_json_table(table_name)

        # create join table if DNE
        if join_table_name not in self._existing_table_names:
            transaction.create_join_table()

    @staticmethod
    def _insert_into_database(transaction, bundle: Bundle):
        # insert denormalized bundle
        denormalized_bundle = BundleDocumentTransform.transform(bundle)
        transaction.insert(
            table_name='bundles',
            uuid=bundle.uuid,
            json_as_dict=denormalized_bundle,
        )

        # insert file metadata, and join table entry
        for normalizable_file in bundle.normalizable_files:
            # TODO uuids -> fqids
            if normalizable_file.uuid not in self._inserted_metadata_files:
                transaction.insert(
                    table_name=normalizable_file.schema_module_plural,
                    uuid=normalizable_file.uuid,
                    json_as_dict=normalizable_file,
                )
            self._inserted_metadata_files[normalizable_file.uuid] = True

            transaction.insert_join(
                table_name=f"bundles_{normalizable_file.schema_module_plural}",
                bundle_uuid=bundle.uuid,
                file_uuid=normalizable_file.uuid
            )
