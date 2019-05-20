import os, sys, unittest

from unittest.mock import patch

from dcpquery import config
from dcpquery.api.query_job import create_async_query_job
from dcpquery.api.query_jobs import process_async_query


class TestCreateAsyncQuery(unittest.TestCase):
    uuid = '26f0424a-fdce-455f-ac2e-f8f5619c6eda'
    query = "SELECT * FROM files limit 10;"
    mock_event_record = {'messageId': '26f0424a-fdce-455f-ac2e-f8f5619c6eda',
                         'receiptHandle': 'AAAAA',
                         'body': '"SELECT * FROM files limit 10;"',
                         'attributes': {'ApproximateReceiveCount': '1',
                                        'SentTimestamp': '1547593710857',
                                        'SenderId': 'AROAIW2TZ546I:query-api-dev',
                                        'ApproximateFirstReceiveTimestamp': '154'},
                         'messageAttributes': {},
                         'md5OfBody': '0',
                         'eventSource': 'aws:sqs',
                         'eventSourceARN': 'arn:***',
                         'awsRegion': 'us-east-1'}

    @patch("dcpquery.api.query_jobs.set_job_status")
    def test_process_async_query_keeps_job_status_updated(self, set_job_status):
        job_id = self.mock_event_record["messageId"]
        process_async_query(self.mock_event_record)
        set_job_status.assert_called_with(
            job_id,
            result_location={'Bucket': config.s3_bucket_name, 'Key': f'job_result/{job_id}'},
            status="done"
        )

    @patch("dcpquery.api.query_job.set_job_status")
    @patch("dcpquery.api.query_job.aws.resources.sqs.Queue")
    def test_create_async_query_calls_process_async_func_with_correct_args(self, sqs, set_job_status):
        create_async_query_job(self.mock_event_record["body"])
        set_job_status.assert_called()
        sqs.assert_called()


if __name__ == '__main__':
    unittest.main()
