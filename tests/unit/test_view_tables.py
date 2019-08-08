import json
import unittest

from dcpquery import config
from dcpquery.db import BundleFileLink, File, Bundle, DCPMetadataSchemaType
from dcpquery.etl import dcpquery_etl_finalizer, create_view_tables, update_process_join_table
from tests import load_fixture


class TestViewTables(unittest.TestCase):
    vx_bundle_uuid = '0c8d7f15-47c2-42c2-83de-47ae48e1eae1'

    @classmethod
    def setUpClass(cls):
        vx_bundle_version = '2018-10-06T190237.485774Z'
        vx_bundle_fqid = f'{cls.vx_bundle_uuid}.{vx_bundle_version}'
        vx_bundle_manifest = load_fixture('vx_bundle_later_version.json')
        vx_bundle_aggregate_md = json.loads(load_fixture('vx_bundle_document.json'))

        vx_bundle = Bundle(fqid=vx_bundle_fqid,
                           manifest=json.loads(vx_bundle_manifest),
                           aggregate_metadata=vx_bundle_aggregate_md)
        vx_bf_links = []

        for f in json.loads(vx_bundle_manifest)['files']:
            if f["content-type"] == "application/json":
                f_row = File(uuid=f["uuid"], version=f["version"], body=json.loads(load_fixture(f["name"])),
                             content_type=f["content-type"], size=f["size"])
                vx_bf_links.append(BundleFileLink(bundle=vx_bundle, file=f_row, name=f["name"]))

        config.db_session.add_all(vx_bf_links)

        config.db_session.commit()

        create_view_tables()
        update_process_join_table()

    def test_db_views_exist_for_each_schema_type(self):
        from dcpquery import config

        views = sorted([view[0] for view in config.db_session.execute(
            """
            SELECT table_name FROM INFORMATION_SCHEMA.views
            WHERE table_schema = ANY (current_schemas(false))
            """
        ).fetchall()])
        views.remove('files')
        views.remove('bundles')

        schema_types = sorted(
            [schema[0] for schema in config.db_session.query(DCPMetadataSchemaType).with_entities(
                DCPMetadataSchemaType.name).all()])

        self.assertEqual(views, schema_types)

    def test_biomaterial_view_table_contains_all_biomaterial_files(self):
        from dcpquery import config

        biomaterial_view_table_count = config.db_session.execute(
            """
            SELECT count(*) from cell_line;
            """
        ).fetchall()[0][0]

        files_of_type_biomaterial_count = config.db_session.execute(
            """
            SELECT count(*) from files where dcp_schema_type_name='cell_line';
            """
        ).fetchall()[0][0]
        self.assertEqual(biomaterial_view_table_count, files_of_type_biomaterial_count)

    def test_bundle_view_table_only_contains_latest_version(self):
        bundle_versions = config.db_session.execute(
            """
            SELECT version from bundles_all_versions where uuid=:uuid
            """, [{'uuid': self.vx_bundle_uuid}]
        ).fetchall()

        self.assertEqual(len(bundle_versions), 2)
        versions = sorted([x[0] for x in bundle_versions])

        latest_version = config.db_session.execute(
            """
            SELECT version from bundles where uuid=:uuid
            """, [{'uuid': self.vx_bundle_uuid}]
        ).fetchall()
        self.assertEqual(len(latest_version), 1)
        self.assertEqual(latest_version[0][0], versions[-1])

    def test_file_view_table_only_contains_latest_version(self):
        file_uuid = 'd96015ad-0783-454a-a836-264391c60b02'
        file_versions = config.db_session.execute(
            """
            SELECT version from files_all_versions where uuid=:uuid
            """, [{'uuid': file_uuid}]
        ).fetchall()

        self.assertEqual(len(file_versions), 2)
        versions = sorted([x[0] for x in file_versions])

        latest_version = config.db_session.execute(
            """
            SELECT version from files where uuid=:uuid
            """, [{'uuid': file_uuid}]
        ).fetchall()
        self.assertEqual(len(latest_version), 1)
        self.assertEqual(latest_version[0][0], versions[-1])

    def test_bundles_table_contains_latest_version_of_all_bundles(self):
        all_bundles_count = config.db_session.execute(
            """
            SELECT count(*) from bundles_all_versions;
            """
        ).fetchall()[0][0]

        unique_uuids_count = config.db_session.execute(
            """
            SELECT count(DISTINCT(uuid)) from bundles_all_versions;
            """
        ).fetchall()[0][0]

        latest_version_bundle_count = config.db_session.execute(
            """
            SELECT count(*) from bundles;
            """
        ).fetchall()[0][0]

        latest_version_unique_uuid_count = config.db_session.execute(
            """
            SELECT count(DISTINCT(uuid)) from bundles;
            """
        ).fetchall()[0][0]

        self.assertGreater(all_bundles_count, latest_version_bundle_count)
        self.assertEqual(unique_uuids_count, latest_version_bundle_count, latest_version_unique_uuid_count)

    def test_file_table_contains_latest_version_of_all_files(self):
        all_files_count = config.db_session.execute(
            """
            SELECT count(*) from files_all_versions;
            """
        ).fetchall()[0][0]

        unique_uuids_count = config.db_session.execute(
            """
            SELECT count(DISTINCT(uuid)) from files_all_versions;
            """
        ).fetchall()[0][0]

        latest_version_file_count = config.db_session.execute(
            """
            SELECT count(*) from files;
            """
        ).fetchall()[0][0]

        latest_version_unique_uuid_count = config.db_session.execute(
            """
            SELECT count(DISTINCT(uuid)) from files;
            """
        ).fetchall()[0][0]

        self.assertGreater(all_files_count, latest_version_file_count)
        self.assertEqual(unique_uuids_count, latest_version_file_count, latest_version_unique_uuid_count)
