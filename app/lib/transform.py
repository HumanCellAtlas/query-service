import inflect
import re

from lib.model import Bundle, FileMetadata


class BundleDocumentTransform:

    _inflect_engine = inflect.engine()
    _array_file_regexp = re.compile('^[a-zA-Z0-9_]*_[0-9]*[.]json$')

    @classmethod
    def transform(cls, bundle: Bundle):
        """
        transform a bundle into an aggregated bundle document

        Below are the transformation rules. All keys are first-level keys in the dictionary.

            1. ret_val['uuid'] is set to the bundle's uuid
            2. ret_val['version'] is set to the version of the bundle
            3. ret_val['manifest'] is set to the bundle manifest
            4. ret_val[plural('<prefix>')] is set to an array containing all indexable file data from files with
               file names of the format <prefix>_###.json
            5. ret_val['<prefix>'] is set to the file data from all remaining indexable files of format <prefix>.json

        :param bundle: the bundle to transform
        :return: the bundle document as a dictionary
        """
        document = dict(
            uuid=str(bundle.uuid),
            version=bundle.version,
            manifest=bundle.bundle_manifest
        )
        for file_data in bundle.indexable_files:
            file_name = file_data.metadata.name
            is_for_array = cls._array_file_regexp.match(file_name)
            if is_for_array:
                if file_data.schema_module_plural not in document:
                    document[file_data.schema_module_plural] = []
                document[file_data.schema_module_plural] += [file_data]
            else:
                key_name = re.sub('[.]json$', '', file_name)
                document[key_name] = file_data
        return dict(**document)
