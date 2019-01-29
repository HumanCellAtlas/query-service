import os
import sys
import unittest
from uuid import uuid4

from test import vx_bundle, clear_views, truncate_tables, eventually, gen_random_chars

pkg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))  # noqa
sys.path.insert(0, pkg_root)  # noqa

from lib.config import Config
from lib.db.database import PostgresDatabase, Tables


class TestReadOnlyTransactions(unittest.TestCase):
    db = PostgresDatabase(Config.test_database_uri)

    def test_read_only_returns_column_names(self):
        project_file = next(f for f in vx_bundle.files if f.metadata.name == 'project_0.json')
        with self.db.transaction() as (cursor, tables):
            # insert files
            result = tables.files.insert(project_file)
            self.assertEqual(result, 1)

        query_results, column_names = self.db.run_read_only_query("SELECT * FROM FILES;")

        self.assertEqual(column_names, ['file_uuid', 'file_version', 'fqid', 'name', 'schema_type_id', 'json'])


class TestPostgresLoader(unittest.TestCase):

    db = PostgresDatabase(Config.test_database_uri)

    def setUp(self):
        with self.db._connection.cursor() as cursor:
            clear_views(cursor)
            truncate_tables(cursor)

    def test_insert_select(self):
        project_file = next(f for f in vx_bundle.files if f.metadata.name == 'project_0.json')
        process_file = next(f for f in vx_bundle.files if f.metadata.name == 'process_0.json')
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
            result = tables.bundles.insert(vx_bundle, dict(a='b'))
            self.assertEqual(result, 1)
            # select bundle
            result = tables.bundles.select(vx_bundle.uuid, vx_bundle.version)
            file_fqids = result.pop('file_fqids')
            self.assertDictEqual(
                result,
                dict(
                    uuid=str(vx_bundle.uuid),
                    version=vx_bundle.version,
                    json=dict(a='b')
                )
            )
            self.assertEqual(len(vx_bundle.files), len(file_fqids))
            self.assertSetEqual(set(f.fqid for f in vx_bundle.files), set(file_fqids))

            # insert bundles_files
            result = tables.files.insert(process_file)
            self.assertEqual(result, 1)
            result = tables.bundles_files.insert(
                vx_bundle.uuid, vx_bundle.version, project_file.uuid, project_file.version)
            self.assertEqual(result, 1)
            result = tables.bundles_files.insert(
                vx_bundle.uuid, vx_bundle.version, process_file.uuid, process_file.version)
            self.assertEqual(result, 1)
            # select bundles_files
            result = tables.bundles_files.select_bundle(vx_bundle.uuid, vx_bundle.version)
            result = sorted(result, key=lambda x: x['file_uuid'])
            self.assertEqual(len(result), 2)
            self.assertDictEqual(
                result[0],
                dict(
                    bundle_uuid=str(vx_bundle.uuid),
                    bundle_version=vx_bundle.version,
                    file_uuid=str(process_file.uuid),
                    file_version=process_file.version
                )
            )
            self.assertDictEqual(
                result[1],
                dict(
                    bundle_uuid=str(vx_bundle.uuid),
                    bundle_version=vx_bundle.version,
                    file_uuid=str(project_file.uuid),
                    file_version=project_file.version
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
                    tables.files.create_view(table_name, schema_type=gen_random_chars(4))
                # list
                test_list(tables, num_test_tables)
        finally:
            with self.db.transaction() as (cursor, _):
                clear_views(cursor)
            self.db._connection.commit()
            with self.db.transaction() as (_, tables):
                test_list(tables, 0)

    def test_job_status_creation(self):
        uuid = uuid4()
        with self.db.transaction() as (cursor, tables):
            row_count = tables.job_status.insert(uuid)
            assert row_count == 1
            job = tables.job_status.select(uuid)
            assert job['status'] == 'CREATED'
            job = tables.job_status.select_from_write_db(uuid)
            assert job['status'] == 'CREATED'

    def test_job_status_status_update(self):
        uuid = uuid4()
        with self.db.transaction() as (cursor, tables):
            row_count = tables.job_status.insert(uuid)
            assert row_count == 1
            tables.job_status.update_job_status(uuid, 'COMPLETE')
            job = tables.job_status.select(uuid)
            assert job['status'] == 'COMPLETE'


if __name__ == '__main__':
    unittest.main()
