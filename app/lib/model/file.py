import inflect

from uuid import UUID
from lib.model.metadata import FileMetadata


class File(dict):

    _inflect_engine = inflect.engine()

    def __init__(self, metadata: FileMetadata, **kwargs):
        self.metadata = metadata
        super().__init__(kwargs)

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
