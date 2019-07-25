import os
import sys

import sqlalchemy
import unittest

from dcpquery import config
from dcpquery.db import File, Bundle, Process, ProcessFileLink, drop_db, init_db, BundleFileLink
from tests import vx_bf_links


class TestReadOnlyTransactions(unittest.TestCase):
    def test_read_only_returns_column_names(self):
        project_file = next(l.file for l in vx_bf_links if l.name == 'project_0.json')
        config.db_session.add(project_file)
        config.db_session.commit()

        row = next(config.db.execute("SELECT * FROM FILES;"))
        expected_column_names = ['fqid', 'uuid', 'version', 'dcp_schema_type_name', 'body', 'content_type', 'size',
                                 'extension']

        self.assertEqual(list(dict(row).keys()), expected_column_names)


# Note: these tests alter global state and so may not play well with other concurrent tests/operations
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
        config.db_session.execute("DROP RULE file_table_ignore_duplicate_inserts ON files_all_versions;")
        config.db_session.execute("DROP RULE bundle_table_ignore_duplicate_inserts ON bundles_all_versions;")
        config.db_session.execute("DROP RULE process_table_ignore_duplicate_inserts ON processes;")
        config.db_session.execute(
            "DROP RULE process_file_join_table_ignore_duplicate_inserts ON process_file_join_table;"
        )
        config.db_session.execute("DROP RULE bundle_file_join_table_ignore_duplicate_inserts ON bundle_file_links;")
        config.db_session.commit()

    @classmethod
    def tearDownClass(cls):
        config.db_session.rollback()
        TestDBManager().create_upsert_rules_in_db()

    def test_file_table_rule(self):
        # Test db throws an error without rule
        with self.assertRaises(sqlalchemy.exc.IntegrityError):
            config.db_session.add(File(uuid=self.uuid, version=self.version))
            config.db_session.commit()
        config.db_session.rollback()

        # add rule
        config.db_session.execute(TestDBManager.file_ignore_duplicate_rule_sql)
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
        config.db_session.execute(TestDBManager.bundle_ignore_duplicate_rule_sql)
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
        config.db_session.execute(TestDBManager.process_ignore_duplicate_rule_sql)
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
        config.db_session.execute(TestDBManager.process_file_link_ignore_duplicate_rule_sql)
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
        config.db_session.execute(TestDBManager.bundle_file_link_ignore_duplicate_rule_sql)
        config.db_session.commit()

        # try to add duplicate file, check no error thrown
        config.db_session.add(
            BundleFileLink(
                bundle_fqid=self.uuid + "." + self.version,
                file_fqid=self.uuid + "." + self.version, name='boo'
            )
        )
        config.db_session.commit()


class TestDatabaseUtils(unittest.TestCase):
    def test_db_cli(self):
        orig_argv = sys.argv
        sys.argv = ["prog", "--help"]
        try:
            import dcpquery.db.__main__
        except SystemExit as e:
            self.assertEqual(e.args[0], os.EX_OK)
        sys.argv = orig_argv

    def test_init_db(self):
        init_db(dry_run=True)
        init_db()  # dry_run is True by default

    def test_drop_db(self):
        drop_db(dry_run=True)
        drop_db()  # dry_run is True by default


class TestDBManager:
    process_file_link_ignore_duplicate_rule_sql = """
        CREATE OR REPLACE RULE process_file_join_table_ignore_duplicate_inserts AS
            ON INSERT TO process_file_join_table
                WHERE EXISTS (
                  SELECT 1
                FROM process_file_join_table
                WHERE process_uuid = NEW.process_uuid
                AND process_file_connection_type=NEW.process_file_connection_type
                AND file_uuid=NEW.file_uuid
            )
            DO INSTEAD NOTHING;
    """
    file_ignore_duplicate_rule_sql = """
        CREATE OR REPLACE RULE file_table_ignore_duplicate_inserts AS
            ON INSERT TO files_all_versions
                WHERE EXISTS (
                  SELECT 1
                FROM files_all_versions
                WHERE fqid = NEW.fqid
            )
            DO INSTEAD NOTHING;
    """
    bundle_ignore_duplicate_rule_sql = """
        CREATE OR REPLACE RULE bundle_table_ignore_duplicate_inserts AS
            ON INSERT TO bundles_all_versions
                WHERE EXISTS (
                  SELECT 1
                FROM bundles_all_versions
                WHERE fqid = NEW.fqid
            )
            DO INSTEAD NOTHING;
    """
    bundle_file_link_ignore_duplicate_rule_sql = """
        CREATE OR REPLACE RULE bundle_file_join_table_ignore_duplicate_inserts AS
            ON INSERT TO bundle_file_links
                WHERE EXISTS (
                  SELECT 1
                FROM bundle_file_links
                WHERE bundle_fqid = NEW.bundle_fqid
                AND file_fqid = NEW.file_fqid
            )
            DO INSTEAD NOTHING;
    """
    process_ignore_duplicate_rule_sql = """
        CREATE OR REPLACE RULE process_table_ignore_duplicate_inserts AS
            ON INSERT TO processes
                WHERE EXISTS (
                  SELECT 1
                FROM processes
                WHERE process_uuid = NEW.process_uuid
            )
            DO INSTEAD NOTHING;
    """

    get_all_children_function_sql = """
        CREATE or REPLACE FUNCTION get_all_children(IN parent_process_uuid UUID)
            RETURNS TABLE(child_process UUID) as $$
              WITH RECURSIVE recursive_table AS (
                SELECT child_process_uuid FROM process_join_table
                WHERE parent_process_uuid=$1
                UNION
                SELECT process_join_table.child_process_uuid FROM process_join_table
                INNER JOIN recursive_table
                ON process_join_table.parent_process_uuid = recursive_table.child_process_uuid)
            SELECT * from recursive_table;
            $$ LANGUAGE SQL;
    """
    get_all_parents_function_sql = """
        CREATE or REPLACE FUNCTION get_all_parents(IN child_process_uuid UUID)
            RETURNS TABLE(parent_process UUID) as $$
              WITH RECURSIVE recursive_table AS (
                SELECT parent_process_uuid FROM process_join_table
                WHERE child_process_uuid=$1
                UNION
                SELECT process_join_table.parent_process_uuid FROM process_join_table
                INNER JOIN recursive_table
                ON process_join_table.child_process_uuid = recursive_table.parent_process_uuid)
            SELECT * from recursive_table;
            $$ LANGUAGE SQL;
    """

    def create_upsert_rules_in_db(self):
        config.db_session.execute(
            self.bundle_file_link_ignore_duplicate_rule_sql + self.bundle_ignore_duplicate_rule_sql
        )
        config.db_session.execute(
            self.process_file_link_ignore_duplicate_rule_sql + self.process_ignore_duplicate_rule_sql
        )
        config.db_session.execute(self.file_ignore_duplicate_rule_sql)
        config.db_session.commit()

    def create_recursive_functions_in_db(self):
        config.db_session.execute(self.get_all_children_function_sql + self.get_all_parents_function_sql)
        config.db_session.commit()


if __name__ == '__main__':
    unittest.main()
