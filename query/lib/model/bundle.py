import re
import typing

from uuid import UUID
from ..model.metadata import FileMetadata
from ..model.file import File


class BundleManifest(dict):

    @property
    def file_metadata(self) -> typing.List[FileMetadata]:
        return [FileMetadata(f) for f in self['files']]


class Bundle:

    def __init__(self, fqid: str, bundle_manifest: BundleManifest, files: typing.List[File]):
        self.fqid = fqid
        tmp_uuid, self.version = fqid.split('.', 1)
        self.uuid = UUID(tmp_uuid)
        self._bundle_manifest = bundle_manifest
        self._files = files

    @property
    def bundle_manifest(self):
        return self._bundle_manifest

    @property
    def files(self) -> typing.List[File]:
        return self._files

    def __eq__(self, other):
        if isinstance(other, Bundle):
            return self._bundle_manifest == other._bundle_manifest and self._files == other._files
        return False
