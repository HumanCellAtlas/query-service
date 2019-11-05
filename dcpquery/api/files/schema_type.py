import requests
from flask import Response

from dcpquery import config
from dcpquery.db.models import File, DCPMetadataSchemaType


def get(schema_type, version=None):
    """

    :param schema_type: Name of the dcp metadata schema type
    :param version:
    :return:
    """
    major = version.split('.')[0]
    minor = version.split('.')[1]
    if not DCPMetadataSchemaType.get_schema_type(schema_type):
        return Response(status=requests.codes.not_found)

    file_fqids = get_file_fqids_for_schema_type_version(schema_type, major, minor)
    return {"file_fqids": file_fqids, "schema_type": schema_type, "schema_version": version}, requests.codes.ok


def get_file_fqids_for_schema_type_version(schema_type, major, minor):
    file_fqids = config.db_session.query(File) \
        .with_entities(File.fqid) \
        .filter(File.dcp_schema_type_name == schema_type) \
        .filter(File.schema_major_version == major) \
        .filter(File.schema_minor_version == minor) \
        .all()
    return [x[0] for x in file_fqids]
