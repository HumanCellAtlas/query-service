import json

import pylru
from dateutil.parser import parse as parse_datetime

from psycopg2 import IntegrityError
from sqlalchemy.dialects.postgresql import JSONB, UUID

from query.lib.database.tables import Bundles, Files, SchemaTypes, BundlesFilesLink
from query.lib.database import Database
from query.lib.logger import logger
from query.lib.model import Bundle
from query.lib.db.database import PostgresDatabase, Tables


class Loader:

    def load(self, bundle: Bundle, transformed_bundle: dict):
        raise NotImplementedError()


class PostgresLoader(Loader):

    def __init__(self, db: PostgresDatabase):
        self._db = db
        self._existing_view_names = set([])

    def load(self, bundle: Bundle, transformed_bundle: dict):
        with self._db.transaction() as (_, tables):
            self._prepare_database(tables, bundle)
        with self._db.transaction() as (_, tables):
            self._insert_into_database(tables, bundle, transformed_bundle)

    # do we still need to use views?
    def _prepare_database(self, tables: Tables, bundle: Bundle):
        # get table names for tables implied by the bundle manifest
        view_names_to_type_mapping = dict([(f.schema_type_plural, f.schema_type) for f in bundle.files])
        implied_view_names = set(f.schema_type_plural for f in bundle.files if f.normalizable)

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

    def _insert_into_database(self, tables: Tables, bundle: Bundle, transformed_bundle: dict):
        # insert the bundle
        tables.bundles.insert(bundle, transformed_bundle)

        # insert files, and join table entry
        for file in bundle.files:
            if file.fqid not in self._inserted_files:
                tables.files.insert(file)
            self._inserted_files[file.fqid] = True
            tables.bundles_files.insert(
                bundle_uuid=bundle.uuid,
                bundle_version=bundle.version,
                file_uuid=file.uuid,
                file_version=file.metadata.version
            )


class DatabaseLoader(Loader):
    def __init__(self):
        db_string = 'postgresql://predev:example128@query-predev.cluster-cdaogjt23uha.us-east-1.rds.amazonaws.com:5432/query_predev'
        self.db = Database(db_string)
        self._inserted_files = pylru.lrucache(1000)

    def load(self, bundle, transformed_bundle):
        self._insert_into_database(bundle, transformed_bundle)

    # todo refactor to use orm object instead of bundle model
    def _insert_into_database(self, bundle: Bundle, transformed_bundle: dict):
        files = []
        new_bundle = Bundles(fqid=bundle.fqid, uuid=str(bundle.uuid), version=bundle.version, manifest=transformed_bundle)
        # bundle = self.db.get_or_create_by_fqid(Bundles, fqid=bundle.fqid, uuid=str(bundle.uuid), version=bundle.version, manifest=transformed_bundle)
        from pprint import pprint
        print(f"BUNDLE: {new_bundle}. Contains: {new_bundle.fqid}")
        self.db.insert_one(new_bundle)

        for file in bundle.files:

            if file.fqid not in self._inserted_files:
                schema_type = self.db.get_or_create(SchemaTypes, name=file.schema_type)
                # Todo handle case where same file is contained in different bundle (ie update bundles field)
                # new_file = Files(fqid=file.fqid, uuid=str(file.uuid), version=parse_datetime(file.version),
                #                  name=file.metadata.name, json=(file if file.metadata.indexable else None),
                #                  schema_type=schema_type
                #                  )

                self.db.get_or_create_by_fqid(Files, fqid=file.fqid, uuid=str(file.uuid), version=parse_datetime(file.version),
                                 name=file.metadata.name, json=(file if file.metadata.indexable else None),
                                 schema_type=schema_type)
                self.db.get_or_create(BundlesFilesLink, file_fqid=file.fqid, bundle_fqid=bundle.fqid)
                # bundle_file = BundlesFilesLink(file_fqid=file.fqid, bundle_fqid=bundle.fqid)
                # files.append(bundle_file)
                # self.db.insert_many([new_file, bundle_file])
            # self.db.insert_many(files)
            self._inserted_files[file.fqid] = True
        #
