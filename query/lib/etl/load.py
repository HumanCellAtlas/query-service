import pylru
from psycopg2 import IntegrityError

from query.lib.etl.transform import BundleDocumentTransform
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
        self._inserted_files = pylru.lrucache(1000)

    def load(self, bundle: Bundle, transformed_bundle: dict):
        with self._db.transaction() as (_, tables):
            self._prepare_database(tables, bundle)
        with self._db.transaction() as (_, tables):
            self._insert_into_database(tables, bundle, transformed_bundle)

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
                if file.metadata.name == "links.json":
                    self.load_links(tables, file['links'])
            self._inserted_files[file.fqid] = True
            tables.bundles_files.insert(
                bundle_uuid=bundle.uuid,
                bundle_version=bundle.version,
                file_uuid=file.uuid,
                file_version=file.metadata.version
            )

    def load_links(self, tables, links):
        for link in links:
            process = BundleDocumentTransform.format_process_info(link)
            process['children'] = list(self.get_child_process_uuids(tables, process['output_file_uuids']))
            process['parents'] = list(self.get_parent_process_uuids(tables, process['input_file_uuids']))
            self.create_processes(tables, process)
            self.link_parent_and_child_processes(tables, process)

    def create_processes(self, tables, process):
        input_file_uuids = process['input_file_uuids']
        output_file_uuids = process['output_file_uuids']
        protocol_uuids = process['protocol_uuids']

        for file_uuid in input_file_uuids:
            tables.process_links.insert(process['process_uuid'], file_uuid, 'INPUT_ENTITY')

        for file_uuid in output_file_uuids:
            tables.process_links.insert(process['process_uuid'], file_uuid, 'OUTPUT_ENTITY')

        for file_uuid in protocol_uuids:
            tables.process_links.insert(process['process_uuid'], file_uuid, 'PROTOCOL_ENTITY')

    def link_parent_and_child_processes(self, tables: Tables, process: object):
        already_linked_parents = tables.process_links.list_direct_parent_process_uuids(process['process_uuid'])
        already_linked_children = tables.process_links.list_direct_children_process_uuids(process['process_uuid'])

        parents = [x for x in process['parents'] if x not in already_linked_parents]
        children = [x for x in process['children'] if x not in already_linked_children]

        for parent in parents:
            tables.process_links.insert_parent_child_link(parent_process_uuid=parent,
                                                          child_process_uuid=process['process_uuid'])
        for child in children:
            tables.process_links.insert_parent_child_link(parent_process_uuid=process['process_uuid'],
                                                          child_process_uuid=child)

    def get_child_process_uuids(self, tables: Tables, output_file_uuids):
        children = []
        for file_uuid in output_file_uuids:
            child_uuids = tables.process_links.list_process_uuids_for_file_uuid(file_uuid, 'INPUT_ENTITY')
            children = children + child_uuids
        return list(set(children))

    def get_parent_process_uuids(self, tables: Tables, input_file_uuids):
        parents = []
        for file_uuid in input_file_uuids:
            parent_uuids = tables.process_links.list_process_uuids_for_file_uuid(file_uuid, 'OUTPUT_ENTITY')
            parents = parents + parent_uuids
        return list(set(parents))
