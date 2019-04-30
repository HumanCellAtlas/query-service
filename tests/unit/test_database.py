import sqlalchemy
import unittest, secrets
from uuid import uuid4

# from lib.etl.load import PostgresLoader
from dcpquery.db import Process, File, DCPQueryDBManager, Bundle, ProcessFileLink, BundleFileLink
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


# Note: these tests alters global state and so may not play well with other concurrent tests/operations
class TestDBRules(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.uuid = "a309af02-0888-4184-bcf2-5971dec9e8ab"
        cls.version = "2018-09-06T190237.485774Z"
        config.db_session.add(File(uuid=cls.uuid, version=cls.version))
        config.db_session.add(Bundle(uuid=cls.uuid, version=cls.version))
        config.db_session.add(Process(process_uuid=cls.uuid))
        config.db_session.add(ProcessFileLink(
            process_uuid=cls.uuid, file_uuid=cls.uuid, process_file_connection_type="INPUT_ENTITY")
        )
        config.db_session.add(
            BundleFileLink(bundle_fqid=cls.uuid + "." + cls.version, file_fqid=cls.uuid + "." + cls.version, name='boo')
        )
        config.db_session.commit()

        # remove rules
        config.db_session.execute("DROP RULE file_table_ignore_duplicate_inserts ON files;")
        config.db_session.execute("DROP RULE bundle_table_ignore_duplicate_inserts ON bundles;")
        config.db_session.execute("DROP RULE process_table_ignore_duplicate_inserts ON processes;")
        config.db_session.execute(
            "DROP RULE process_file_join_table_ignore_duplicate_inserts ON process_file_join_table;"
        )
        config.db_session.execute("DROP RULE bundle_file_join_table_ignore_duplicate_inserts ON bundle_file_links;")
        config.db_session.commit()

    #
    @classmethod
    def tearDownClass(cls):
        config.db_session.rollback()
        DCPQueryDBManager().create_upsert_rules_in_db()

    def test_file_table_rule(self):
        # Test db throws an error without rule
        with self.assertRaises(sqlalchemy.exc.IntegrityError):
            config.db_session.add(File(uuid=self.uuid, version=self.version))
            config.db_session.commit()
        config.db_session.rollback()

        # add rule
        config.db_session.execute(DCPQueryDBManager.file_ignore_duplicate_rule_sql)
        config.db_session.commit()

        # try to add duplicate file, check no error thrown
        config.db_session.add(File(uuid=self.uuid, version=self.version))
        config.db_session.commit()

    def test_bundle_table_rule(self):
        with self.assertRaises(sqlalchemy.exc.IntegrityError):
            config.db_session.add(Bundle(uuid=self.uuid, version=self.version))
            config.db_session.commit()
        config.db_session.rollback()

        # add rule
        config.db_session.execute(DCPQueryDBManager.bundle_ignore_duplicate_rule_sql)
        config.db_session.commit()

        # try to add duplicate file, check no error thrown
        config.db_session.add(Bundle(uuid=self.uuid, version=self.version))
        config.db_session.commit()

    def test_process_table_rule(self):
        with self.assertRaises(sqlalchemy.exc.IntegrityError):
            config.db_session.add(Process(process_uuid=self.uuid))
            config.db_session.commit()
        config.db_session.rollback()

        # add rule
        config.db_session.execute(DCPQueryDBManager.process_ignore_duplicate_rule_sql)
        config.db_session.commit()

        # try to add duplicate file, check no error thrown
        config.db_session.add(Process(process_uuid=self.uuid))
        config.db_session.commit()

    def test_process_file_link_table_rule(self):
        with self.assertRaises(sqlalchemy.exc.IntegrityError):
            config.db_session.add(ProcessFileLink(
                process_uuid=self.uuid, file_uuid=self.uuid, process_file_connection_type="INPUT_ENTITY")
            )
            config.db_session.commit()
        config.db_session.rollback()

        # add rule
        config.db_session.execute(DCPQueryDBManager.process_file_link_ignore_duplicate_rule_sql)
        config.db_session.commit()

        # try to add duplicate file, check no error thrown
        config.db_session.add(ProcessFileLink(
            process_uuid=self.uuid, file_uuid=self.uuid, process_file_connection_type="INPUT_ENTITY")
        )
        config.db_session.commit()

    def test_bundle_file_link_table_rule(self):
        with self.assertRaises(sqlalchemy.exc.IntegrityError):
            config.db_session.add(
                BundleFileLink(
                    bundle_fqid=self.uuid + "." + self.version,
                    file_fqid=self.uuid + "." + self.version,
                    name='boo'
                )
            )
            config.db_session.commit()
        config.db_session.rollback()

        # add rule
        config.db_session.execute(DCPQueryDBManager.bundle_file_link_ignore_duplicate_rule_sql)
        config.db_session.commit()

        # try to add duplicate file, check no error thrown
        config.db_session.add(
            BundleFileLink(
                bundle_fqid=self.uuid + "." + self.version,
                file_fqid=self.uuid + "." + self.version, name='boo'
            )
        )
        config.db_session.commit()


if __name__ == '__main__':
    unittest.main()
