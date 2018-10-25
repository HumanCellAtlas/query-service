import os
import sys
import unittest
from dateutil.parser import parse as parse_datetime
from uuid import uuid4

pkg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))  # noqa
sys.path.insert(0, pkg_root)  # noqa

from test import *
from lib.config import Config
from lib.model import datetime_to_version
from lib.db.database import PostgresDatabase, Tables


class TestPostgresLoader(unittest.TestCase):

    db = PostgresDatabase(Config.test_database_uri)

    def setUp(self):
        with self.db._connection.cursor() as cursor:
            clear_views(cursor)
            truncate_tables(cursor)

    def test_insert_select(self):
        uuid = uuid4()
        version = '2018-10-18T121314.123456Z'

        file1_module = 'donor_organism'
        file1_uuid = uuid4()
        file1_version = '2018-10-24T121314.123456Z'

        file2_module = 'sequencing_protocol'
        file2_uuid = uuid4()
        file2_version = '2018-10-25T121314.123456Z'
        example_json1 = dict(a='b')
        example_json2 = dict(b='c')
        with self.db.transaction() as (cursor, tables):
            # insert files
            result = tables.files.insert(file1_module, file1_uuid, file1_version, example_json1)
            self.assertEqual(result, 1)
            result = tables.files.insert(file2_module, file2_uuid, file2_version, example_json2)
            self.assertEqual(result, 1)
            # select files
            result = tables.files.select(file1_module, file1_uuid, file1_version)
            self.assertDictEqual(result['json'], example_json1)
            result = tables.files.select(file2_module, file2_uuid, file2_version)
            self.assertDictEqual(result['json'], example_json2)

            # insert bundle
            result = tables.bundles.insert(uuid, version)
            self.assertEqual(result, 1)
            # select bundle
            result = tables.bundles.select(uuid, version)
            self.assertEqual(result['uuid'], str(uuid))
            self.assertEqual(result['version'], version)
            result = tables.bundles.select(file1_uuid, version)
            self.assertIsNone(result)

            # insert bundles_files
            result = tables.bundles_files.insert(uuid, version, file1_uuid, file1_version)
            self.assertEqual(result, 1)
            result = tables.bundles_files.insert(uuid, version, file2_uuid, file2_version)
            self.assertEqual(result, 1)
            # select bundles_files
            result = tables.bundles_files.select_bundle(uuid, version)
            result = sorted(result, key=lambda x: x['file_version'])
            self.assertEqual(len(result), 2)
            self.assertDictEqual(
                result[0],
                dict(
                    bundle_uuid=str(uuid),
                    bundle_version=version,
                    file_uuid=str(file1_uuid),
                    file_version=file1_version
                )
            )
            self.assertDictEqual(
                result[1],
                dict(
                    bundle_uuid=str(uuid),
                    bundle_version=version,
                    file_uuid=str(file2_uuid),
                    file_version=file2_version
                )
            )

    def test_table_create_list(self):
        num_test_tables = 3
        test_table_names = [
            f"test_table_{gen_random_chars(6)}" for _ in range(num_test_tables)
        ]

        @eventually(5.0, 1.0)
        def test_list(tables: Tables, num_intersecting_tables: int):
            ls_result = set(tables.files.select_views())
            inner_result = ls_result & set(test_table_names)
            self.assertEqual(len(inner_result), num_intersecting_tables)

        try:
            with self.db.transaction() as (cursor, tables):
                # create
                for table_name in test_table_names:
                    tables.files.create_view(table_name, module=gen_random_chars(4))
                # list
                test_list(tables, num_test_tables)
        finally:
            with self.db.transaction() as (cursor, _):
                clear_views(cursor)
            self.db._connection.commit()
            with self.db.transaction() as (_, tables):
                test_list(tables, 0)


if __name__ == '__main__':
    unittest.main()
