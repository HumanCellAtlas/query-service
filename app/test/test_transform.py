import os
import sys
import unittest

pkg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))  # noqa
sys.path.insert(0, pkg_root)  # noqa

from test import *
from lib.etl.transform import BundleDocumentTransform


class TestTransform(unittest.TestCase):

    def test_construct_documents(self):
        bundle_dict = BundleDocumentTransform.transform(vx_bundle)
        self.assertDictEqual(
            bundle_dict,
            json.loads(load_fixture('vx_bundle_document.json'))
        )

    _expected_document = dict()


if __name__ == '__main__':
    unittest.main()
