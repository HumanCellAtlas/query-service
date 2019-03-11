import typing

import inflection
import re

from uuid import UUID

from query.lib.model.metadata import FileMetadata


class File(dict):

    _normalizable_file = re.compile('^.*[_][0-9]+[.]json$')

    def __init__(self, metadata: FileMetadata, **kwargs):
        self.metadata = metadata
        super().__init__(kwargs)

    @property
    def normalizable(self):
        return self._normalizable_file.match(self.metadata.name) is not None

    @property
    def schema_type(self) -> typing.Optional[str]:
        if self.metadata.indexable:
            return self['describedBy'].split('/')[-1] if 'describedBy' in self else None
        return None

    @property
    def schema_type_plural(self):
        if self.schema_type is None:
            return None
        if '_' in self.schema_type:
            group_words = self.schema_type.split('_')
            group_words[-1] = inflection.pluralize(group_words[-1])
            return '_'.join(group_words)
        return inflection.pluralize(self.schema_type)

    @property
    def uuid(self) -> UUID:
        return self.metadata.uuid

    @property
    def version(self) -> str:
        return self.metadata.version

    @property
    def fqid(self) -> str:
        return f"{self.uuid}.{self.version}"
