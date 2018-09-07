import os
import sys
import unittest
import uuid

pkg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))  # noqa
sys.path.insert(0, pkg_root)  # noqa

import boto3
from lib.s3_client import S3Client


class TestS3Client(unittest.TestCase):

    sts = boto3.client("sts")
    account_id = sts.get_caller_identity()["Account"]
    region = "us-east-1"
    bucket = "query-service-test-{0}".format(account_id)
    s3_client = S3Client(region, bucket)
    s3 = s3_client.s3

    def setUp(self):
        self.s3_object_key = "test/data/" + str(uuid.uuid4())
        self.s3.Bucket(self.bucket)\
            .put_object(Key=self.s3_object_key, Body=bytes("hello", "utf-8"))

    def tearDown(self):
        obj = self.s3.Object(self.bucket, self.s3_object_key)
        obj.delete()

    def test_s3_client(self):
        raw_str = self.s3_client.get(self.s3_object_key)
        self.assertEqual(raw_str, "hello")
