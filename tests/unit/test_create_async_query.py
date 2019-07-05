import os, sys, json, unittest

from unittest.mock import patch

from dcpquery import config
from dcpquery.api.query_job import create_async_query_job
from dcpquery.api.query_jobs import process_async_query


class TestCreateAsyncQuery(unittest.TestCase):
    job_id = '26f0424a-fdce-455f-ac2e-f8f5619c6eda'
    query = "SELECT * FROM files limit %(l)s;"
    params = {"l": 10}
    mock_event_record = {'messageId': job_id,
                         'receiptHandle': 'AAAAA',
                         'body': json.dumps(dict(query=query, params=params)),
                         'attributes': {'ApproximateReceiveCount': '1',
                                        'SentTimestamp': '1547593710857',
                                        'SenderId': 'AROAIW2TZ546I:query-api-dev',
                                        'ApproximateFirstReceiveTimestamp': '154'},
                         'messageAttributes': {},
                         'md5OfBody': '0',
                         'eventSource': 'aws:sqs',
                         'eventSourceARN': 'arn:***',
                         'awsRegion': 'us-east-1'}
#
#    def setUp(self):
#        config.reset_db_session()
#
#    def tearDown(self):
#        config.reset_db_session()

    @patch("dcpquery.api.query_jobs.set_job_status")
    def test_process_async_query_keeps_job_status_updated(self, set_job_status):
        config.db_statement_timeout_seconds = 880
        process_async_query(self.mock_event_record)
        set_job_status.assert_called_with(
            self.job_id,
            result_location={'Bucket': config.s3_bucket_name, 'Key': f'job_result/{self.job_id}'},
            status="done"
        )

    @patch("dcpquery.api.query_jobs.set_job_status")
    def test_process_async_query_with_invalid_query(self, set_job_status):
        config.db_statement_timeout_seconds = 880
        body = json.dumps(dict(query="SELECT * FROM NONEXISTENT_TABLE", params={}))
        process_async_query(dict(self.mock_event_record, body=body))
        set_job_status_args = set_job_status.call_args
        self.assertEqual(set_job_status_args[0][0], self.job_id)
        self.assertEqual(set_job_status_args[1]["status"], "failed")

    @patch("dcpquery.api.query_job.set_job_status")
    @patch("dcpquery.api.query_job.aws.resources.sqs.Queue")
    def test_create_async_query_calls_process_async_func_with_correct_args(self, sqs, set_job_status):
        create_async_query_job(**json.loads(self.mock_event_record["body"]))
        set_job_status.assert_called()
        sqs.assert_called()


if __name__ == '__main__':
    unittest.main()
