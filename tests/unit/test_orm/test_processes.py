import unittest

from dcpquery import config
from dcpquery.db.models import Process
from dcpquery.etl import load_links, update_process_join_table
from tests import mock_links


class TestProcesses(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        load_links(mock_links['links'], 'mock_bundle_uuid')
        config.db_session.commit()
        update_process_join_table()

    def test_get_all_parents(self):
        parent_processes = Process.list_all_parent_processes('a0000000-aaaa-aaaa-aaaa-aaaaaaaaaaaa')
        expected_parents = ['a0000003-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'a0000004-aaaa-aaaa-aaaa-aaaaaaaaaaaa']
        self.assertCountEqual(expected_parents, parent_processes)

    def test_get_all_children(self):
        child_processes = Process.list_all_child_processes('a0000003-aaaa-aaaa-aaaa-aaaaaaaaaaaa')
        expected_children = ['a0000000-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'a0000001-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
                             'a0000002-aaaa-aaaa-aaaa-aaaaaaaaaaaa']
        self.assertCountEqual(expected_children, child_processes)


if __name__ == '__main__':
    unittest.main()
