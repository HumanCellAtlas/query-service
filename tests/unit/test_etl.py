import unittest
from unittest.mock import patch

from dcpquery.etl.load import load_links


class TestETLHelpers(unittest.TestCase):
    @patch('dcpquery.etl.load.logger.error')
    def test_links_ignore_unknown_format(self, logger):
        load_links([{1: 2}], 'mock_bundle_uuid')
        logger.assert_called_once()


if __name__ == '__main__':
    unittest.main()
