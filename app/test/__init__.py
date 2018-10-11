import os
import json
import sys

pkg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))  # noqa
sys.path.insert(0, pkg_root)  # noqa

from lib.extract import Extractor
from lib.model import Bundle, BundleManifest, File, FileMetadata


def load_fixture(fixture_file):
    with open('test/fixtures/' + fixture_file, 'r') as fh:
        txt = fh.read()
    return txt


vx_bundle_fqid = '0c8d7f15-47c2-42c2-83de-47ae48e1eae1.2018-09-06T190237.485774Z'
vx_bundle_str = load_fixture('vx_bundle.json')

vx_bundle = Bundle(
    fqid=vx_bundle_fqid,
    bundle_manifest=BundleManifest(**json.loads(vx_bundle_str)),
    files=[
        File(
            FileMetadata(d),
            **json.loads(load_fixture(d['name']))
        )
        for d in json.loads(vx_bundle_str)['files'] if d['name'].endswith('.json')
    ]
)


class FixtureExtractor(Extractor):

    _key_to_fixture_map = dict([
        (d.key, load_fixture(d.name))
        for d in BundleManifest(**json.loads(vx_bundle_str)).file_metadata
    ])
    _key_to_fixture_map['bundles/' + vx_bundle_fqid] = vx_bundle_str

    def extract(self, key: str):
        data = self._key_to_fixture_map[key]
        return self._deserialize(data)
