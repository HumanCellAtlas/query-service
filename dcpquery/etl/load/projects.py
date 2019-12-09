import logging

from dcpquery import config
from dcpquery.db.models.project import Project, ProjectContributorJoinTable, ProjectFunderJoinTable, \
    ProjectPublicationJoinTable, ProjectAccessionJoinTable, ProjectLinkJoinTable
from dcpquery.etl.load.utils import check_data
from dcpquery.etl.load.modules import create_funder, get_or_create_contributor, get_or_create_publication, \
    get_or_create_url_link, \
    get_or_create_accession

logger = logging.getLogger(__name__)


@check_data
def get_or_create_project(data):
    logger.info(f"Create Project: {data.get('project_core', {}).get('project_short_name')}")
    funder_objects = []
    contributor_objects = []
    publication_objects = []
    link_objects = []
    accession_objects = []
    uuid = data.get('provenance', {}).get('document_id')
    body = data
    title = data.get('project_core', {}).get("project_title")
    short_name = data.get("project_core", {}).get("project_short_name")
    description = data.get("project_core", {}).get("project_description")
    funder_list = data.get('funders', [])
    contributor_list = data.get('contributors', [])
    publication_list = data.get("publications", [])
    supplementary_links_list = data.get("supplementary_links", [])
    geo_series_accession_list = data.get("geo_series_accessions", [])
    insdc_study_accession_list = data.get("insdc_study_accessions", [])
    insdc_project_accession_list = data.get("insdc_project_accessions", [])
    for publication in publication_list:
        publication_objects.append(get_or_create_publication(publication))
    for funder in funder_list:
        funder_objects.append(create_funder(funder))
    for contributor in contributor_list:
        contributor_objects.append(get_or_create_contributor(contributor))
    for link in supplementary_links_list:
        link_objects.append(get_or_create_url_link(link))
    for accession in geo_series_accession_list:
        accession_objects.append(get_or_create_accession(accession, "GEO_SERIES"))
    for accession in insdc_study_accession_list:
        accession_objects.append(get_or_create_accession(accession, "INSDC_STUDY"))
    for accession in insdc_project_accession_list:
        accession_objects.append(get_or_create_accession(accession, "INSDC_PROJECT"))
    project = Project.get_or_create(uuid=uuid, short_name=short_name, title=title, description=description, body=body)
    for funder in funder_objects:
        create_project_funder_link(project, funder)

    for contributor in contributor_objects:
        create_project_contributor_link(project, contributor)

    for publication in publication_objects:
        create_project_publication_list(project, publication)

    for accession in accession_objects:
        create_project_accession_link(project, accession)

    for link in link_objects:
        create_project_url_link(project, link)
    return project


def create_project_funder_link(project, funder):
    config.db_session.add(ProjectFunderJoinTable(project=project, funder=funder))


def create_project_contributor_link(project, contributor):
    config.db_session.add(ProjectContributorJoinTable(project=project, contributor=contributor))


def create_project_publication_list(project, publication):
    config.db_session.add(ProjectPublicationJoinTable(project_uuid=project.uuid, publication=publication))


def create_project_accession_link(project, accession):
    config.db_session.add(ProjectAccessionJoinTable(project_uuid=project.uuid, accession=accession))


def create_project_url_link(project, link):
    config.db_session.add(ProjectLinkJoinTable(project, link))
