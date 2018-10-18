import os
import sys
import unittest
from collections import Counter, defaultdict

pkg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))  # noqa
sys.path.insert(0, pkg_root)  # noqa

from psycopg2 import sql
from test import *
from lib.database import PostgresDatabase, Transaction
from lib.load import PostgresLoader


class TestPostgresLoader(unittest.TestCase):

    _test_identifier = gen_random_chars(6)
    db = PostgresDatabase(CONFIG.test_database_uri)
    loader = PostgresLoader(db)

    bundles_table = 'bundles'
    implied_join_tables = [
        'bundles_metadata_files',
    ]
    implied_json_tables = [
        'sequence_files',
        'dissociation_protocols',
        'donor_organisms',
        'cell_suspensions',
        'processes',
        'specimen_from_organisms',
    ]

    def setUp(self):
        assert(self.db._connection_uri == CONFIG.test_database_uri and CONFIG.test_database_uri.endswith('/test'))
        with self.db.transaction() as transaction:
            self._clear_tables(transaction)
            self.loader._existing_table_names.clear()
            self.loader._prepare_database(transaction, vx_bundle)

    def test_prepare_database(self):
        with self.db.transaction() as transaction:
            result = set(transaction.list_tables())
            expected = set([self.bundles_table] + self.implied_join_tables)
            self.assertEqual(result & expected, expected)

    def test_insert_into_database(self):
        # collect expected results
        file_counts_by_schema_module = Counter()
        file_uuids_by_schema_module = defaultdict(set)
        for f in vx_bundle.normalizable_files:
            file_counts_by_schema_module[f.schema_module_plural] += 1
            file_uuids_by_schema_module[f.schema_module_plural].add(str(f.uuid))

        self.loader.load(vx_bundle)

        with self.db.transaction() as transaction:
            # bundle insertion
            result = transaction.select('bundles', vx_bundle.uuid)
            self.assertEqual(result['uuid'], str(vx_bundle.uuid))
            self.assertEqual(result['json']['uuid'], str(vx_bundle.uuid))
            # json and join tables
            for table_name in self.implied_json_tables:
                transaction._cursor.execute(
                    sql.SQL(
                        """
                        SELECT bf.* FROM bundles_metadata_files AS bf
                        JOIN {} AS json_table on bf.file_uuid = json_table.uuid
                        WHERE bf.bundle_uuid = %s
                        """.format(table_name)
                    ),
                    (str(vx_bundle.uuid),)
                )
                result = transaction._cursor.fetchall()
                bundle_uuid = set([t[0] for t in result])
                table_uuids = set([t[1] for t in result])
                self.assertEqual(bundle_uuid, {str(vx_bundle.uuid)})
                self.assertEqual(table_uuids, file_uuids_by_schema_module[table_name])
                self.assertEqual(len(result), file_counts_by_schema_module[table_name])

    @staticmethod
    def _clear_tables(transaction: Transaction):
        transaction._cursor.execute(
            """
            CREATE OR REPLACE FUNCTION drop_tables(username IN VARCHAR) RETURNS void AS $$
            DECLARE
                statements CURSOR FOR
                    SELECT tablename FROM pg_tables
                    WHERE
                        tableowner = username AND
                        schemaname = 'public';
            BEGIN
                FOR stmt IN statements LOOP
                    EXECUTE 'DROP TABLE ' || quote_ident(stmt.tablename) || ' CASCADE;';
                END LOOP;
            END;
            $$ LANGUAGE plpgsql;
            """
        )
        transaction._cursor.execute(
            """
            SELECT drop_tables('master');
            """
        )


if __name__ == '__main__':
    unittest.main()
