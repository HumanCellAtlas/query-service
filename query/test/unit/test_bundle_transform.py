import json
import unittest

from test import vx_bundle, load_fixture


from query.lib.etl.bundle_transform import BundleDocumentTransform


class TestTransform(unittest.TestCase):

    def test_construct_documents(self):
        bundle_dict = BundleDocumentTransform.transform(vx_bundle)
        expected = json.loads(load_fixture('vx_bundle_document.json'))
        self.assertDictEqual(bundle_dict, expected)

    _expected_document = dict()


if __name__ == '__main__':
    unittest.main()
