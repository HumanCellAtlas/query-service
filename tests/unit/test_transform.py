import os, sys, json, copy, shutil, unittest
from tempfile import TemporaryDirectory

from dcpquery.etl import transform_bundle, format_process_info, get_file_extension
from tests import vx_bundle, load_fixture, mock_links, vx_bundle_uuid, vx_bundle_version


class TestTransform(unittest.TestCase):
    def test_construct_documents(self):
        fixtures_path = f"{os.path.dirname(__file__)}/../fixtures"
        expected = json.loads(load_fixture('vx_bundle_document.json'))
        with TemporaryDirectory() as td:
            for f in os.listdir(fixtures_path):
                if f.endswith(".json") and "query" not in f and not f.startswith("vx_"):
                    shutil.copy(os.path.join(fixtures_path, f), td)
            bundle_dict = transform_bundle(bundle_uuid=vx_bundle_uuid,
                                           bundle_version=vx_bundle_version,
                                           bundle_path=td,
                                           bundle_manifest_path=os.path.join(fixtures_path, "vx_bundle.json"))

            self.assertDictEqual(bundle_dict, expected)

    @unittest.skip("WIP")
    # TODO turn this test on
    def test_construct_documents_handles_empty_bundle(self):
        fixtures_path = f"{os.path.dirname(__file__)}/../fixtures"
        expected = json.loads(load_fixture('vx_bundle_document.json'))
        with TemporaryDirectory() as td:
            for f in os.listdir(fixtures_path):
                if f.endswith(".json") and "query" not in f and not f.startswith("vx_") and not f.startswith("mock_"):
                    shutil.copy(os.path.join(fixtures_path, f), td)
            bundle_dict = transform_bundle(bundle_uuid=vx_bundle_uuid,
                                           bundle_version=vx_bundle_version,
                                           bundle_path="/nonexistent-directory",
                                           bundle_manifest_path=os.path.join(fixtures_path, "vx_bundle.json"))
        expected["aggregate_metadata"].clear()
        expected["files"].clear()
        self.assertDictEqual(bundle_dict, expected)

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
