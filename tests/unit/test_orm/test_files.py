import unittest

from dcpquery import config
from dcpquery.db.models import File, BundleFileLink
from dcpquery.exceptions import DCPFileNotFoundError
from tests import vx_bf_links


class TestFiles(unittest.TestCase):
    project_file = next(l.file for l in vx_bf_links if l.name == 'project_0.json')
    process_file = next(l.file for l in vx_bf_links if l.name == 'process_0.json')

    def test_select_file(self):
        result = File.select_file(file_fqid=self.project_file.fqid)

        self.assertEqual(result.uuid, self.project_file.uuid)
        self.assertEqual(result.version, self.project_file.version)
        expect_version = self.project_file.version.strftime("%Y-%m-%dT%H%M%S.%fZ")
        self.assertEqual(result.fqid, f"{self.project_file.uuid}.{expect_version}")
        self.assertEqual(result.body, self.project_file.body)

    def test_delete_files(self):
        file_fqids = [file[0] for file in config.db_session.query("fqid FROM files LIMIT 3;").all()]
        # Need to delete bundle_file_links with fk to file prior to deleting the file
        BundleFileLink.delete_links_for_files(file_fqids)

        File.delete_files(file_fqids)

        for file_fqid in file_fqids:
            self.assertEqual(File.select_file(file_fqid=file_fqid), None)

    def test_select_files_for_uuid(self):
        file_uuid = config.db_session.execute("SELECT uuid from files_all_versions limit 1;").fetchall()[0][0]
        expected_files = config.db_session.execute("SELECT * FROM files_all_versions where uuid = :file_uuid",
                                                   {"file_uuid": file_uuid}).fetchall()
        files = File.select_files_for_uuid(str(file_uuid))
        self.assertEqual(len(expected_files), len(files))

        # check fqids match
        self.assertEqual(sorted([x[0] for x in expected_files]), sorted([x.fqid for x in files]))

    def test_select_files_for_non_existent_uuid(self):
        file_uuid = 'AAAAAAAA-AAAA-AAAA-AAAA-AAAAAAAAAAAA'
        with self.assertRaises(DCPFileNotFoundError):
            File.select_files_for_uuid(file_uuid)


if __name__ == '__main__':
    unittest.main()
