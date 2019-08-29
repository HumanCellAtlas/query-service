import unittest
from unittest.mock import patch

from dcpquery import config
from dcpquery.db import Bundle
from dcpquery.etl import drop_one_bundle, process_bundle_event
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

        self.assertLess(post_deletion_file_count, file_count)

    @patch('dcpquery.etl.drop_one_bundle')
    def test_process_bundle_event_handles_deletions(self, mock_bundle_drop):
        process_bundle_event(mock_bundle_deletion_event)
        mock_bundle_drop.assert_called_once_with(
            bundle_uuid='5541acba-066e-4b1e-9420-323513d0a899', bundle_version='2018-10-05T103504.447604Z'
        )
