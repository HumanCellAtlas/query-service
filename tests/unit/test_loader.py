import unittest, secrets

from unittest.mock import patch

from dcpquery.db import DCPMetadataSchemaType
from dcpquery.etl import load_links, get_child_process_uuids, get_parent_process_uuids, create_process_file_links, \
    link_parent_and_child_processes, create_view_tables
from tests import vx_bundle, mock_links


class TestPostgresLoader(unittest.TestCase):
    _test_identifier = secrets.token_hex(16)

    def setUp(self):
        load_links(mock_links['links'])

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
        self.assertEqual(views, schema_types)

    def test_biomaterial_view_table_contains_all_biomaterial_files(self):
        from dcpquery import config
        create_view_tables('mock_extractor')
        biomaterial_view_table_count = config.db_session.execute(
            """
            SELECT count(*) from biomaterial;
            """
        ).fetchall()[0][0]

        files_of_type_biomaterial_count = config.db_session.execute(
            """
            SELECT count(*) from files where dcp_schema_type_name='biomaterial';
            """
        ).fetchall()[0][0]
        self.assertEqual(biomaterial_view_table_count, files_of_type_biomaterial_count)

    @unittest.skip("WIP")
    def test_prepare_database(self):
        with self.db.transaction() as (_, tables):
            result = set(tables.files.select_views())
            implied_views = set(f.schema_type_plural for f in vx_bundle.files if f.normalizable)
            self.assertEqual(result & implied_views, implied_views)

    @unittest.skip("WIP")
    def test_insert_into_database(self):
        self.loader.load(vx_bundle, dict(a='b'))

        with self.db.transaction() as (cursor, tables):
            # bundle insertion
            result = tables.bundles.select(vx_bundle.uuid, vx_bundle.version)
            self.assertIsNotNone(result)

            # join table
            result = tables.bundles_files.select_bundle(vx_bundle.uuid, vx_bundle.version)
            self.assertTrue(len(result) > 0)

            # files and view tables
            for file in vx_bundle.files:
                result = tables.files.select(file.uuid, file.version)
                self.assertIsNotNone(result)

    def test_get_child_process_uuids_returns_correct_ids(self):
        child_processes = get_child_process_uuids(['b0000004-aaaa-aaaa-aaaa-aaaaaaaaaaaa'])
        expected_result = ['a0000001-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'a0000002-aaaa-aaaa-aaaa-aaaaaaaaaaaa']
        self.assertCountEqual(expected_result, child_processes)

    def test_get_parent_process_uuids_returns_correct_ids(self):
        parent_processes = get_parent_process_uuids(['b0000001-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
                                                     'b0000009-aaaa-aaaa-aaaa-aaaaaaaaaaaa'])
        expected_result = ['a0000003-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'a0000002-aaaa-aaaa-aaaa-aaaaaaaaaaaa']
        self.assertCountEqual(expected_result, parent_processes)

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

    @patch('dcpquery.etl.ProcessProcessLink', )
    def test_link_parent_and_child_processes_called_correct_number_of_times(self, mock_process_process_link):
        link = {
            "process": "a0000006-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
            "inputs": [
                "b0000011-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                "b0000012-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
            ],
            "input_type": "biomaterial",
            "outputs": [
                "b0000014-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                "b0000015-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
            ],
            "output_type": "file",
            "protocols": [
                {
                    "protocol_type": "library_preparation_protocol",
                    "protocol_id": "c0000010-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
                },
                {
                    "protocol_type": "sequencing_protocol",
                    "protocol_id": "c0000011-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
                }
            ]
        }
        load_links([link])

        mock_process = {'process_uuid': 'a0000005-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
                        'input_file_uuids': ["b0000006-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                                             "b0000007-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                                             'b0000008-aaaa-aaaa-aaaa-aaaaaaaaaaaa'],
                        'output_file_uuids': ["b0000011-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                                              "b0000012-aaaa-aaaa-aaaa-aaaaaaaaaaaa"],
                        'protocol_uuids': ['c0000013-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
                                           'c0000011-aaaa-aaaa-aaaa-aaaaaaaaaaaa'],
                        'parents': ['a0000001-aaaa-aaaa-aaaa-aaaaaaaaaaaa'],
                        'children': ['a0000006-aaaa-aaaa-aaaa-aaaaaaaaaaaa']}

        with patch('dcpquery.config.db_session.add_all'):
            link_parent_and_child_processes(mock_process)
        assert mock_process_process_link.call_count == 2


if __name__ == '__main__':
    unittest.main()
