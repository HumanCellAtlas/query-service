import json
import typing
from uuid import UUID

from hca.dss import DSSClient


class Extractor:

    def extract_bundle(self, uuid: UUID, version: typing.Optional[str]):
        raise NotImplementedError()

    def extract_file(self, uuid: UUID):
        raise NotImplementedError()

    @staticmethod
    def _deserialize(serialized_json: str):
        return json.loads(serialized_json)


class DSSClientExtractor(Extractor):

    def __init__(self, dss: DSSClient):
        self._dss = dss

    def extract_bundle(self, uuid: UUID, version: typing.Optional[str]=None):
        return self._dss.get_bundle(replica='aws', uuid=str(uuid), version=version)['bundle']

    def extract_file(self, uuid: UUID):
        return self._dss.get_file(replica='aws', uuid=str(uuid))


