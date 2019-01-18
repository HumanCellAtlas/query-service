import unittest

import boto3
from moto import mock_s3

from lib.config import Config


class QueryTestCaseUsingMockAWS(unittest.TestCase):

    def setUp(self):
        # Setup mock AWS
        self.s3_mock = mock_s3()
        self.s3_mock.start()
        conn = boto3.resource('s3', region_name='us-east-1')
        conn.create_bucket(Bucket=f'query-service-{Config.account_id}')

    def tearDown(self):
        self.s3_mock.stop()