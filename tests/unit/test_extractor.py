import os
import sys
import unittest

from tests import vx_bundle


@unittest.skip("WIP")
class TestExtractor(unittest.TestCase):

    # extractor = FixtureExtractor()

    def test_bundle(self):
        bundle = self.extractor.extract_bundle(vx_bundle.uuid, vx_bundle.version)
        self.assertEqual(vx_bundle, bundle)
        bundle._files = bundle._files[:-1]
        self.assertNotEqual(vx_bundle, bundle)


if __name__ == '__main__':
    unittest.main()
