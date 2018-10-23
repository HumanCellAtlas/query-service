from uuid import UUID


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
