import os
import sys
import unittest
from collections import Counter, defaultdict

pkg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))  # noqa
sys.path.insert(0, pkg_root)  # noqa

from test import *
from lib.config import Config
from lib.db.database import PostgresDatabase
from lib.model import datetime_to_version
from lib.etl.load import PostgresLoader


class TestPostgresLoader(unittest.TestCase):

    _test_identifier = gen_random_chars(6)
    db = PostgresDatabase(Config.test_database_uri)
    loader = PostgresLoader(db)

    implied_views = {
        'sequence_files',
        'dissociation_protocols',
        'donor_organisms',
        'cell_suspensions',
        'processes',
        'specimen_from_organisms',
    }

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
            self.assertEqual(result & self.implied_views, self.implied_views)

    def test_insert_into_database(self):
        # collect expected results
        file_counts_by_schema_module = Counter()
        file_uuids_by_schema_module = defaultdict(set)
        for f in vx_bundle.files:
            file_counts_by_schema_module[f.schema_module_plural] += 1
            file_uuids_by_schema_module[f.schema_module_plural].add(str(f.fqid))

        self.loader.load(vx_bundle)

        with self.db.transaction() as (cursor, tables):
            # bundle insertion
            result = tables.bundles.select(vx_bundle.uuid, vx_bundle.version)
            self.assertEqual(len(result), 15)
            self.assertSetEqual(set(r['uuid'] for r in result), {str(vx_bundle.uuid)})
            self.assertSetEqual(set(r['version'] for r in result), {str(vx_bundle.version)})
            self.assertSetEqual(
                set(f"{r['file_uuid']}.{r['file_version']}" for r in result),
                {
                    "d9a429f1-27e4-47bd-97de-b0c84516f36e.2018-09-06T190237.485774Z",
                    "a309af02-0888-4184-bcf2-5971dec9e8ab.2018-09-06T190237.485774Z",
                    "cbe65256-0c33-42ac-b58d-900b1231f272.2018-09-06T190237.485774Z",
                    "cf8cb45c-00cc-4ce9-8181-41f4a172898b.2018-09-06T190237.485774Z",
                    "3a644546-cf11-4d92-8485-e0e198722524.2018-09-06T190237.485774Z",
                    "d96015ad-0783-454a-a836-264391c60b02.2018-09-06T190237.485774Z",
                    "1e0fccf9-5cfa-450b-a08b-baf58b306276.2018-09-06T190237.485774Z",
                    "9f4531d6-5a7e-4d45-96e4-9e688534bbc7.2018-09-06T190237.485774Z",
                    "4acc13c8-2265-40c5-b1b8-67400aab379a.2018-09-06T190237.485774Z",
                    "4eba7001-6392-4392-a47a-3f09a4a9071f.2018-09-06T190237.485774Z",
                    "96923fa6-6ef9-46eb-8c64-3ff0c0cd73bd.2018-09-06T190237.485774Z",
                    "0ab85d4f-2706-4a56-9efd-e99d85abe21a.2018-09-06T190237.485774Z",
                    "45cb47f4-c804-48a8-9bfa-a090b1845b1c.2018-09-06T190237.485774Z",
                    "4b91e322-5891-4ce6-aa54-ae56f3093e33.2018-09-06T190237.485774Z",
                    "eb8376db-a875-4934-9c44-09e54efdc167.2018-09-06T190237.485774Z"
                }
            )
            # json and join tables
            for view_name in self.implied_views:
                cursor.execute(
                    sql.SQL(
                        """
                        SELECT b.uuid, b.version, b.file_uuid, b.file_version
                        FROM bundles AS b
                        JOIN {} AS json_table
                        ON b.file_uuid = json_table.uuid AND b.file_version = json_table.version
                        WHERE b.uuid = %s AND b.version = %s
                        """.format(view_name)
                    ),
                    (str(vx_bundle.uuid), vx_bundle.version)
                )
                result = cursor.fetchall()
                bundle_uuid = set([f"{t[0]}.{datetime_to_version(t[1])}" for t in result])
                table_uuids = set([f"{t[2]}.{datetime_to_version(t[3])}" for t in result])
                self.assertEqual(bundle_uuid, {str(vx_bundle.fqid)})
                self.assertEqual(table_uuids, file_uuids_by_schema_module[view_name])
                self.assertEqual(len(result), file_counts_by_schema_module[view_name])

    @staticmethod
    def _clear_tables(cursor):
        clear_views(cursor)
        truncate_tables(cursor)


if __name__ == '__main__':
    unittest.main()
