import unittest, secrets
from uuid import uuid4

# from lib.etl.load import PostgresLoader
from dcpquery.db import Process
from dcpquery.etl import load_links
from tests import vx_bundle, clear_views, truncate_tables, eventually, mock_links

from dcpquery import config


@unittest.skip("WIP")
class TestReadOnlyTransactions(unittest.TestCase):
    def test_read_only_returns_column_names(self):
        project_file = next(f for f in vx_bundle.files if f.metadata.name == 'project_0.json')
        with config.db.transaction() as (cursor, tables):
            # insert files
            result = tables.files.insert(project_file)
            self.assertEqual(result, 1)

        query_results, column_names = self.db.run_read_only_query("SELECT * FROM FILES;")

        self.assertEqual(column_names, ['file_uuid', 'file_version', 'fqid', 'name', 'schema_type_id', 'json'])


class TestPostgresLoader(unittest.TestCase):

    # db = PostgresDatabase(Config.test_database_uri)
    # loader = PostgresLoader(db)

    def setUp(self):
        truncate_tables()

    @unittest.skip("WIP")
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

            # insert process_links
            process_uuid = 'a0000000-aaaa-aaaa-aaaa-aaaaaaaaaaaa'
            file_uuid = 'b0000000-aaaa-aaaa-aaaa-aaaaaaaaaaaa'
            process_file_connection_type = 'INPUT_ENTITY'

            row_count = tables.process_links.insert(
                process_uuid, file_uuid, process_file_connection_type
            )
            assert row_count == 1
            # select process_links
            process = tables.process_links.select_by_process_uuid(process_uuid)

            assert process['uuid'] == process_uuid
            assert process['file_uuid'] == file_uuid
            assert process['process_file_connection_type'] == process_file_connection_type

            processes = tables.process_links.list_process_uuids_for_file_uuid(file_uuid)
            assert processes == [process_uuid]

            processes = tables.process_links.list_process_uuids_for_file_uuid(file_uuid, 'OUTPUT_ENTITY')
            assert processes == []

            # TODO @madison - refactor this into multiple tests
            # insert - process_links_join_table
            process1_uuid = 'a0000001-aaaa-aaaa-aaaa-aaaaaaaaaaaa'
            row_count = tables.process_links.insert_parent_child_link(process_uuid, process1_uuid)
            assert row_count == 1

            # select process_links_join_table_functions
            process2_uuid = 'a0000002-aaaa-aaaa-aaaa-aaaaaaaaaaaa'
            process3_uuid = 'a0000003-aaaa-aaaa-aaaa-aaaaaaaaaaaa'
            process4_uuid = 'a0000004-aaaa-aaaa-aaaa-aaaaaaaaaaaa'
            process5_uuid = 'a0000005-aaaa-aaaa-aaaa-aaaaaaaaaaaa'

            tables.process_links.insert_parent_child_link(process_uuid, process2_uuid)
            tables.process_links.insert_parent_child_link(process1_uuid, process3_uuid)
            tables.process_links.insert_parent_child_link(process1_uuid, process4_uuid)
            tables.process_links.insert_parent_child_link(process5_uuid, process4_uuid)

            children = tables.process_links.list_direct_children_process_uuids(process_uuid)
            assert children == [process1_uuid, process2_uuid]

            parents = tables.process_links.list_direct_parent_process_uuids(process4_uuid)
            assert parents == [process1_uuid, process5_uuid]

    @unittest.skip("WIP")
    def test_table_create_list(self):
        num_test_tables = 3
        test_table_names = [
            f"test_table_{secrets.token_hex(12)}" for _ in range(num_test_tables)
        ]

        # def test_list(tables: Tables, num_intersecting_tables: int):

        @eventually(5.0, 1.0)
        def test_list(tables, num_intersecting_tables: int):
            ls_result = set(tables.files.select_views())
            inner_result = ls_result & set(test_table_names)
            self.assertEqual(len(inner_result), num_intersecting_tables)

        try:
            with self.db.transaction() as (cursor, tables):
                # create
                for table_name in test_table_names:
                    tables.files.create_view(table_name, schema_type=secrets.token_hex(8))
                # list
                test_list(tables, num_test_tables)
        finally:
            with self.db.transaction() as (cursor, _):
                clear_views(cursor)
            self.db._connection.commit()
            with self.db.transaction() as (_, tables):
                test_list(tables, 0)

    def test_get_all_parents(self):
        load_links(mock_links['links'])

        parent_processes = Process.list_all_parent_processes('a0000000-aaaa-aaaa-aaaa-aaaaaaaaaaaa')
        expected_parents = ['a0000003-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'a0000004-aaaa-aaaa-aaaa-aaaaaaaaaaaa']
        self.assertCountEqual(expected_parents, parent_processes)

    def test_get_all_children(self):
        load_links(mock_links['links'])

        child_processes = Process.list_all_child_processes('a0000003-aaaa-aaaa-aaaa-aaaaaaaaaaaa')
        expected_children = ['a0000000-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'a0000001-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
                             'a0000002-aaaa-aaaa-aaaa-aaaaaaaaaaaa']
        self.assertCountEqual(expected_children, child_processes)


if __name__ == '__main__':
    unittest.main()
