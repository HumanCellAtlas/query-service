import logging

from dcpquery import config
from dcpquery.db.models.project import Project, ProjectContributorJoinTable, ProjectFunderJoinTable, \
    ProjectPublicationJoinTable, ProjectAccessionJoinTable, ProjectLinkJoinTable
from dcpquery.etl.load.modules import create_funder, get_or_create_contributor, get_or_create_publication, get_or_create_url_link, \
    get_or_create_accession
logger = logging.getLogger(__name__)


def create_project(project_data):
    logger.info(f"Create Project: {project_data['project_core']['project_short_name']}")
    funder_objects = []
    contributor_objects = []
    publication_objects = []
    link_objects = []
    accession_objects = []
    uuid = project_data.get('provenance', {}).get('document_id')
    body = project_data
    title = project_data.get('project_core', {}).get("project_title")
    short_name = project_data.get("project_core", {}).get("project_short_name")
    description = project_data.get("project_core", {}).get("project_description")
    funder_list = project_data.get('funders')
    contributor_list = project_data.get('contributors')
    publication_list = project_data.get("publications")
    supplementary_links_list = project_data.get("supplementary_links")
    geo_series_accession_list = project_data.get("geo_series_accessions")
    insdc_study_accession_list = project_data.get("insdc_study_accessions")
    insdc_project_accession_list = project_data.get("insdc_project_accessions")
    for publication in publication_list:
        publication_objects.append(get_or_create_publication(publication))
    for funder in funder_list:
        funder_objects.append(create_funder(funder))
    for contributor in contributor_list:
        contributor_objects.append(get_or_create_contributor(contributor))
    for link in supplementary_links_list:
        link_objects.append(get_or_create_url_link(link))
    for accession in geo_series_accession_list:
        accession_objects.append(get_or_create_accession(accession, "geo_series"))
    for accession in insdc_study_accession_list:
        accession_objects.append(get_or_create_accession(accession, "insdc_study"))
    for accession in insdc_project_accession_list:
        accession_objects.append(get_or_create_accession(accession, "insdc_project"))
    project = Project(uuid=uuid, short_name=short_name, title=title, description=description, body=body)
    config.db_session.add(project)
    config.db_session.add_all(funder_objects, contributor_objects, publication_objects, link_objects)
    for funder in funder_objects:
        config.db_session.add(create_project_funder_link(project, funder))

    for contributor in contributor_objects:
        create_project_contributor_link(project, contributor)

    for publication in publication_objects:
        create_project_publication_list(project, publication)

    for accession in accession_objects:
        create_project_accession_link(project, accession)

    for link in link_objects:
        create_project_url_link(project, link)


def create_project_funder_link(project, funder):
    config.db_session.add(ProjectFunderJoinTable(project=project, funder=funder))


def create_project_contributor_link(project, contributor):
    config.db_session.add(ProjectContributorJoinTable(project=project, contributor=contributor))


def create_project_publication_list(project, publication):
    config.db_session.add(ProjectPublicationJoinTable(project, publication))


def create_project_accession_link(project, accession):
    config.db_session.add(ProjectAccessionJoinTable(project, accession))


def create_project_url_link(project, link):
    config.db_session.add(ProjectLinkJoinTable(project, link))

