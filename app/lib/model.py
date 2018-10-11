import typing
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
        return self['uuid']

    @property
    def version(self):
        return self['version']


class File(dict):

    def __init__(self, metadata: FileMetadata, **kwargs):
        self.metadata = metadata
        super().__init__(kwargs)

    @staticmethod
    def from_extractor(extractor: Extractor, metadata: FileMetadata):
        return File(metadata, **extractor.extract(metadata.key))


class BundleManifest(dict):

    @property
    def file_metadata(self):
        return [FileMetadata(f) for f in self['files'] if f['name'].endswith('.json')]


class Bundle:

    def __init__(self, fqid: str, bundle_manifest: BundleManifest, files: typing.List[File]):
        self.fqid = fqid
        self.uuid, self.version = fqid.split('.', 1)
        self._bundle_manifest = bundle_manifest
        self._files = files

    @staticmethod
    def from_extractor(extractor: Extractor, bundle_key: str):
        bundle_manifest = BundleManifest(**extractor.extract(bundle_key))
        _, bundle_fqid = bundle_key.split('/')
        files = []
        for metadata in bundle_manifest.file_metadata:
            files += [File.from_extractor(extractor, metadata)]
        return Bundle(fqid=bundle_fqid, bundle_manifest=bundle_manifest, files=files)

    @property
    def bundle_manifest(self):
        return self._bundle_manifest

    @property
    def indexable_files(self):
        return [f for f in self._files if f.metadata.indexable]

    def __eq__(self, other):
        if isinstance(other, Bundle):
            return self._bundle_manifest == other._bundle_manifest and self._files == other._files
        return False
