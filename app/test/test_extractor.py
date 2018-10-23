import os
import sys
import unittest

pkg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))  # noqa
sys.path.insert(0, pkg_root)  # noqa

from test import *


class TestExtractor(unittest.TestCase):

    extractor = FixtureExtractor()

    def test_bundle(self):
        bundle = self.extractor.extract_bundle(vx_bundle.uuid, vx_bundle.version)
        self.assertEqual(vx_bundle, bundle)
        bundle._files = bundle._files[:-1]
        self.assertNotEqual(vx_bundle, bundle)


if __name__ == '__main__':
    unittest.main()
