import boto3
from retrying import retry


class S3Client:
    def __init__(self, region, bucket):
        self.region = region
        self.bucket = bucket
        self.s3 = boto3.resource('s3')

    @retry(wait_fixed=1000, stop_max_attempt_number=3)
    def get(self, s3_object_key):
        obj = self.s3.Object(self.bucket, s3_object_key)
        return obj.get()['Body'].read().decode("utf-8")