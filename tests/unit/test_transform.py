import json
import unittest

from dcpquery.etl import format_process_info, get_file_extension
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

    def test_get_file_extension(self):
        file0_name = 'anything.json'
        file1_name = 'somethingelse.fastq.gz'
        file2_name = 'no_extension'

        file0_extension = get_file_extension(file0_name)
        file1_extension = get_file_extension(file1_name)
        file2_extension = get_file_extension(file2_name)

        self.assertEqual(file0_extension, '.json')
        self.assertEqual(file1_extension, '.fastq.gz')
        self.assertEqual(file2_extension, None)


if __name__ == '__main__':
    unittest.main()
