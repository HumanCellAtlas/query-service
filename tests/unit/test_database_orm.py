import time
import unittest

from dcpquery.db import Bundle, BundleFileLink, Process, File, ProcessFileLink, ConnectionTypeEnum
from dcpquery.etl import load_links, update_process_join_table
from tests import vx_bundle, vx_bf_links, vx_bundle_aggregate_md, mock_links

from dcpquery import config


class TestBundles(unittest.TestCase):
    def test_insert_select_bundle(self):
        config.db_session.add(vx_bundle)
        config.db_session.commit()

        # select bundle
        bundle = Bundle.select_bundle(vx_bundle.fqid)
        res = config.db_session.query(Bundle).filter(Bundle.uuid == vx_bundle.uuid,
                                                     Bundle.version == vx_bundle.version).all()
        result = list(res)
        self.assertEqual(len(result), 1)

        self.assertEqual(result[0], bundle)
        self.assertEqual(result[0].uuid, vx_bundle.uuid)
        self.assertEqual(result[0].version, vx_bundle.version)
        expect_version = vx_bundle.version.strftime("%Y-%m-%dT%H%M%S.%fZ")
        self.assertEqual(result[0].fqid, f"{vx_bundle.uuid}.{expect_version}")
        self.assertDictEqual(result[0].aggregate_metadata, vx_bundle_aggregate_md)
        self.assertEqual(len(result[0].files), len(vx_bundle.files))
        self.assertSetEqual(set(f.fqid for f in vx_bundle.files), set(f.fqid for f in result[0].files))

    def test_delete_bundles_deletes_list_of_bundles(self):
        bundle_fqids = [bundle[0] for bundle in config.db_session.query("fqid FROM bundles LIMIT 3;").all()]
        # Need to delete bundle_file_links with fk to bundle prior to deleting the bundle
        BundleFileLink.delete_links_for_bundles(bundle_fqids)

        Bundle.delete_bundles(bundle_fqids)

        for bundle_fqid in bundle_fqids:
            self.assertEqual(Bundle.select_bundle(bundle_fqid=bundle_fqid), None)


class TestBundleFileLinks(unittest.TestCase):
    project_file = next(l.file for l in vx_bf_links if l.name == 'project_0.json')
    process_file = next(l.file for l in vx_bf_links if l.name == 'process_0.json')

    def test_insert_select_bundle_file_link(self):
        # insert bundle-file links
        config.db_session.add_all(vx_bf_links)
        config.db_session.commit()

        # select bundle-file links
        res = config.db_session.query(BundleFileLink).filter(BundleFileLink.bundle_fqid == vx_bundle.fqid,
                                                             BundleFileLink.file_fqid == self.process_file.fqid)
        result = list(res)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, "process_0.json")
        self.assertEqual(result[0].bundle_fqid, vx_bundle.fqid)
        self.assertEqual(result[0].file_fqid, self.process_file.fqid)

        res = BundleFileLink.select_links_for_bundle_fqids(bundle_fqids=[vx_bundle.fqid]).fetchall()

        result = sorted(res, key=lambda x: x.file_fqid)
        self.assertEqual(len(result), 14)
        expect_version = vx_bundle.version.strftime("%Y-%m-%dT%H%M%S.%fZ")

        self.assertEqual(result[1].bundle_fqid, f"{vx_bundle.uuid}.{expect_version}")
        expect_version = self.process_file.version.strftime("%Y-%m-%dT%H%M%S.%fZ")
        self.assertEqual(result[1].file_fqid, f"{self.process_file.uuid}.{expect_version}")

        self.assertEqual(result[6].bundle_fqid, f"{vx_bundle.uuid}.{expect_version}")

        expect_version = self.project_file.version.strftime("%Y-%m-%dT%H%M%S.%fZ")
        self.assertEqual(result[6].file_fqid, f"{self.project_file.uuid}.{expect_version}")

    def test_select_links_by_file_fqids(self):
        file_fqid = config.db_session.query("fqid FROM files LIMIT 1;").all()[0][0]
        expected_bundle_file_links = config.db_session.execute(
            f"SELECT * FROM bundle_file_links where file_fqid='{file_fqid}'").fetchall()

        config.db_session.expire_all()
        actual_bundle_file_links = BundleFileLink.select_links_for_file_fqids([file_fqid]).fetchall()
        self.assertCountEqual(expected_bundle_file_links, actual_bundle_file_links)

    def test_delete_links_for_bundle(self):
        bundle_fqid = config.db_session.query("bundle_fqid FROM bundle_file_links LIMIT 1;").all()[0][0]
        bundle_file_links = config.db_session.execute(
            f"SELECT * FROM bundle_file_links where bundle_fqid='{bundle_fqid}'").fetchall()
        self.assertGreater(len(bundle_file_links), 0)
        BundleFileLink.delete_links_for_bundles([bundle_fqid])
        bundle_file_links = config.db_session.execute(
            f"SELECT * FROM bundle_file_links where bundle_fqid='{bundle_fqid}'").fetchall()

        self.assertEqual(len(bundle_file_links), 0)

    def test_delete_links_for_file(self):
        file_fqid = config.db_session.query("file_fqid FROM bundle_file_links LIMIT 1;").all()[0][0]
        bundle_file_links = BundleFileLink.select_links_for_file_fqids(file_fqids=[file_fqid]).fetchall()
        self.assertGreater(len(bundle_file_links), 0)
        BundleFileLink.delete_links_for_files([file_fqid])
        bundle_file_links = BundleFileLink.select_links_for_file_fqids(file_fqids=[file_fqid]).fetchall()

        self.assertEqual(len(bundle_file_links), 0)

    def test_select_links_by_bundle_fqids(self):
        bundle_fqid = config.db_session.query("fqid FROM bundles LIMIT 1;").all()[0][0]
        expected_bundle_file_links = config.db_session.execute(
            f"SELECT * FROM bundle_file_links where bundle_fqid='{bundle_fqid}'").fetchall()

        config.db_session.expire_all()
        actual_bundle_file_links = BundleFileLink.select_links_for_bundle_fqids([bundle_fqid]).fetchall()
        self.assertCountEqual(expected_bundle_file_links, actual_bundle_file_links)


