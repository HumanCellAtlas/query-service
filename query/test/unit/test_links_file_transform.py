import unittest
from mock import patch

from query.lib.config import Config
from query.lib.db.database import Tables, PostgresDatabase
from query.lib.etl.links_file_transform import LinksFileTransform
from test import mock_links, truncate_tables


class TestLinksTransform(unittest.TestCase):
    db = PostgresDatabase(Config.test_database_uri)

    def setUp(self):
        with self.db.transaction() as (cursor, tables):
            truncate_tables(cursor)
            LinksFileTransform().links_file_transformer(tables, mock_links['links'])

    @patch.object(LinksFileTransform, 'format_process_info')
    @patch.object(LinksFileTransform, 'get_child_process_uuids')
    @patch.object(LinksFileTransform, 'get_parent_process_uuids')
    @patch.object(LinksFileTransform, 'create_processes')
    @patch.object(LinksFileTransform, 'link_parent_and_child_processes')
    @patch.object(Tables, 'process_links')
    def test_lft_functions_called_once_per_link_object_links(self, mock_tables, mock_link_parent_child,
                                                             mock_create_processes, mock_get_parent_uuids,
                                                             mock_get_child_uuids, mock_format):
        LinksFileTransform().links_file_transformer(mock_tables, mock_links['links'])
        assert mock_format.call_count == 6
        assert mock_get_child_uuids.call_count == 6
        assert mock_get_parent_uuids.call_count == 6
        assert mock_create_processes.call_count == 6
        assert mock_link_parent_child.call_count == 6

    def test_format_process_info_correctly_formats_link_object(self):
        mock_process = {'process_uuid': 'process_0', 'input_file_uuids': ['file_1', 'file_2', 'file_3'],
                        'output_file_uuids': ['file_4', 'file_5'], 'protocol_uuids': ['protocol_0', 'protocol_1']}
        process = LinksFileTransform().format_process_info(mock_links['links'][0])
        assert process == mock_process

    def test_get_child_process_uuids_returns_correct_ids(self):
        with self.db.transaction() as (cursor, tables):
            child_processes = LinksFileTransform().get_child_process_uuids(tables, ['file_4'])
        expected_result = ['process_1', 'process_2']
        self.assertCountEqual(expected_result, child_processes)

    def test_get_parent_process_uuids_returns_correct_ids(self):
        with self.db.transaction() as (cursor, tables):
            parent_processes = LinksFileTransform().get_parent_process_uuids(tables, ['file_1', 'file_9'])
        expected_result = ['process_3', 'process_2']
        self.assertCountEqual(expected_result, parent_processes)

    @patch.object(Tables, 'process_links')
    def test_create_processes_calls_insert_correct_number_times(self, mock_tables):
        mock_process = {'process_uuid': 'process_6', 'input_file_uuids': ['file_11', 'file_12', 'file_13'],
                        'output_file_uuids': ['file_14', 'file_15'], 'protocol_uuids': ['protocol_10', 'protocol_11']}
        LinksFileTransform.create_processes(mock_tables, mock_process)
        assert mock_tables.process_links.insert.call_count == 7

    @patch.object(Tables, 'process_links')
    def test_link_parent_and_child_processes_called_correct_number_of_times(self, mock_tables):
        link = {
            "process": "process_6",
            "inputs": [
                "file_11",
                "file_12",
            ],
            "input_type": "biomaterial",
            "outputs": [
                "file_14",
                "file_15"
            ],
            "output_type": "file",
            "protocols": [
                {
                    "protocol_type": "library_preparation_protocol",
                    "protocol_id": "protocol_10"
                },
                {
                    "protocol_type": "sequencing_protocol",
                    "protocol_id": "protocol_11"
                }
            ]
        }
        with self.db.transaction() as (cursor, tables):
            LinksFileTransform().links_file_transformer(tables, [link])

        mock_process = {'process_uuid': 'process_5', 'input_file_uuids': ['file_6', 'file_7', 'file_8'],
                        'output_file_uuids': ['file_11', 'file_12'], 'protocol_uuids': ['protocol_13', 'protocol_11'],
                        'parents': ['process_1'], 'children': ['process_6']}
        LinksFileTransform.link_parent_and_child_processes(mock_tables, mock_process)
        assert mock_tables.process_links.insert_parent_child_link.call_count == 2

    def test_get_all_parents(self):
        with self.db.transaction() as (cursor, tables):
            parent_processes = tables.process_links.list_all_parents('process_0')

        expected_parents = ['process_3', 'process_4']
        self.assertCountEqual(expected_parents, parent_processes)

    def test_get_all_children(self):
        with self.db.transaction() as (cursor, tables):
            child_processes = tables.process_links.list_all_children('process_3')
        expected_children = ['process_0', 'process_1', 'process_2']
        self.assertCountEqual(expected_children, child_processes)
