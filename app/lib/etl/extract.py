import json
import re
from functools import lru_cache
from uuid import UUID

from hca.dss import DSSClient

from lib.model import FileMetadata, File, Bundle, BundleManifest
from lib.etl.s3_client import S3Client


class Extractor:

    _json_file = re.compile('.+[.]json$')

    def extract_bundle(self, uuid: UUID, version: str) -> Bundle:
        bundle_manifest = BundleManifest(**self._get_bundle_data(uuid, version))
        files = [
            File(m, **self._get_file_data(m))
            for m in bundle_manifest.file_metadata if Extractor._json_file.match(m.name)
        ]
        return Bundle(
            fqid=f"{uuid}.{bundle_manifest['version']}",
            bundle_manifest=bundle_manifest,
            files=files
        )

    def _get_bundle_data(self, uuid: UUID, version: str) -> dict:
        raise NotImplementedError()

    def _get_file_data(self, file_metadata: FileMetadata) -> dict:
        raise NotImplementedError()

    @staticmethod
    def _deserialize(serialized_json: str):
        return json.loads(serialized_json)


class DSSExtractor(Extractor):

    def __init__(self, dss: DSSClient):
        self._dss = dss

    def extract_bundle(self, uuid: UUID, version: str) -> Bundle:
        raise NotImplementedError()

    @lru_cache(maxsize=1000)
    def _get_bundle_data(self, uuid: UUID, version: str) -> dict:
        return self._dss.get_bundle(replica='aws', uuid=str(uuid), version=version)['bundle']

    @lru_cache(maxsize=1000)
    def _get_file_data(self, file_metadata: FileMetadata) -> dict:
        return self._dss.get_file(replica='aws', uuid=str(file_metadata.uuid), version=file_metadata.version)


class S3Extractor(Extractor):

    def __init__(self, s3: S3Client):
        self._s3 = s3

    def extract_bundle(self, uuid: UUID, version: str) -> Bundle:
        raise NotImplementedError()

    @lru_cache(maxsize=1000)
    def _get_bundle_data(self, uuid: UUID, version: str) -> dict:
        return self._s3.get(f"bundles/{uuid}.{version}")

    @lru_cache(maxsize=1000)
    def _get_file_data(self, file_metadata: FileMetadata) -> dict:
        return self._s3.get(file_metadata.key)
