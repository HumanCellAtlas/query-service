import os
import sys
import unittest

pkg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))  # noqa
sys.path.insert(0, pkg_root)  # noqa

from test import *
from lib.model import Bundle


class TestModel(unittest.TestCase):

    extractor = FixtureExtractor()

    def test_bundle(self):
        bundle = Bundle.from_extractor(self.extractor, vx_bundle.uuid)
        self.assertEqual(vx_bundle, bundle)
        bundle._files = bundle._files[:-1]
        self.assertNotEqual(vx_bundle, bundle)


if __name__ == '__main__':
    unittest.main()
