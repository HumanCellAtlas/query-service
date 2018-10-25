import pylru
from psycopg2 import IntegrityError

from lib.logger import logger
from lib.model import Bundle
from lib.db.database import PostgresDatabase, Tables


class Loader:

    def load(self, bundle: Bundle):
        raise NotImplementedError()


class PostgresLoader(Loader):

    def __init__(self, db: PostgresDatabase):
        self._db = db
        self._existing_view_names = set([])
        self._inserted_files = pylru.lrucache(1000)

    def load(self, bundle: Bundle):
        with self._db.transaction() as (_, tables):
            self._prepare_database(tables, bundle)
        with self._db.transaction() as (_, tables):
            self._insert_into_database(tables, bundle)

    def _prepare_database(self, tables: Tables, bundle: Bundle):
        # get table names for tables implied by the bundle manifest
        view_names_to_type_mapping = dict([(f.schema_module_plural, f.schema_module) for f in bundle.files])
        implied_view_names = set(f.schema_module_plural for f in bundle.files if f.normalizable)

        # if there are views implied in the manifest not recorded in PostgresLoader, refresh
        if len(implied_view_names - self._existing_view_names) > 0:
            self._existing_view_names = set(tables.files.select_views())

        # create view tables still outstanding
        for view_name in implied_view_names - self._existing_view_names:
            logger.info(f"Creating view: {view_name}")
            try:
                tables.files.create_view(view_name, view_names_to_type_mapping[view_name])
            except IntegrityError:
                logger.info(f"View already exists: {view_name}")

    def _insert_into_database(self, tables: Tables, bundle: Bundle):
        # insert the bundle
        tables.bundles.insert(bundle)

        # insert files, and join table entry
        for file in bundle.files:
            if file.fqid not in self._inserted_files:
                r = tables.files.insert(file)
            self._inserted_files[file.fqid] = True
