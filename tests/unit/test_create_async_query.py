import os, sys, unittest
from unittest.mock import patch


@unittest.skip("WIP")
class TestCreateAsyncQuery(unittest.TestCase):
    uuid = '26f0424a-fdce-455f-ac2e-f8f5619c6eda'
    query = "SELECT * FROM files limit 10;"
    mock_event = {'Records': [{
        'messageId': 'AAAAA',
        'receiptHandle': 'AAAAA',
        'body': '{"query": "SELECT * FROM files limit 10;",'
                ' "job_id": "26f0424a-fdce-455f-ac2e-f8f5619c6eda"}',
        'attributes': {'ApproximateReceiveCount': '1',
                       'SentTimestamp': '1547593710857',
                       'SenderId': 'AROAIW2TZ546I:query-api-dev',
                       'ApproximateFirstReceiveTimestamp': '154'},
        'messageAttributes': {}, 'md5OfBody': '9014201ab8d59dfd',
        'eventSource': 'aws:sqs',
        'eventSourceARN': 'arn:***',
        'awsRegion': 'us-east-1'}]}

    @patch('query.lib.db.database.JobStatus')
    def test_process_async_query_keeps_job_status_updated(self, mock_job_status):
        mock_job_status().update_job_status.return_value = None
        # process_async_query(TestCreateAsyncQuery.uuid, TestCreateAsyncQuery.query)

        self.assertEqual(mock_job_status().update_job_status.call_count, 2)

    @patch('async_query_lambda.app.process_async_query')
    def test_create_async_query_calls_process_async_func_with_correct_args(self, mock_process):
        # handler(self.mock_event, 'context')
        assert mock_process.called_once_with(TestCreateAsyncQuery.uuid, TestCreateAsyncQuery.query)
