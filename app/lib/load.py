import pylru
from psycopg2 import IntegrityError

from lib.logger import logger
from lib.model import Bundle
from lib.database import PostgresDatabase
from lib.transform import BundleDocumentTransform


class Loader:

    def load(self, bundle: Bundle):
        raise NotImplementedError()


class PostgresLoader(Loader):

    def __init__(self, db: PostgresDatabase):
        self._db = db
        self._existing_view_names = set([])
        self._inserted_metadata_files = pylru.lrucache(1000)

    def load(self, bundle: Bundle):
        with self._db.transaction() as transaction:
            self._prepare_database(transaction, bundle)
        with self._db.transaction() as transaction:
            self._insert_into_database(transaction, bundle)

    def _prepare_database(self, transaction, bundle: Bundle):
        # get table names for tables implied by the bundle manifest
        view_names_to_type_mapping = dict([(f.schema_module_plural, f.schema_module) for f in bundle.normalizable_files])
        implied_view_names = set([f.schema_module_plural for f in bundle.normalizable_files])

        # if there are tables implied in the manifest not recorded in PostgresLoader, refresh
        if len(implied_view_names - self._existing_view_names) > 0:
            self._existing_view_names = set(transaction.list_views())

        # create view tables still outstanding
        for view_name in implied_view_names - self._existing_view_names:
            logger.info(f"Creating view: {view_name}")
            try:
                transaction.create_metadata_file_view(view_name, view_names_to_type_mapping[view_name])
            except IntegrityError:
                logger.info(f"View already exists: {view_name}")

    def _insert_into_database(self, transaction, bundle: Bundle):
        # insert denormalized bundle
        denormalized_bundle = BundleDocumentTransform.transform(bundle)
        transaction.insert_bundle(
            uuid=bundle.uuid,
            version=bundle.version,
            json_as_dict=denormalized_bundle,
        )

        # insert file metadata, and join table entry
        for normalizable_file in bundle.normalizable_files:
            if normalizable_file.fqid not in self._inserted_metadata_files:
                transaction.insert_metadata_file(
                    file_type=normalizable_file.schema_module,
                    uuid=normalizable_file.uuid,
                    version=normalizable_file.metadata.version,
                    json_as_dict=normalizable_file,
                )
            self._inserted_metadata_files[normalizable_file.fqid] = True
            transaction.insert_join(
                bundle_uuid=bundle.uuid,
                bundle_version=bundle.version,
                file_uuid=normalizable_file.uuid,
                file_version=normalizable_file.metadata.version
            )
