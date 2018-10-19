import re
import typing
import inflect

from uuid import UUID
from .extract import Extractor


class FileMetadata(dict):

    @property
    def key(self):
        return "blobs/" + '.'.join([
            self['sha256'],
            self['sha1'],
            self['s3-etag'],
            self['crc32c']
        ])

    @property
    def name(self):
        return self['name']

    @property
    def indexable(self):
        return self['indexed']

    @property
    def uuid(self):
        return UUID(self['uuid'])

    @property
    def version(self) -> str:
        return self['version']


class File(dict):

    _inflect_engine = inflect.engine()

    def __init__(self, metadata: FileMetadata, **kwargs):
        self.metadata = metadata
        super().__init__(kwargs)

    @staticmethod
    def from_extractor(extractor: Extractor, metadata: FileMetadata):
        return File(metadata, **extractor.extract_file(metadata.uuid, metadata.version))

    @property
    def schema_module(self):
        return '_'.join(self.metadata.name.split('_')[:-1])

    @property
    def schema_module_plural(self):
        group_words = self.metadata.name.rsplit('_', 1)[0].split('_')
        group_words[-1] = self._inflect_engine.plural(group_words[-1])
        return '_'.join(group_words)

    @property
    def uuid(self) -> UUID:
        return UUID(self['provenance']['document_id'])

    @property
    def version(self) -> str:
        return self.metadata.version

    @property
    def fqid(self) -> str:
        return f"{self.uuid}.{self.version}"


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
