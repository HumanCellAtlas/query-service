import os
import sys
import unittest

pkg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))  # noqa
sys.path.insert(0, pkg_root)  # noqa

from test import *
from lib.config import Config
from lib.db.database import PostgresDatabase
from lib.etl.load import PostgresLoader


class TestPostgresLoader(unittest.TestCase):

    _test_identifier = gen_random_chars(6)
    db = PostgresDatabase(Config.test_database_uri)
    loader = PostgresLoader(db)

    def setUp(self):
        assert(self.db._connection_uri == Config.test_database_uri and Config.test_database_uri.endswith('/test'))
        with self.db._connection.cursor() as cursor:
            self._clear_tables(cursor)
            self.loader._existing_view_names.clear()
        with self.db.transaction() as (_, tables):
            self.loader._prepare_database(tables, vx_bundle)

    def test_prepare_database(self):
        with self.db.transaction() as (_, tables):
            result = set(tables.files.select_views())
            implied_views = set(f.schema_type_plural for f in vx_bundle.files if f.normalizable)
            self.assertEqual(result & implied_views, implied_views)

    def test_insert_into_database(self):
        self.loader.load(vx_bundle)

        with self.db.transaction() as (cursor, tables):
            # bundle insertion
            result = tables.bundles.select(vx_bundle.uuid, vx_bundle.version)
            self.assertIsNotNone(result)

            # join table
            result = tables.bundles_files.select(vx_bundle.uuid, vx_bundle.version)
            self.assertTrue(len(result) > 0)

            # files and view tables
            for file in vx_bundle.files:
                result = tables.files.select(file.uuid, file.version)
                self.assertIsNotNone(result)

    @staticmethod
    def _clear_tables(cursor):
        clear_views(cursor)
        truncate_tables(cursor)


if __name__ == '__main__':
    unittest.main()
