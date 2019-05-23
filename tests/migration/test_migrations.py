import os, sys, glob, re, subprocess, unittest

from dcpquery import config


# Note: these tests alter global state and so may not play well with other concurrent tests/operations
# this test should never be run on the prod db
class TestAllMigrations(unittest.TestCase):
    def setUp(self):
        self.latest_rev = config.db_session.execute("SELECT * FROM alembic_version;").fetchall()[0][0]
        self.rev_links = self.get_revisions()
        self.ordered_revisions = []

    @classmethod
    def get_revisions(cls):
        rev_links = {}
        for fn in glob.glob(
                os.path.join(os.path.dirname(__file__), "../../dcpquery/alembic/versions/????????????_*.py")):
            with open(fn) as fh:
                for line in fh:
                    rev_re = re.match("revision = (.+)", line)
                    if rev_re:
                        revision = rev_re.group(1).strip("'")
                    downrev_re = re.match("down_revision = (.+)", line)
                    if downrev_re:
                        down_revision = downrev_re.group(1).strip("'")
                rev_links[revision] = down_revision
        return rev_links

    def test_migrations(self):
        # downgrade migrations in order (backwards)
        path = os.path.join(os.path.dirname(__file__), "../..")
        rev = self.latest_rev

        while rev in self.rev_links:
            self.ordered_revisions.insert(0, rev)
            subprocess.run(['alembic', 'downgrade', rev],
                           cwd=path)
            rev = self.rev_links[rev]

        # upgrade migrations in order
        for rev in self.ordered_revisions:
            subprocess.run(['alembic', 'upgrade', rev],
                           cwd=path)

        # test test that current latest migrations matches starting latest migration
        latest_migration = config.db_session.execute("SELECT * FROM alembic_version;").fetchall()[0][0]
        self.assertEqual(latest_migration, self.latest_rev)
