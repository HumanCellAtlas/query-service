import unittest

import boto3
from moto import mock_s3

from query.lib.config import Config


class QueryTestCaseUsingMockAWS(unittest.TestCase):

    def setUp(self):
        # Setup mock AWS
        self.s3_mock = mock_s3()
        self.s3_mock.start()
        self.conn = boto3.resource('s3', region_name='us-east-1')
        self.conn.create_bucket(Bucket=Config.query_service_bucket)

    def tearDown(self):
        self.s3_mock.stop()
