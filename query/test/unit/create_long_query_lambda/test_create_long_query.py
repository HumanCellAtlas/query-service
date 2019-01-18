from unittest.mock import patch

from create_long_query_lambda.app import create_long_query
from lambdas.long_query.create_long_query import query_db_and_put_results_in_s3
from test.unit import QueryTestCaseUsingMockAWS


class TestCreateLongQuery(QueryTestCaseUsingMockAWS):
    def setUp(self):
        super().setUp()
        self.uuid = '26f0424a-fdce-455f-ac2e-f8f5619c6eda'
        self.query = "SELECT * FROM files limit 10;"
        self.mock_event = {'Records': [{'messageId': 'AAAAA',
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
    @patch('query.lambdas.long_query.create_long_query.Config')
    def test_create_long_query_keeps_job_status_updated(self, mock_config, mock_job_status):
        mock_job_status().update_job_status.return_value = None
        mock_config.configure_mock(account_id='123')
        query_db_and_put_results_in_s3(self.uuid, self.query)
        self.assertEqual(mock_job_status().update_job_status.call_count, 2)

    @patch('create_long_query_lambda.app.query_db_and_put_results_in_s3')
    def test_create_long_query_calls_query_db_and_etc_with_correct_args(self, mock_query_db):
        create_long_query(self.mock_event, 'context')
        assert mock_query_db.called_once_with(self.uuid, self.query)

    def tearDown(self):
        super().tearDown()
