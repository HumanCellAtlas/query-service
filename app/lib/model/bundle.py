import re
import typing

from uuid import UUID
from lib.etl.extract import Extractor
from lib.model.metadata import FileMetadata
from lib.model.file import File


class BundleManifest(dict):

    @property
    def file_metadata(self) -> typing.List[FileMetadata]:
        return [FileMetadata(f) for f in self['files']]


class Bundle:

    _normalizable_file = re.compile('.*[0-9]+[.]json$')
    _json_file = re.compile('.+[.]json$')

    def __init__(self, fqid: str, bundle_manifest: BundleManifest, files: typing.List[File]):
        self.fqid = fqid
        tmp_uuid, self.version = fqid.split('.', 1)
        self.uuid = UUID(tmp_uuid)
        self._bundle_manifest = bundle_manifest
        self._files = files

    @staticmethod
    def from_extractor(extractor: Extractor, bundle_uuid: UUID, version: str):
        bundle_manifest = BundleManifest(**extractor.extract_bundle(bundle_uuid, version))
        files = [
            File.from_extractor(extractor, m)
            for m in bundle_manifest.file_metadata if Bundle._json_file.match(m.name)
        ]
        return Bundle(
            fqid=f"{bundle_uuid}.{bundle_manifest['version']}",
            bundle_manifest=bundle_manifest,
            files=files
        )

    @property
    def bundle_manifest(self):
        return self._bundle_manifest

    @property
    def indexable_files(self) -> typing.List[File]:
        return [f for f in self._files if f.metadata.indexable]

    @property
    def normalizable_files(self) -> typing.List[File]:
        return [f for f in self.indexable_files if self._normalizable_file.match(f.metadata.name)]

    def __eq__(self, other):
        if isinstance(other, Bundle):
            return self._bundle_manifest == other._bundle_manifest and self._files == other._files
        return False
