import unittest

from test import vx_bundle, clear_views, truncate_tables, gen_random_chars, mock_links

from query.lib.config import Config
from query.lib.db.database import PostgresDatabase, Tables
from query.lib.etl.load import PostgresLoader
from mock import patch


class TestPostgresLoader(unittest.TestCase):
    _test_identifier = gen_random_chars(6)
    db = PostgresDatabase(Config.test_database_uri)
    loader = PostgresLoader(db)

    def setUp(self):
        assert (self.db._connection_uri == Config.test_database_uri and Config.test_database_uri.endswith('/test'))
        with self.db._connection.cursor() as cursor:
            self._clear_tables(cursor)
            self.loader._existing_view_names.clear()
        with self.db.transaction() as (_, tables):
            self.loader._prepare_database(tables, vx_bundle)
            self.loader.load_links(tables, mock_links['links'])

    def test_prepare_database(self):
        with self.db.transaction() as (_, tables):
            result = set(tables.files.select_views())
            implied_views = set(f.schema_type_plural for f in vx_bundle.files if f.normalizable)
            self.assertEqual(result & implied_views, implied_views)

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
        with self.db.transaction() as (cursor, tables):
            child_processes = self.loader.get_child_process_uuids(tables, ['b0000004-aaaa-aaaa-aaaa-aaaaaaaaaaaa'])
        expected_result = ['a0000001-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'a0000002-aaaa-aaaa-aaaa-aaaaaaaaaaaa']
        self.assertCountEqual(expected_result, child_processes)

    def test_get_parent_process_uuids_returns_correct_ids(self):
        with self.db.transaction() as (cursor, tables):
            parent_processes = self.loader.get_parent_process_uuids(tables, ['b0000001-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
                                                                             'b0000009-aaaa-aaaa-aaaa-aaaaaaaaaaaa'])
        expected_result = ['a0000003-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'a0000002-aaaa-aaaa-aaaa-aaaaaaaaaaaa']
        self.assertCountEqual(expected_result, parent_processes)

    @patch.object(Tables, 'process_links')
    def test_create_processes_calls_insert_correct_number_times(self, mock_tables):
        mock_process = {'process_uuid': 'a0000006-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
                        'input_file_uuids': ["b0000011-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                                             "b0000012-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                                             'b0000013-aaaa-aaaa-aaaa-aaaaaaaaaaaa'],
                        'output_file_uuids': ["b0000014-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                                              "b0000015-aaaa-aaaa-aaaa-aaaaaaaaaaaa"],
                        'protocol_uuids': ['c0000010-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
                                           'c0000011-aaaa-aaaa-aaaa-aaaaaaaaaaaa']}
        self.loader.create_processes(mock_tables, mock_process)
        assert mock_tables.process_links.insert.call_count == 7

    @patch.object(Tables, 'process_links')
    def test_link_parent_and_child_processes_called_correct_number_of_times(self, mock_tables):
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
        with self.db.transaction() as (cursor, tables):
            self.loader.load_links(tables, [link])

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
        self.loader.link_parent_and_child_processes(mock_tables, mock_process)
        assert mock_tables.process_links.insert_parent_child_link.call_count == 2

    @staticmethod
    def _clear_tables(cursor):
        clear_views(cursor)
        truncate_tables(cursor)


if __name__ == '__main__':
    unittest.main()
