import inflect
import re

from copy import deepcopy

from .model import Bundle


class BundleDocumentTransform:

    _inflect_engine = inflect.engine()
    _array_file_regexp = re.compile('^[a-zA-Z0-9_]*_[0-9]*[.]json$')

    @staticmethod
    def transform(bundle: Bundle):
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
            uuid=bundle.uuid,
            version=bundle.version,
            manifest=bundle.bundle_manifest
        )
        for file_data in bundle.indexable_files:
            file_name = file_data.metadata.name
            is_for_array = BundleDocumentTransform._array_file_regexp.match(file_name)
            if is_for_array:
                group_name = BundleDocumentTransform._get_group_name(file_data.metadata.name)
                if group_name not in document:
                    document[group_name] = []
                document[group_name] += [file_data]
            else:
                key_name = re.sub('[.]json$', '', file_name)
                document[key_name] = file_data
        return dict(**document)

    @staticmethod
    def _get_group_name(file_name):
        group_words = file_name.rsplit('_', 1)[0].split('_')
        group_words[-1] = BundleDocumentTransform._inflect_engine.plural(group_words[-1])
        return '_'.join(group_words)
