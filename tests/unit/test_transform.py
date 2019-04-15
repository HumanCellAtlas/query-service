import json
import unittest

from dcpquery.etl import format_process_info
from tests import vx_bundle, load_fixture, mock_links


class TestTransform(unittest.TestCase):

    @unittest.skip("WIP")
    def test_construct_documents(self):
        bundle_dict = {}  # BundleDocumentTransform.transform(vx_bundle)
        expected = json.loads(load_fixture('vx_bundle_document.json'))
        self.assertDictEqual(bundle_dict, expected)

    _expected_document = dict()

    def test_format_process_info_correctly_formats_link_object(self):
        expected_process = {'process_uuid': 'a0000000-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
                            'input_file_uuids': ['b0000001-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
                                                 'b0000002-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
                                                 'b0000003-aaaa-aaaa-aaaa-aaaaaaaaaaaa'],
                            'output_file_uuids': ['b0000004-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
                                                  'b0000005-aaaa-aaaa-aaaa-aaaaaaaaaaaa'],
                            'protocol_uuids': ['c0000000-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
                                               'c0000001-aaaa-aaaa-aaaa-aaaaaaaaaaaa']}
        process = format_process_info(mock_links['links'][0])
        self.assertDictEqual(process, expected_process)


if __name__ == '__main__':
    unittest.main()
