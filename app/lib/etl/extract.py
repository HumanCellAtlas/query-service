import json
from functools import lru_cache
from uuid import UUID

from hca.dss import DSSClient


class Extractor:

    def extract_bundle(self, uuid: UUID, version: str):
        raise NotImplementedError()

    def extract_file(self, uuid: UUID, version: str):
        raise NotImplementedError()

    @staticmethod
    def _deserialize(serialized_json: str):
        return json.loads(serialized_json)


class DSSClientExtractor(Extractor):

    def __init__(self, dss: DSSClient):
        self._dss = dss

    @lru_cache(maxsize=1000)
    def extract_bundle(self, uuid: UUID, version: str):
        return self._dss.get_bundle(replica='aws', uuid=str(uuid), version=version)['bundle']

    @lru_cache(maxsize=1000)
    def extract_file(self, uuid: UUID, version: str):
        return self._dss.get_file(replica='aws', uuid=str(uuid))
