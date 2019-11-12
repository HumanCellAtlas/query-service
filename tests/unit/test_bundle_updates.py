import datetime
import unittest
import uuid
from unittest.mock import patch

from dcpquery import config
from dcpquery.db.models import Bundle, Project, File, ProjectFileLink, BundleFileLink
from dcpquery.dss_subscription_event_handling import drop_one_bundle, process_bundle_event
from tests import mock_bundle_deletion_event


class BundleUpdateEvents(unittest.TestCase):
    def test_drop_one_bundle_handles_deletion(self):
        bundle_fqid = config.db_session.execute(
            "SELECT fqid FROM bundles_all_versions LIMIT 1;").fetchall()[0][0]

        bundle_uuid = bundle_fqid.split('.', 1)[0]
        bundle_version = bundle_fqid.split('.', 1)[1]

        file_count = config.db_session.execute("SELECT COUNT(*) from files_all_versions;").fetchall()[0][0]
        self.assertIsNotNone(Bundle.select_bundle(bundle_fqid))
        self.assertGreaterEqual(config.db_session.execute(
            f"SELECT COUNT(*) FROM bundle_file_links where bundle_fqid='{bundle_fqid}'").fetchall()[0][0], 0)

        drop_one_bundle(bundle_uuid, bundle_version)

        self.assertIsNone(Bundle.select_bundle(bundle_fqid))
        self.assertEqual(config.db_session.execute(
            f"SELECT COUNT(*) FROM bundle_file_links where bundle_fqid='{bundle_fqid}'").fetchall()[0][0], 0)

        post_deletion_file_count = config.db_session.execute(
            "SELECT COUNT(*) from files_all_versions;").fetchall()[0][0]

        self.assertLessEqual(post_deletion_file_count, file_count)

    @patch('dcpquery.dss_subscription_event_handling.drop_one_bundle')
    def test_process_bundle_event_handles_deletions(self, mock_bundle_drop):
        process_bundle_event(mock_bundle_deletion_event)
        mock_bundle_drop.assert_called_once()


class BundleDeletion(unittest.TestCase):
    def setUp(self):
        self.version = str(datetime.datetime.utcnow())
        self.version_2 = str(datetime.datetime.utcnow() + datetime.timedelta(0, 60))

        self.project_0_uuid = str(uuid.uuid4())
        self.project_1_uuid = str(uuid.uuid4())
        self.project_2_uuid = str(uuid.uuid4())

        self.bundle_0_uuid = str(uuid.uuid4())
        self.bundle_1_uuid = str(uuid.uuid4())

        self.file_0_uuid = str(uuid.uuid4())
        self.file_1_uuid = str(uuid.uuid4())
        self.file_2_uuid = str(uuid.uuid4())

        project_0 = Project(uuid=self.project_0_uuid, version=self.version)
        project_1 = Project(uuid=self.project_1_uuid, version=self.version)
        project_2 = Project(uuid=self.project_2_uuid, version=self.version)

        bundle_0 = Bundle(uuid=self.bundle_0_uuid, version=self.version)
        bundle_1 = Bundle(uuid=self.bundle_1_uuid, version=self.version)
        bundle_1_v2 = Bundle(uuid=self.bundle_1_uuid, version=self.version_2)

        file_0 = File(uuid=self.file_0_uuid, version=self.version)
        file_1 = File(uuid=self.file_1_uuid, version=self.version)
        file_2 = File(uuid=self.file_2_uuid, version=self.version)
        file_1_v2 = File(uuid=self.file_1_uuid, version=self.version_2)

        project_file_link_0 = ProjectFileLink(project=project_0, file=file_0)
        project_file_link_1 = ProjectFileLink(project=project_1, file=file_1)
        project_file_link_2 = ProjectFileLink(project=project_2, file=file_2)

        project_file_link_3 = ProjectFileLink(project=project_1, file=file_1_v2)

        bundle_file_link_0 = BundleFileLink(bundle=bundle_0, file=file_0, name="file_0")
        bundle_file_link_1 = BundleFileLink(bundle=bundle_1, file=file_1, name="file_1")
        bundle_file_link_2 = BundleFileLink(bundle=bundle_0, file=file_2, name="file_2")
        bundle_file_link_3 = BundleFileLink(bundle=bundle_1, file=file_2, name="file_2")

        bundle_file_link_4 = BundleFileLink(bundle=bundle_1_v2, file=file_1_v2, name="file_1")
        bundle_file_link_5 = BundleFileLink(bundle=bundle_1_v2, file=file_2, name="file_1")

        config.db_session.add_all(
            [project_file_link_0, project_file_link_1, project_file_link_2, project_file_link_3, bundle_file_link_0,
             bundle_file_link_1, bundle_file_link_2, bundle_file_link_3, bundle_file_link_4, bundle_file_link_5])

        config.db_session.commit()

    def test_bundle_deletion_cascades_to_files(self):
        # check bundle and files exist
        bundle_fqid = self.bundle_1_uuid + '.' + self.version
        self.assertEqual(Bundle.select_bundle(bundle_fqid).fqid, bundle_fqid)

        file_0_fqid = self.file_0_uuid + '.' + self.version
        file_1_fqid = self.file_1_uuid + '.' + self.version
        file_2_fqid = self.file_2_uuid + '.' + self.version
        self.assertEqual(File.select_file(file_0_fqid).fqid, file_0_fqid)
        self.assertEqual(File.select_file(file_1_fqid).fqid, file_1_fqid)
        self.assertEqual(File.select_file(file_2_fqid).fqid, file_2_fqid)

        drop_one_bundle(self.bundle_1_uuid, self.version)
        config.db_session.flush()

        # check files only in that bundle are gone
        self.assertEqual(File.select_file(file_1_fqid), None)
        self.assertEqual(File.select_file(file_0_fqid).fqid, file_0_fqid)
        self.assertEqual(File.select_file(file_2_fqid).fqid, file_2_fqid)

    def test_bundle_deletion_cascades_to_projects(self):
        project_0_fqid = self.project_0_uuid + '.' + self.version
        project_1_fqid = self.project_1_uuid + '.' + self.version
        project_2_fqid = self.project_2_uuid + '.' + self.version

        self.assertIsNotNone(Project.select_one(project_0_fqid))
        self.assertIsNotNone(Project.select_one(project_1_fqid))
        self.assertIsNotNone(Project.select_one(project_2_fqid))
        config.readonly_db = False

        drop_one_bundle(self.bundle_0_uuid, self.version)
        config.db_session.flush()
        self.assertIsNone(Project.select_one(project_0_fqid))
        self.assertIsNotNone(Project.select_one(project_1_fqid))
        self.assertIsNotNone(Project.select_one(project_2_fqid))

    def test_bundle_deletion_and_cascade_is_version_specific(self):
        bundle_1_v2_fqid = self.bundle_1_uuid + '.' + self.version_2
        project_1_fqid = self.project_1_uuid + '.' + self.version
        file_1_v2_fqid = self.file_1_uuid + '.' + self.version_2
        drop_one_bundle(self.bundle_1_uuid, self.version)
        self.assertIsNotNone(Bundle.select_bundle(bundle_1_v2_fqid))
        self.assertIsNotNone(Project.select_one(project_1_fqid))
        self.assertIsNotNone(File.select_file(file_1_v2_fqid))
