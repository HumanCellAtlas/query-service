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
        project_file = next(f for f in vx_bundle.files if f.metadata.name == 'project_0.json')
        with self.db.transaction() as (cursor, tables):
            # insert files
            result = tables.files.insert(project_file)
            self.assertEqual(result, 1)
            # select files
            result = tables.files.select(project_file.uuid, project_file.version)
            self.assertDictEqual(
                result,
                dict(
                    uuid=str(project_file.uuid),
                    version=project_file.version,
                    fqid=f"{project_file.uuid}.{project_file.version}",
                    name="project_0.json",
                    json=project_file
                )
            )

            # insert bundle
            result = tables.bundles.insert(vx_bundle)
            self.assertEqual(result, 1)
            # select bundle
            result = tables.bundles.select(vx_bundle.uuid, vx_bundle.version)
            file_fqids = result.pop('file_fqids')
            self.assertDictEqual(
                result,
                dict(
                    uuid=str(vx_bundle.uuid),
                    version=vx_bundle.version
                )
            )
            self.assertEqual(len(vx_bundle.files), len(file_fqids))
            self.assertSetEqual(set(f.fqid for f in vx_bundle.files), set(file_fqids))

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
