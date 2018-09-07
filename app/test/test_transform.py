import json
import unittest

from test import *
from lib.transform import Bundle, BundleManifest, File, FileDescriptor


class TestTransform(unittest.TestCase):

    extractor = FixtureExtractor()

    extracted_fixtures = Bundle(
        BundleManifest(**json.loads(vx_bundle)),
        [
            File(
                FileDescriptor(d),
                **json.loads(load_fixture(d['name']))
            )
            for d in json.loads(vx_bundle)['files'] if d['name'].endswith('.json')
        ]
    )

    def test_bundle(self):
        bundle = Bundle.load_from_extractor(self.extractor, 'vx_bundle')
        self.assertEqual(self.extracted_fixtures, bundle)
        bundle._files = bundle._files[:-1]
        self.assertNotEqual(self.extracted_fixtures, bundle)
