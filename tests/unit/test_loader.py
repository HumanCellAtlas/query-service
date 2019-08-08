import json, unittest, secrets

from unittest.mock import patch

from dcpquery import config
from dcpquery.db import Bundle, DCPMetadataSchemaType

from tests import (vx_bundle, vx_bundle_uuid, vx_bundle_version, vx_bundle_manifest, vx_bundle_aggregate_md, mock_links,
                   load_fixture)
from dcpquery.etl import load_links, create_process_file_links, BundleLoader, dcpquery_etl_finalizer


class TestPostgresLoader(unittest.TestCase):
    _test_identifier = secrets.token_hex(16)

    def setUp(self):
        load_links(mock_links['links'], 'mock_bundle_uuid')

    def test_db_views_exist_for_each_schema_type(self):
        from dcpquery import config

        views = [view[0] for view in config.db_session.execute(
            """
            SELECT table_name FROM INFORMATION_SCHEMA.views
            WHERE table_schema = ANY (current_schemas(false))
            """
        ).fetchall()]

        schema_types = [schema[0] for schema in
                        config.db_session.query(DCPMetadataSchemaType).with_entities(DCPMetadataSchemaType.name).all()]
        schema_types.append('bundles')
        schema_types.append('files')
        self.assertEqual(sorted(views), sorted(schema_types))

    def test_biomaterial_view_table_contains_all_biomaterial_files(self):
        from dcpquery import config
        dcpquery_etl_finalizer('mock_extractor')

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

    @unittest.skip("WIP")
    def test_prepare_database(self):
        with self.db.transaction() as (_, tables):
            result = set(tables.files.select_views())
            implied_views = set(f.schema_type_plural for f in vx_bundle.files if f.normalizable)
            self.assertEqual(result & implied_views, implied_views)

    def test_insert_into_database(self):
        config.reset_db_session()
        files = []
        for f in json.loads(vx_bundle_manifest)['files']:
            if f["content-type"] == "application/json":
                body = json.loads(load_fixture(f["name"]))
                file_dict = {
                    "name": f["name"],
                    "uuid": f["uuid"],
                    "version": f["version"],
                    "body": body,
                    "content-type": f["content-type"],
                    "size": f["size"],
                    "schema_type": body["schema_type"]
                }
                files.append(file_dict)
        BundleLoader().load_bundle(dict(uuid=vx_bundle_uuid,
                                        version=vx_bundle_version,
                                        manifest=json.loads(vx_bundle_manifest),
                                        aggregate_metadata=vx_bundle_aggregate_md,
                                        files=files))
        res = config.db_session.query(Bundle).filter(Bundle.uuid == vx_bundle_uuid,
                                                     Bundle.version == vx_bundle_version)
        result = list(res)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].uuid, vx_bundle_uuid)
        self.assertEqual(result[0].version.strftime("%Y-%m-%dT%H%M%S.%fZ"), vx_bundle_version)
        self.assertDictEqual(result[0].manifest, json.loads(vx_bundle_manifest))
        self.assertDictEqual(result[0].aggregate_metadata, vx_bundle_aggregate_md)

    @patch('dcpquery.config.db_session.add_all')
    @patch('dcpquery.etl.ProcessFileLink', )
    def test_create_processes_calls_insert_correct_number_times(self, mock_process_file_link, mock_add_all):
        mock_process = {'process_uuid': 'a0000006-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
                        'input_file_uuids': ["b0000011-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                                             "b0000012-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                                             'b0000013-aaaa-aaaa-aaaa-aaaaaaaaaaaa'],
                        'output_file_uuids': ["b0000014-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                                              "b0000015-aaaa-aaaa-aaaa-aaaaaaaaaaaa"],
                        'protocol_uuids': ['c0000010-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
                                           'c0000011-aaaa-aaaa-aaaa-aaaaaaaaaaaa']}
        create_process_file_links(mock_process)
        assert mock_process_file_link.call_count == 7


if __name__ == '__main__':
    unittest.main()
