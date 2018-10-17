import os
import sys
import unittest
from uuid import uuid4

pkg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))  # noqa
sys.path.insert(0, pkg_root)  # noqa

from test import *
from lib.database import PostgresDatabase
from psycopg2 import sql


class TestPostgresLoader(unittest.TestCase):

    db = PostgresDatabase(CONFIG.test_database_uri)

    @classmethod
    def setUpClass(cls):
        with cls.db.transaction() as transaction:
            transaction.create_json_table('bundles')

    def test_insert_select_delete(self):
        uuid = uuid4()
        example_json = dict(a='b')
        try:
            with self.db.transaction() as transaction:
                # insert
                result = transaction.insert('bundles', uuid, example_json)
                self.assertEqual(result, 1)
                # select
                result = transaction.select('bundles', uuid)
                self.assertDictEqual(result['json'], example_json)
        finally:
            with self.db.transaction() as transaction:
                # delete
                result = transaction.delete('bundles', uuid)
                self.assertEqual(result, 1)
                result = transaction.select('bundles', uuid)
                self.assertIsNone(result)

    def test_table_create_list_delete(self):
        num_test_tables = 3
        test_table_names = [
            f"test_table_{gen_random_chars(6)}" for _ in range(num_test_tables)
        ]

        @eventually(5.0, 1.0)
        def test_list(transaction, num_intersecting_tables: int):
            ls_result = set(transaction.list_tables())
            inner_result = ls_result & set(test_table_names)
            self.assertEqual(len(inner_result), num_intersecting_tables)

        try:
            with self.db.transaction() as transaction:
                # create
                for table_name in test_table_names:
                    transaction.create_json_table(table_name)
                # list
                test_list(transaction, num_test_tables)
        finally:
            with self.db._connection.cursor() as cursor:
                for table_name in test_table_names:
                    cursor.execute(sql.SQL("DROP TABLE {}".format(table_name)))
            self.db._connection.commit()
            with self.db.transaction() as transaction:
                test_list(transaction, 0)


if __name__ == '__main__':
    unittest.main()
