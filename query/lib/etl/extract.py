import json
import re
from functools import lru_cache
from uuid import UUID

from hca.dss import DSSClient

from ..model import FileMetadata, File, Bundle, BundleManifest
from ..etl.s3_client import S3Client


class Extractor:

    def extract_bundle(self, uuid: UUID, version: str) -> Bundle:
        bundle_manifest = BundleManifest(**self._get_bundle_data(uuid, version))
        files = [
            File(m, **self._get_file_data(m)) if m.indexable else File(m)
            for m in bundle_manifest.file_metadata
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

    @lru_cache(maxsize=1000)
    def _get_bundle_data(self, uuid: UUID, version: str) -> dict:
        return self._dss.get_bundle(replica='aws', uuid=str(uuid), version=version)['bundle']

    @lru_cache(maxsize=1000)
    def _get_file_data(self, file_metadata: FileMetadata) -> dict:
        return self._dss.get_file(replica='aws', uuid=str(file_metadata.uuid), version=file_metadata.version)


class S3Extractor(Extractor):

    def __init__(self, s3: S3Client):
        self._s3 = s3

    @lru_cache(maxsize=1000)
    def _get_bundle_data(self, uuid: UUID, version: str) -> dict:
        return json.loads(self._s3.get(f"bundles/{uuid}.{version}"))

    @lru_cache(maxsize=1000)
    def _get_file_data(self, file_metadata: FileMetadata) -> dict:
        return json.loads(self._s3.get(file_metadata.key))

