import os
import sys
import unittest
from uuid import uuid4

pkg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))  # noqa
sys.path.insert(0, pkg_root)  # noqa

from test import *
from lib.config import Config
from lib.database import PostgresDatabase


class TestPostgresLoader(unittest.TestCase):

    db = PostgresDatabase(Config.test_database_uri)

    @classmethod
    def setUpClass(cls):
        with cls.db.transaction() as transaction:
            clear_views(transaction._cursor)

    def test_bundle_insert_select_delete(self):
        uuid = uuid4()
        version = '2018-10-18T121314.123456Z'
        example_json = dict(a='b')
        try:
            with self.db.transaction() as transaction:
                # insert
                result = transaction.insert_bundle(uuid, version, example_json)
                self.assertEqual(result, 1)
                # select
                result = transaction.select_bundle(uuid, version)
                self.assertDictEqual(result['json'], example_json)
        finally:
            with self.db.transaction() as transaction:
                # delete
                result = transaction.delete_bundle(uuid, version)
                self.assertEqual(result, 1)
                result = transaction.select_bundle(uuid, version)
                self.assertIsNone(result)

    def test_metadata_file_insert_select_delete(self):
        uuid = uuid4()
        version = '2018-10-18T121314.123456Z'
        file_type = 'donor_organism'
        example_json = dict(a='b')
        try:
            with self.db.transaction() as transaction:
                # insert
                result = transaction.insert_metadata_file(file_type, uuid, version, example_json)
                self.assertEqual(result, 1)
                # select
                result = transaction.select_metadata_file(file_type, uuid, version)
                self.assertDictEqual(result['json'], example_json)
        finally:
            with self.db.transaction() as transaction:
                # delete
                result = transaction.delete_metadata_file(file_type, uuid, version)
                self.assertEqual(result, 1)
                result = transaction.select_metadata_file(file_type, uuid, version)
                self.assertIsNone(result)

    def test_table_create_list_delete(self):
        num_test_tables = 3
        test_table_names = [
            f"test_table_{gen_random_chars(6)}" for _ in range(num_test_tables)
        ]

        @eventually(5.0, 1.0)
        def test_list(transaction, num_intersecting_tables: int):
            ls_result = set(transaction.list_views())
            inner_result = ls_result & set(test_table_names)
            self.assertEqual(len(inner_result), num_intersecting_tables)

        try:
            with self.db.transaction() as transaction:
                # create
                for table_name in test_table_names:
                    transaction.create_metadata_file_view(table_name, file_type=gen_random_chars(4))
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
