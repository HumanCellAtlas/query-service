import requests
from flask import Response
from dcpquery.db.models import File, BundleFileLink
from dcpquery.exceptions import DCPFileNotFoundError


def get(file_uuid, check_events):
    """
    Function called by /files/{file_uuid}/bundles endpoint
    :param file_uuid: UUID of file of interest
    :param check_events: Boolean to flag if it is necessary to check for recent bundle events from the dss
    :return: an object containing the file_uuid and a list of bundle_fqids that file belongs to
    """
    if check_events:
        pass
        # TODO when dss event replay endpoint available, set up cron job and check for missed events
    try:
        files = File.select_files_for_uuid(file_uuid)
    except DCPFileNotFoundError:
        return Response(status=requests.codes.not_found)
    file_fqids = [x.fqid for x in files]
    bundles = BundleFileLink.select_links_for_file_fqids(file_fqids)
    return {"file_uuid": file_uuid, "bundle_fqids": [x[0] for x in bundles]}, requests.codes.ok
