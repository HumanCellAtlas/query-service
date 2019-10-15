import os, sys, json, unittest, io, uuid, datetime

import requests
from requests.models import Response

import dcpquery, dcplib.etl
from dcpquery.dss_subscription_event_handling import process_bundle_event

files = [
    {
        "name": hex(i),
        "content-type": "application/json",
        "uuid": str(uuid.uuid4()),
        "version": datetime.datetime.now().isoformat(),
        "sha256": "0",
        "size": 8
    }
    for i in range(256)
]


class MockHTTPClient:
    status_code = requests.codes.ok

    def get(self, url, params):
        if "files" in url:
            payload = {}
        else:
            payload = {"bundle": {"files": files}}
        res = Response()
        res.status_code = self.status_code
        res.raw = io.BytesIO(json.dumps(payload).encode())
        return res


class MockDSSClient(MockHTTPClient):
    host = "localhost"

    class MockDSSMethod:
        def __call__(self, es_query, replica):
            return {"total_hits": 1}

        def iterate(self, es_query, replica, per_page):
            for i in range(4):
                yield {"bundle_fqid": "a%d.b" % i}

        def paginate(self, es_query, replica, per_page):
            for i in range(4):
                yield {"results": [{"bundle_fqid": "a%d.b" % i}]}

    post_search = MockDSSMethod()

    def __init__(self, swagger_url="swagger_url"):
        self.swagger_url = swagger_url


class TestExtractor(unittest.TestCase):
    def setUp(self):
        dcpquery.config._dss_client = MockDSSClient()
        self.HTTPRequest = dcplib.etl.HTTPRequest
        dcplib.etl.HTTPRequest = MockHTTPClient

    def tearDown(self):
        dcpquery.config._dss_client = None
        dcplib.etl.HTTPRequest = self.HTTPRequest

    def test_bundle_event_handling(self):
        with open(f'{os.path.dirname(__file__)}/../fixtures/mock_sqs_bundle_create_event.json', 'r') as fh:
            process_bundle_event(json.loads(json.load(fh)["Records"][0]["body"]))

        with open(f'{os.path.dirname(__file__)}/../fixtures/mock_sqs_bundle_delete_event.json', 'r') as fh:
            process_bundle_event(json.loads(json.load(fh)["Records"][0]["body"]))


if __name__ == '__main__':
    unittest.main()
