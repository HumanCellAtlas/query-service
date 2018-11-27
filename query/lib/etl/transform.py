from collections import defaultdict

from lib.model import Bundle


class BundleDocumentTransform:

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
        document = defaultdict(list)
        document.update(
            uuid=str(bundle.uuid),
            version=bundle.version,
            manifest=bundle.bundle_manifest
        )

        for file in bundle.files:
            if not file.metadata.indexable:
                continue
            if file.schema_type_plural:
                if file.normalizable:
                    document[file.schema_type_plural].append(file)
                else:
                    document[file.schema_type] = file

        return dict(**document)
