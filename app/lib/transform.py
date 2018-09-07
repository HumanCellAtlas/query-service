import typing
from .extract import Extractor


class FileDescriptor(dict):

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


class File(dict):

    def __init__(self, descriptor: FileDescriptor, **kwargs):
        self.descriptor = descriptor
        super().__init__(kwargs)

    @staticmethod
    def load_from_extractor(extractor: Extractor, descriptor: FileDescriptor):
        return File(descriptor, **extractor.extract(descriptor.key))

    @property
    def is_project(self):
        return self.descriptor.name.startswith('project_')

    @property
    def is_json_file(self):
        return not self.is_project and self.descriptor.name.endswith('.json')


class BundleManifest(dict):

    @property
    def descriptors(self):
        return [FileDescriptor(f) for f in self['files'] if f['name'].endswith('.json')]


class Bundle:

    def __init__(self, bundle_manifest: BundleManifest, files: typing.List[File]):
        self._bundle_manifest = bundle_manifest
        self._files = files

    @staticmethod
    def load_from_extractor(extractor: Extractor, bundle_fqid: str):
        bundle_manifest = BundleManifest(**extractor.extract(bundle_fqid))
        files = []
        for descriptor in bundle_manifest.descriptors:
            files += [File.load_from_extractor(extractor, descriptor)]
        return Bundle(bundle_manifest=bundle_manifest, files=files)

    @property
    def bundle_manifest(self):
        return self._bundle_manifest

    @property
    def projects(self):
        return [f for f in self._files if f.is_project]

    @property
    def json_files(self):
        return [f for f in self._files if f.is_json_file]

    def __eq__(self, other):
        if isinstance(other, Bundle):
            return self._bundle_manifest == other._bundle_manifest and self._files == other._files
        return False
