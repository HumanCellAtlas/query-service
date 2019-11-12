import unittest

from dcpquery import config
from dcpquery.db.models import Project, ProjectFileLink, File


class TestProjects(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock_project_fqid = 'DDDDDDDD-5c98-4d26-a614-246d12c2e5d7.2019-05-15T183023.365000Z'
        cls.mock_project_fqid_1 = 'EEEEEEEE-5c98-4d26-a614-246d12c2e5d7.2019-05-15T183023.365000Z'
        project = Project(fqid=cls.mock_project_fqid)
        project_1 = Project(fqid=cls.mock_project_fqid_1)
        config.db_session.add_all([project, project_1])
        config.db_session.commit()

    def test_insert_select_project(self):
        project_fqid = 'DEDEDEDE-5c98-4d26-a614-246d12c2e5d7.2019-05-15T183023.365000Z'
        # check none
        res = Project.select_one(project_fqid)
        self.assertIsNone(res)

        project = Project(fqid=project_fqid)
        config.db_session.add(project)
        config.db_session.commit()

        # check exists
        res = Project.select_one(project_fqid)
        self.assertIsNotNone(res)

    def test_delete_many(self):
        # check both projects are there
        res = config.db_session.query(Project).filter(
            Project.fqid.in_((self.mock_project_fqid, self.mock_project_fqid_1))).all()
        result = list(res)
        self.assertEqual(len(result), 2)
        # delete
        Project.delete_many([self.mock_project_fqid, self.mock_project_fqid_1])
        config.db_session.flush()
        # check they are gone
        res = config.db_session.query(Project).filter(
            Project.fqid.in_((self.mock_project_fqid, self.mock_project_fqid_1))).all()
        result = list(res)
        self.assertEqual(len(result), 0)


class TestProjectFileLinks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # create and add project file links
        cls.mock_project_fqid_0 = 'CCCCCCCC-5c98-4d26-a614-246d12c2e5d7.2019-05-15T183023.365000Z'
        cls.mock_project_fqid_1 = 'FFFFFFFF-5c98-4d26-a614-246d12c2e5d7.2019-05-15T183023.365000Z'
        cls.mock_file_fqid = 'AAAAAAAA-5c98-4d26-a614-246d12c2e5d7.2019-05-15T183023.365000Z'
        cls.mock_file_fqid_1 = 'BBBBBBBB-5c98-4d26-a614-246d12c2e5d7.2019-05-15T183023.365000Z'

        project = Project(fqid=cls.mock_project_fqid_0)
        project1 = Project(fqid=cls.mock_project_fqid_1)
        file = File(fqid=cls.mock_file_fqid)
        file1 = File(fqid=cls.mock_file_fqid_1)
        project_file_link = ProjectFileLink(project=project, file=file)
        project_file_link_1 = ProjectFileLink(project=project, file=file1)
        project_file_link_2 = ProjectFileLink(project=project1, file=file)
        project_file_link_3 = ProjectFileLink(project=project1, file=file1)

        config.db_session.add_all([project_file_link, project_file_link_1, project_file_link_2, project_file_link_3])
        config.db_session.commit()

    def test_insert_select_project_file_links(self):
        mock_project_fqid = 'ABCDABCD-5c98-4d26-a614-246d12c2e5d7.2019-05-15T183023.365000Z'
        mock_file_fqid = 'DCBADCBA-5c98-4d26-a614-246d12c2e5d7.2019-05-15T183023.365000Z'

        # check none
        res = config.db_session.query(ProjectFileLink).filter(
            ProjectFileLink.project_fqid == mock_project_fqid).all()
        result = list(res)
        self.assertEqual(len(result), 0)

        # create
        project = Project(fqid=mock_project_fqid)
        file = File(fqid=mock_file_fqid)
        project_file_link = ProjectFileLink(project=project, file=file)
        config.db_session.add(project_file_link)
        config.db_session.commit()

        # check exists and references correct file
        res = config.db_session.query(ProjectFileLink).filter(
            ProjectFileLink.project_fqid == mock_project_fqid).all()
        result = list(res)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].file_fqid, mock_file_fqid)

    def test_select_links_for_file_fqids(self):
        links = ProjectFileLink.select_links_for_file_fqids([self.mock_file_fqid_1, self.mock_file_fqid]).fetchall()
        self.assertEqual(len(links), 4)

        # check that the first item in the returned row is the project_fqid
        self.assertIn(links[0][0], [self.mock_project_fqid_0, self.mock_project_fqid_1])

    def test_delete_links_for_files(self):
        # create links for deletion
        mock_file_fqid = 'AAAAAAAA-DDDD-4d26-a614-246d12c2e5d7.2019-05-15T183023.365000Z'
        mock_file_fqid_1 = 'BBBBBBBB-DDDD-4d26-a614-246d12c2e5d7.2019-05-15T183023.365000Z'

        project = Project(fqid=self.mock_project_fqid_1)
        file = File(fqid=mock_file_fqid)
        file1 = File(fqid=mock_file_fqid_1)
        project_file_link = ProjectFileLink(project=project, file=file)
        project_file_link_1 = ProjectFileLink(project=project, file=file1)
        config.db_session.add_all([project_file_link, project_file_link_1])
        config.db_session.commit()

        # check project file links exist
        links = ProjectFileLink.select_links_for_file_fqids([mock_file_fqid_1, mock_file_fqid]).fetchall()
        self.assertEqual(len(links), 2)

        # delete links
        ProjectFileLink.delete_links_for_files([mock_file_fqid, mock_file_fqid_1])
        config.db_session.flush()

        # check project file links dont exist
        links = ProjectFileLink.select_links_for_file_fqids([mock_file_fqid_1, mock_file_fqid]).fetchall()
        self.assertEqual(len(links), 0)

    def test_select_links_for_project_fqids(self):
        links = ProjectFileLink.select_links_for_project_fqids(
            [self.mock_project_fqid_0, self.mock_project_fqid_1])
        self.assertEqual(len(links), 4)

        for link in links:
            self.assertIn(link[0], [self.mock_project_fqid_0, self.mock_project_fqid_1])
            self.assertIn(link[1], [self.mock_file_fqid, self.mock_file_fqid_1])


if __name__ == '__main__':
    unittest.main()