class TestProcessFileLinks(unittest.TestCase):
    def setUp(self):
        self.project_uuid = "394a5578-90ec-41ec-9377-82b04dcca1d4"
        self.project_verion = "2018-10-03T19:27:55.449Z"
        process_uuid = "42fe7e59-220d-473c-afe5-42a6d315d778"
        self.project_fqid = self.project_uuid + "." + self.project_verion
        self.cell_suspension_fqid_v2 = "c4c2f98a-93d4-488c-aaf5-4602359e27e9.2018-12-08 09:35:54.808000"
        cell_suspension_fqid = "c4c2f98a-93d4-488c-aaf5-4602359e27e9.2018-10-08 09:35:54.808000"

        File(fqid=self.project_fqid, body={"mock": "mock"},
             dcp_schema_type_name='project',
             content_type="application/json; dcp-type='metadata/project'", extension=".json", size=4448)
        process = Process(process_uuid=process_uuid)
        cell_suspension = File(fqid=cell_suspension_fqid, body={"mock": "mock"},
                               dcp_schema_type_name='cell_suspension',
                               content_type="application/json; dcp-type='metadata/biomaterial'", size=921,
                               extension=".json")

        File(fqid=self.cell_suspension_fqid_v2, body={"mock": "mock"},
             dcp_schema_type_name='cell_suspension',
             content_type="application/json; dcp-type='metadata/biomaterial'", size=921,
             extension=".json")
        self.pfl = ProcessFileLink(process_uuid=process.process_uuid, project_fqid=self.project_fqid,
                                   file_uuid=cell_suspension.uuid,
                                   process_file_connection_type=ConnectionTypeEnum.INPUT_ENTITY)

    def test_most_recent_file_version(self):
        file = self.pfl.get_most_recent_file()
        self.assertEqual(file.fqid, self.cell_suspension_fqid_v2)

    def test_project_uuid(self):
        self.assertEqual(self.pfl.project_uuid, self.project_uuid)

    def test_project_version(self):
        self.assertEqual(self.pfl.project_version, self.project_verion)


class TestProcesses(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        load_links(mock_links['links'], 'mock_bundle_uuid', 'mock_project_fqid')
        config.db_session.commit()
        update_process_join_table()

    def test_get_all_parents(self):
        parent_processes = Process.list_all_parent_processes('a0000000-aaaa-aaaa-aaaa-aaaaaaaaaaaa')
        expected_parents = ['a0000003-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'a0000004-aaaa-aaaa-aaaa-aaaaaaaaaaaa']
        self.assertCountEqual(expected_parents, parent_processes)

    def test_get_all_children(self):
        child_processes = Process.list_all_child_processes('a0000003-aaaa-aaaa-aaaa-aaaaaaaaaaaa')
        expected_children = ['a0000000-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'a0000001-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
                             'a0000002-aaaa-aaaa-aaaa-aaaaaaaaaaaa']
        self.assertCountEqual(expected_children, child_processes)


class TestFiles(unittest.TestCase):
    project_file = next(l.file for l in vx_bf_links if l.name == 'project_0.json')
    process_file = next(l.file for l in vx_bf_links if l.name == 'process_0.json')

    def test_insert_select_file(self):
        # insert files
        config.db_session.rollback()
        config.db_session.add_all([self.project_file, self.process_file])
        config.db_session.commit()

        # select files
        result = File.select_file(file_fqid=self.project_file.fqid)

        self.assertEqual(result.uuid, self.project_file.uuid)
        self.assertEqual(result.version, self.project_file.version)
        expect_version = self.project_file.version.strftime("%Y-%m-%dT%H%M%S.%fZ")
        self.assertEqual(result.fqid, f"{self.project_file.uuid}.{expect_version}")
        self.assertEqual(result.body, self.project_file.body)

    def test_delete_files(self):
        file_fqids = [file[0] for file in config.db_session.query("fqid FROM files LIMIT 3;").all()]
        # Need to delete bundle_file_links with fk to file prior to deleting the file
        BundleFileLink.delete_links_for_files(file_fqids)

        File.delete_files(file_fqids)

        for file_fqid in file_fqids:
            self.assertEqual(File.select_file(file_fqid=file_fqid), None)


if __name__ == '__main__':
    unittest.main()
