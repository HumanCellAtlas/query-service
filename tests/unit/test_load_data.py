#!/usr/bin/env python

import json, io, unittest, logging, uuid, datetime
from unittest.mock import Mock, patch

from requests.models import Response
import dcplib.etl

import dcpquery.etl


class MockDSSClient:
    host = "localhost"
    swagger_url = "swagger_url"
    files = [
        {"name": hex(i), "content-type": 'application/json; dcp-type="metadata/test"', "uuid": str(uuid.uuid4()),
         "version": str(datetime.datetime.utcnow()), "sha256": "0", "size": 2}
        for i in range(256)
    ]

    class MockDSSMethod:
        def __call__(self, es_query, replica):
            return {"total_hits": 1}

        def iterate(self, es_query, replica, per_page):
            for i in range(4):
                yield {"bundle_fqid": "a%d.b" % i}

    post_search = MockDSSMethod()

    def __init__(self, *args, **kwargs):
        pass

    def get(self, url, params):
        if "files" in url:
            payload = {}
        else:
            payload = {"bundle": {"files": self.files}}
        res = Response()
        res.status_code = 200
        res.raw = io.BytesIO(json.dumps(payload).encode())
        return res


class TestLoadData(unittest.TestCase):
    def test_etl_one_bundle(self):
        dcpquery.etl.DSSClient = MockDSSClient
        dcplib.etl.http = MockDSSClient()
        dcpquery.etl.etl_one_bundle(bundle_uuid="9a5cbcbd-866c-4b6a-9fdb-6581a2d47f3c",
                                    bundle_version="2018-11-27T211302.714868Z")

    @unittest.skip("WIP")
    @patch('load_data_lambda.app.extract_transform_load')
    @patch('load_data_lambda.app.extractor', 'foo')
    @patch('load_data_lambda.app.loader', 'bah')
    def test_query_service_load_data(self, mock_etl):

        '''
        mock_event_data = {"Records": [{'messageId': '33b4de0b-274a-48f0-9b5c-ee600b439c6c',
                                        'receiptHandle': 'AQEBm6V306aUkJhPlCT2hcBz9Q1QXmNmqPV4UC/ebmGQYAMLKQoHxn2k',
                                        'body': '{"bundle_uuid": "9a5cbcbd-866c-4b6a-9fdb-6581a2d47f3c", '
                                                '"bundle_version": "2018-11-27T211302.714868Z"}',
                                        'attributes': {'ApproximateReceiveCount': '1',
                                                       'SentTimestamp': '1543357453729',
                                                       'SenderId': 'AROAIW2WQHOU5B2TZ546I:query-api-dev',
                                                       'ApproximateFirstReceiveTimestamp': '1543357453745'},
                                        'messageAttributes': {}, 'md5OfBody': '4bcabebd5f583eb0b964841edbf3a3ca',
                                        'eventSource': 'aws:sqs',
                                        'eventSourceARN': 'arn:aws:sqs:us-east-1:*:dcp-query-data-input-queue-',
                                        'awsRegion': 'us-east-1'}]}
        '''
        # load_data(mock_event_data, 'context')
        mock_etl.assert_called_once_with(
            extractor='foo',
            loader='bah',
            bundle_uuid='9a5cbcbd-866c-4b6a-9fdb-6581a2d47f3c',
            bundle_version='2018-11-27T211302.714868Z'
        )

    @unittest.skip("WIP")
    @patch('query.lambdas.load_data.load_data.BundleDocumentTransform.transform')
    def test_extract_transform_load(self, mock_transform):
        mock_transform.return_value = 'TRANSFORMED BUNDLE'
        extractor = Mock()
        loader = Mock()
        extractor.extract_bundle.return_value = 'BUNDLE'
        # extract_transform_load(extractor, loader, 'UUID', 'VERSION')
        extractor.extract_bundle.assert_called_once_with('UUID', 'VERSION')
        mock_transform.assert_called_once_with('BUNDLE')
        loader.load.assert_called_once_with('BUNDLE', 'TRANSFORMED BUNDLE')


if __name__ == '__main__':
    unittest.main()
