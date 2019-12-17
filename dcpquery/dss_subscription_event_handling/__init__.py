from dcpquery import config
from dcpquery.db.models import Bundle, BundleFileLink, File, ProjectFileLink, Project
from dcpquery.etl import logger


def drop_one_bundle(bundle_uuid, bundle_version):
    bundle_fqid = bundle_uuid + '.' + bundle_version
    delete_files_and_bundle_file_links_for_bundle_deletion(bundle_fqid)
    Bundle.delete_bundles([bundle_fqid])
    config.db_session.commit()


def delete_files_and_bundle_file_links_for_bundle_deletion(bundle_fqid):
    # get all files associated with that bundle
    file_fqids = [link[1] for link in BundleFileLink.select_links_for_bundle_fqids([bundle_fqid])]

    # delete all bundle file links for the bundle
    BundleFileLink.delete_links_for_bundles([bundle_fqid])

    # find which files are connected to a different bundle --  link[0] is the bundle_fqid, link[1] is the file_fqid
    files_to_keep = [link[1] for link in BundleFileLink.select_links_for_file_fqids(file_fqids)]
    files_to_delete = list(set(file_fqids) - set(files_to_keep))
    delete_projects_and_project_file_links_for_file_deletion(files_to_delete)

    # delete files not connected to any bundles
    File.delete_files(files_to_delete)
    # TODO @madison once processes link to file versions cascade file deletions to associated processes


def delete_projects_and_project_file_links_for_file_deletion(file_fqids):
    # get all projects associated with files marked for deletion link[0] is project_fqid, link[1] is file_fqid
    project_fqids = [link[0] for link in ProjectFileLink.select_links_for_file_fqids(file_fqids)]

    # delete file specific project file links
    ProjectFileLink.delete_links_for_files(file_fqids)
    config.db_session.flush()
    # find which projects are still connected to remaining files
    projects_to_keep = [link[0] for link in ProjectFileLink.select_links_for_project_fqids(project_fqids)]
    projects_to_delete = list(set(project_fqids) - set(projects_to_keep))
    Project.delete_many(projects_to_delete)


def process_bundle_event(dss_event):
    config.readonly_db = False
    config.reset_db_session()
    logger.info(f"Processing DSS event: {dss_event}")
    if dss_event["event_type"] == "CREATE":
        logger.info(f"Processing DSS CREATE event: {dss_event}")
        # etl_one_bundle(**dss_event["match"])
    elif dss_event["event_type"] in {"TOMBSTONE", "DELETE"}:
        logger.info(f"Processing DSS DELETE or TOMBSTONE event: {dss_event}")
        drop_one_bundle(**dss_event["match"])
    else:
        logger.error("Ignoring unknown event type %s", dss_event["event_type"])
