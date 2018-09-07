import os
import json
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))) + "/..")

from lib.extract import Extractor
from lib.transform import BundleManifest


def load_fixture(fixture_file):
    with open('test/fixtures/' + fixture_file, 'r') as fh:
        txt = fh.read()
    return txt


vx_bundle = load_fixture('vx_bundle.json')


class FixtureExtractor(Extractor):

    _key_to_fixture_map = dict([
        (d.key, load_fixture(d.name))
        for d in BundleManifest(**json.loads(vx_bundle)).descriptors
    ])
    _key_to_fixture_map['vx_bundle'] = vx_bundle

    def extract(self, key: str):
        data = self._key_to_fixture_map[key]
        return self._deserialize(data)
