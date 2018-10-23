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
        with self.db.transaction() as transaction:
            self.loader._prepare_database(transaction, vx_bundle)

    def test_prepare_database(self):
        with self.db.transaction() as transaction:
            result = set(transaction.metadata_files.select_views())
            self.assertEqual(result & self.implied_views, self.implied_views)

    def test_insert_into_database(self):
        # collect expected results
        file_counts_by_schema_module = Counter()
        file_uuids_by_schema_module = defaultdict(set)
        for f in vx_bundle.normalizable_files:
            file_counts_by_schema_module[f.schema_module_plural] += 1
            file_uuids_by_schema_module[f.schema_module_plural].add(str(f.fqid))

        self.loader.load(vx_bundle)

        with self.db.transaction() as transaction:
            # bundle insertion
            result = transaction.bundles.select(vx_bundle.uuid, vx_bundle.version)
            self.assertEqual(result['uuid'], str(vx_bundle.uuid))
            self.assertEqual(result['json']['uuid'], str(vx_bundle.uuid))
            # json and join tables
            for view_name in self.implied_views:
                transaction.bundles_metadata_files._cursor.execute(
                    sql.SQL(
                        """
                        SELECT bf.bundle_uuid, bf.bundle_version, bf.file_uuid, bf.file_version
                        FROM bundles_metadata_files AS bf
                        JOIN {} AS json_table
                        ON bf.file_uuid = json_table.uuid AND bf.file_version = json_table.version
                        WHERE bf.bundle_uuid = %s AND bf.bundle_version = %s
                        """.format(view_name)
                    ),
                    (str(vx_bundle.uuid), vx_bundle.version)
                )
                result = transaction.bundles_metadata_files._cursor.fetchall()
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
