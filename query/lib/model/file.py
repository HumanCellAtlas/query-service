import inflect
import re

from uuid import UUID
from lib.model.metadata import FileMetadata


class File(dict):

    _inflect_engine = inflect.engine()
    _normalizable_file = re.compile('.*[0-9]+[.]json$')

    def __init__(self, metadata: FileMetadata, **kwargs):
        self.metadata = metadata
        super().__init__(kwargs)

    @property
    def normalizable(self):
        return self._normalizable_file.match(self.metadata.name) is not None

    @property
    def schema_module(self):
        return '_'.join(self.metadata.name.split('_')[:-1])

    @property
    def schema_module_plural(self):
        tmp = self.metadata.name.replace('.json', '')
        if '_' not in tmp:
            return tmp
        group_words = tmp.rsplit('_', 1)[0].split('_')
        group_words[-1] = self._inflect_engine.plural(group_words[-1])
        return '_'.join(group_words)

    @property
    def uuid(self) -> UUID:
        return self.metadata.uuid

    @property
    def version(self) -> str:
        return self.metadata.version

    @property
    def fqid(self) -> str:
        return f"{self.uuid}.{self.version}"
