import unittest

from mock import patch

from db_cleanup_lambda.app import handler
from lib.config import Config
from lib.db.database import PostgresDatabase


class TestDBCleanup(unittest.TestCase):

    @patch('query.lib.db.database.JobStatus')
    def test_db_cleanup_calls_correct_function(self, mock_job_status):
        handler({"mock": "event"}, "mock_context")
        assert mock_job_status.delete_old_rows.called_once()

    def test_db_contains_no_job_status_rows_older_than_90_days(self):
        db = PostgresDatabase(Config.serve_database_uri)
        with db.transaction() as (_, tables):
            tables.job_status._cursor.execute(
                "SELECT count(*) FROM job_status WHERE created_at < NOW() - INTERVAL '91 days'"
            )
            count = tables.job_status._cursor.fetchall()
            assert count[0][0] == 0
