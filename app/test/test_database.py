import os
import sys
import unittest
from uuid import uuid4

pkg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))  # noqa
sys.path.insert(0, pkg_root)  # noqa

from test import *
from lib.config import Config
from lib.db.database import PostgresDatabase, Transaction


class TestPostgresLoader(unittest.TestCase):

    db = PostgresDatabase(Config.test_database_uri)

    def setUp(self):
        with self.db._connection.cursor() as cursor:
            clear_views(cursor)
            truncate_tables(cursor)

    def test_bundle_insert_select(self):
        uuid = uuid4()
        version = '2018-10-18T121314.123456Z'
        example_json = dict(a='b')
        with self.db.transaction() as transaction:
            # insert
            result = transaction.bundles.insert(uuid, version, example_json)
            self.assertEqual(result, 1)
            # select
            result = transaction.bundles.select(uuid, version)
            self.assertDictEqual(result['json'], example_json)

    def test_metadata_file_insert_select(self):
        uuid = uuid4()
        version = '2018-10-18T121314.123456Z'
        module = 'donor_organism'
        example_json = dict(a='b')
        with self.db.transaction() as transaction:
            # insert
            result = transaction.metadata_files.insert(module, uuid, version, example_json)
            self.assertEqual(result, 1)
            # select
            result = transaction.metadata_files.select(module, uuid, version)
            self.assertDictEqual(result['json'], example_json)

    def test_table_create_list(self):
        num_test_tables = 3
        test_table_names = [
            f"test_table_{gen_random_chars(6)}" for _ in range(num_test_tables)
        ]

        @eventually(5.0, 1.0)
        def test_list(transaction: Transaction, num_intersecting_tables: int):
            ls_result = set(transaction.metadata_files.select_views())
            inner_result = ls_result & set(test_table_names)
            self.assertEqual(len(inner_result), num_intersecting_tables)

        try:
            with self.db.transaction() as transaction:
                # create
                for table_name in test_table_names:
                    transaction.metadata_files.create_view(table_name, module=gen_random_chars(4))
                # list
                test_list(transaction, num_test_tables)
        finally:
            with self.db._connection.cursor() as cursor:
                clear_views(cursor)
            self.db._connection.commit()
            with self.db.transaction() as transaction:
                test_list(transaction, 0)


if __name__ == '__main__':
    unittest.main()
