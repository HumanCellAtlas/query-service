import json

from .s3_client import S3Client


class Extractor:

    def extract(self, key: str):
        raise NotImplementedError()

    @staticmethod
    def _deserialize(serialized_json: str):
        return json.loads(serialized_json)


class S3Extractor(Extractor):

    def __init__(self, region, bucket):
        self.s3_client = S3Client(region, bucket)

    def extract(self, key: str):
        raw_str = self.s3_client.get(key)
        return self._deserialize(raw_str)
