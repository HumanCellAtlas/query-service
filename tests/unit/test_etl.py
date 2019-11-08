import datetime
import unittest
from unittest.mock import patch

import mock
from dcplib.etl import DSSExtractor

from dcpquery.etl import etl_one_bundle
from dcpquery.etl.load import load_links, BundleLoader


class TestETLHelpers(unittest.TestCase):
    @patch('dcpquery.etl.load.logger.error')
    def test_links_ignore_unknown_format(self, logger):
        load_links([{1: 2}], 'mock_bundle_uuid')
        logger.assert_called_once()

    @patch('dcpquery.etl.os')
    @patch('dcpquery.etl.transform_bundle')
    @patch.object(BundleLoader, 'load_bundle')
    @patch('dcpquery.etl.config')
    @patch('dcpquery.etl.DSSExtractor')
    def test_etl_one_bundle_calls_load_transform_and_commit(self, mock_extractor, mock_config, mock_loader, mock_transform_bundle, mock_os):
        mock_extractor.return_value.get_files_to_fetch_for_bundle.return_value = 0, 0, []
        mock_bundle_version = datetime.datetime.utcnow()
        mock_bundle_uuid = "AAAAAAAA-AAAA-AAAA-AAAA-AAAAAAAAAAAA"
        etl_one_bundle(bundle_uuid=mock_bundle_uuid, bundle_version=mock_bundle_version)
        self.assertEqual(mock_loader.call_count, 1)
        self.assertEqual(mock_transform_bundle.call_count, 1)
        self.assertEqual(mock_config.db_session.commit.call_count, 1)


if __name__ == '__main__':
    unittest.main()
