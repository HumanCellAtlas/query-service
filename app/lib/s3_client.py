import boto3


class S3Client:
    def __init__(self, region, bucket):
        self.region = region
        self.bucket = bucket
        self.s3 = boto3.resource('s3')

    def get(self, s3_object_key):
        obj = self.s3.Object(self.bucket, s3_object_key)
        return obj.get()['Body'].read().decode("utf-8")
