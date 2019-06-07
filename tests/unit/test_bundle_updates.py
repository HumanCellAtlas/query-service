import unittest
from unittest.mock import patch

from dcpquery import config
from dcpquery.etl import drop_one_bundle, process_bundle_event
from tests import mock_bundle_deletion_event


class BundleUpdateEvewnts(unittest.TestCase):
    def test_drop_one_bundle_handles_deletion(self):
        bundle_uuid = 'dfb5a10e-656f-4faa-a0c9-588afdd47e10'
        bundle_version = '2018-10-11T220440.437634Z'
        bundle_fqid = bundle_uuid + '.' + bundle_version

        file_count = config.db_session.execute("SELECT COUNT(*) from files;").fetchall()[0][0]
        self.assertEqual(config.db_session.execute(
            f"SELECT COUNT(*) FROM bundles WHERE fqid='{bundle_fqid}'").fetchall()[0][0], 1)

        self.assertEqual(config.db_session.execute(
            f"SELECT COUNT(*) FROM bundle_file_links where bundle_fqid='{bundle_fqid}'").fetchall()[0][0], 50)
        drop_one_bundle(bundle_uuid, bundle_version)
        self.assertEqual(config.db_session.execute(
            f"SELECT COUNT(*) FROM bundles WHERE fqid='{bundle_fqid}'").fetchall()[0][0], 0)

        self.assertEqual(config.db_session.execute(
            f"SELECT COUNT(*) FROM bundle_file_links where bundle_fqid='{bundle_fqid}'").fetchall()[0][0], 0)
        config.reset_db_session()
        post_deletion_file_count = config.db_session.execute("SELECT COUNT(*) from files;").fetchall()[0][0]

        self.assertLess(post_deletion_file_count, file_count)

    @patch('dcpquery.etl.drop_one_bundle')
    def test_process_bundle_event_handles_deletions(self, mock_bundle_drop):
        process_bundle_event(mock_bundle_deletion_event)
        mock_bundle_drop.assert_called_once_with(
            bundle_uuid='5541acba-066e-4b1e-9420-323513d0a899', bundle_version='2018-10-05T103504.447604Z'
        )
